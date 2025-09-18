/**
 * Dashboard service for fetching real-time data
 */

import { apiClient } from '@/services/api';

export interface DashboardKPIs {
  total_clients: number;
  monthly_revenue: number;
  scheduled_services: number;
  inventory_items: number;
  low_stock_items: number;
  out_of_stock_items: number;
  pending_orders: number;
  active_staff: number;
  completion_rate: number;
  todays_jobs: number;
}

export interface RevenueTrend {
  name: string;
  value: number;
  date: string;
}

export interface ServiceDistribution {
  name: string;
  value: number;
  percentage: number;
}

export interface TeamProductivity {
  name: string;
  value: number;
  efficiency: number;
}

export interface RecentActivity {
  id: number;
  action: string;
  client: string;
  time: string;
  type: 'client' | 'service' | 'payment' | 'maintenance';
  status?: string;
}

export interface StockAlert {
  product_id: number;
  product_name: string;
  product_sku: string;
  current_stock: number;
  min_stock_level: number;
  alert_type: 'low_stock' | 'out_of_stock';
  days_until_stockout: number;
  suggested_order_quantity: number;
}

class DashboardService {
  async getKPIs(): Promise<DashboardKPIs> {
    try {
      // Get inventory summary
      const inventoryResponse = await apiClient.get('/inventory/dashboard/summary/');
      const inventoryData = inventoryResponse.data;

      // Get real data from other APIs
      const [clientsResponse, financeResponse, hrResponse] = await Promise.all([
        apiClient.get('/sales/clients/'),
        apiClient.get('/finance/invoices/'),
        apiClient.get('/hr/employees/')
      ]);

      const clientsData = clientsResponse.data;
      const financeData = financeResponse.data;
      const hrData = hrResponse.data;

      // Calculate real KPIs from API data
      const totalClients = clientsData.count || 0;
      const monthlyRevenue = financeData.results?.reduce((sum: number, invoice: any) => 
        sum + (invoice.total_amount || 0), 0) || 0;
      const activeStaff = hrData.results?.filter((emp: any) => emp.is_active).length || 0;

      const realKPIs: DashboardKPIs = {
        total_clients: totalClients,
        monthly_revenue: monthlyRevenue,
        scheduled_services: 0, // TODO: Implement scheduling service
        inventory_items: inventoryData.total_products || 0,
        low_stock_items: inventoryData.low_stock_products || 0,
        out_of_stock_items: inventoryData.out_of_stock_products || 0,
        pending_orders: inventoryData.pending_orders || 0,
        active_staff: activeStaff,
        completion_rate: 0, // TODO: Calculate from service completion data
        todays_jobs: 0, // TODO: Implement today's jobs calculation
      };

      return realKPIs;
    } catch (error) {
      console.error('Error fetching KPIs:', error);
      // Return default values on error
      return {
        total_clients: 0,
        monthly_revenue: 0,
        scheduled_services: 0,
        inventory_items: 0,
        low_stock_items: 0,
        out_of_stock_items: 0,
        pending_orders: 0,
        active_staff: 0,
        completion_rate: 0,
        todays_jobs: 0,
      };
    }
  }

  async getRevenueTrend(): Promise<RevenueTrend[]> {
    try {
      // Get real revenue data from finance API
      const response = await apiClient.get('/finance/invoices/');
      const invoices = response.data.results || [];
      
      // Group invoices by month and calculate totals
      const monthlyData: { [key: string]: number } = {};
      invoices.forEach((invoice: any) => {
        if (invoice.invoice_date) {
          const month = new Date(invoice.invoice_date).toLocaleDateString('en-US', { month: 'short' });
          monthlyData[month] = (monthlyData[month] || 0) + (invoice.total_amount || 0);
        }
      });

      // Convert to array format
      const realData: RevenueTrend[] = Object.entries(monthlyData).map(([name, value]) => ({
        name,
        value,
        date: new Date().toISOString() // TODO: Use actual date
      }));

      return realData;
    } catch (error) {
      console.error('Error fetching revenue trend:', error);
      return [];
    }
  }

  async getServiceDistribution(): Promise<ServiceDistribution[]> {
    try {
      // Get real service data from invoices
      const response = await apiClient.get('/finance/invoices/');
      const invoices = response.data.results || [];
      
      // Group by service type (assuming service_type field exists)
      const serviceData: { [key: string]: number } = {};
      invoices.forEach((invoice: any) => {
        const serviceType = invoice.service_type || 'General Service';
        serviceData[serviceType] = (serviceData[serviceType] || 0) + 1;
      });

      const total = Object.values(serviceData).reduce((sum, count) => sum + count, 0);
      
      // Convert to array format with percentages
      const realData: ServiceDistribution[] = Object.entries(serviceData).map(([name, value]) => ({
        name,
        value,
        percentage: total > 0 ? Math.round((value / total) * 100) : 0
      }));

      return realData;
    } catch (error) {
      console.error('Error fetching service distribution:', error);
      return [];
    }
  }

  async getTeamProductivity(): Promise<TeamProductivity[]> {
    try {
      // Get real team data from HR API
      const response = await apiClient.get('/hr/employees/');
      const employees = response.data.results || [];
      
      // Group employees by department/team
      const teamData: { [key: string]: { count: number, totalEfficiency: number } } = {};
      employees.forEach((emp: any) => {
        const teamName = emp.department?.name || 'Unassigned';
        if (!teamData[teamName]) {
          teamData[teamName] = { count: 0, totalEfficiency: 0 };
        }
        teamData[teamName].count++;
        teamData[teamName].totalEfficiency += emp.efficiency_score || 0;
      });

      // Convert to array format
      const realData: TeamProductivity[] = Object.entries(teamData).map(([name, data]) => ({
        name,
        value: data.count,
        efficiency: data.count > 0 ? Math.round(data.totalEfficiency / data.count) : 0
      }));

      return realData;
    } catch (error) {
      console.error('Error fetching team productivity:', error);
      return [];
    }
  }

  async getRecentActivities(): Promise<RecentActivity[]> {
    try {
      // Get real activity data from multiple APIs
      const [clientsResponse, invoicesResponse, employeesResponse] = await Promise.all([
        apiClient.get('/sales/clients/'),
        apiClient.get('/finance/invoices/'),
        apiClient.get('/hr/employees/')
      ]);

      const clients = clientsResponse.data.results || [];
      const invoices = invoicesResponse.data.results || [];
      const employees = employeesResponse.data.results || [];

      const activities: RecentActivity[] = [];

      // Add recent client activities
      clients.slice(0, 2).forEach((client: any, index: number) => {
        activities.push({
          id: index + 1,
          action: "New client registration",
          client: client.name || client.company_name || 'Unknown Client',
          time: this.formatTimeAgo(client.created),
          type: "client",
          status: "completed"
        });
      });

      // Add recent invoice activities
      invoices.slice(0, 2).forEach((invoice: any, index: number) => {
        activities.push({
          id: activities.length + index + 1,
          action: invoice.status === 'paid' ? "Invoice paid" : "Invoice created",
          client: invoice.client?.name || 'Unknown Client',
          time: this.formatTimeAgo(invoice.created),
          type: "payment",
          status: invoice.status || "pending"
        });
      });

      // Sort by time (most recent first) and return top 4
      return activities
        .sort((a, b) => new Date(b.time).getTime() - new Date(a.time).getTime())
        .slice(0, 4);
    } catch (error) {
      console.error('Error fetching recent activities:', error);
      return [];
    }
  }

  private formatTimeAgo(dateString: string): string {
    if (!dateString) return 'Unknown time';
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours} hours ago`;
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`;
  }

  async getStockAlerts(): Promise<StockAlert[]> {
    try {
      const response = await apiClient.get('/inventory/dashboard/stock_alerts/');
      return response.data;
    } catch (error) {
      console.error('Error fetching stock alerts:', error);
      return [];
    }
  }

  async getInventorySummary() {
    try {
      const response = await apiClient.get('/inventory/dashboard/summary/');
      return response.data;
    } catch (error) {
      console.error('Error fetching inventory summary:', error);
      return null;
    }
  }
}

export const dashboardService = new DashboardService();
