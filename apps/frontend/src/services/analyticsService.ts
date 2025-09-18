/**
 * Analytics service for comprehensive reporting and business intelligence
 */

import { apiClient } from '@/services/api';

export interface RevenueAnalytics {
  period: string;
  total_revenue: number;
  revenue_growth: number;
  average_revenue_per_client: number;
  revenue_by_service_type: Array<{
    service_type: string;
    revenue: number;
    percentage: number;
  }>;
  monthly_revenue_trend: Array<{
    month: string;
    revenue: number;
    growth: number;
  }>;
  top_clients: Array<{
    client_id: number;
    client_name: string;
    revenue: number;
    service_count: number;
  }>;
}

export interface ClientAnalytics {
  total_clients: number;
  new_clients_this_month: number;
  client_retention_rate: number;
  average_client_lifetime_value: number;
  client_satisfaction_score: number;
  clients_by_type: Array<{
    client_type: string;
    count: number;
    percentage: number;
  }>;
  client_acquisition_trend: Array<{
    month: string;
    new_clients: number;
    total_clients: number;
  }>;
  top_performing_clients: Array<{
    client_id: number;
    client_name: string;
    total_spent: number;
    service_count: number;
    last_service_date: string;
  }>;
}

export interface OperationalAnalytics {
  total_appointments: number;
  completed_appointments: number;
  completion_rate: number;
  average_appointment_duration: number;
  team_utilization: number;
  equipment_utilization: number;
  service_efficiency: Array<{
    service_type: string;
    average_duration: number;
    completion_rate: number;
    efficiency_score: number;
  }>;
  team_performance: Array<{
    team_id: number;
    team_name: string;
    appointments_completed: number;
    average_rating: number;
    utilization_rate: number;
  }>;
  peak_hours: Array<{
    hour: string;
    appointment_count: number;
    utilization_rate: number;
  }>;
}

export interface FinancialAnalytics {
  total_revenue: number;
  total_expenses: number;
  net_profit: number;
  profit_margin: number;
  cash_flow: number;
  accounts_receivable: number;
  accounts_payable: number;
  revenue_breakdown: Array<{
    category: string;
    amount: number;
    percentage: number;
  }>;
  expense_breakdown: Array<{
    category: string;
    amount: number;
    percentage: number;
  }>;
  profitability_trend: Array<{
    month: string;
    revenue: number;
    expenses: number;
    profit: number;
    margin: number;
  }>;
}

export interface EmployeeAnalytics {
  total_employees: number;
  active_employees: number;
  employee_turnover_rate: number;
  average_employee_tenure: number;
  productivity_metrics: Array<{
    employee_id: number;
    employee_name: string;
    appointments_completed: number;
    hours_worked: number;
    productivity_score: number;
  }>;
  attendance_analytics: {
    average_attendance_rate: number;
    attendance_trend: Array<{
      month: string;
      attendance_rate: number;
    }>;
  };
  performance_analytics: Array<{
    employee_id: number;
    employee_name: string;
    average_rating: number;
    goals_achieved: number;
    goals_total: number;
    performance_score: number;
  }>;
}

export interface InventoryAnalytics {
  total_inventory_value: number;
  inventory_turnover_rate: number;
  low_stock_items: number;
  overstock_items: number;
  top_consumed_items: Array<{
    item_name: string;
    quantity_used: number;
    cost: number;
  }>;
  inventory_trend: Array<{
    month: string;
    inventory_value: number;
    turnover_rate: number;
  }>;
  supplier_performance: Array<{
    supplier_id: number;
    supplier_name: string;
    total_orders: number;
    average_delivery_time: number;
    quality_rating: number;
  }>;
}

export interface KPIDashboard {
  revenue_kpis: {
    monthly_revenue: number;
    revenue_growth: number;
    average_revenue_per_client: number;
    revenue_per_employee: number;
  };
  operational_kpis: {
    appointment_completion_rate: number;
    team_utilization: number;
    client_satisfaction: number;
    service_efficiency: number;
  };
  financial_kpis: {
    profit_margin: number;
    cash_flow: number;
    accounts_receivable_turnover: number;
    return_on_investment: number;
  };
  employee_kpis: {
    employee_productivity: number;
    attendance_rate: number;
    turnover_rate: number;
    training_completion_rate: number;
  };
}

export interface CustomReport {
  id: number;
  name: string;
  description: string;
  report_type: 'revenue' | 'operational' | 'financial' | 'employee' | 'inventory' | 'custom';
  parameters: Record<string, any>;
  created_by: number;
  created_by_name?: string;
  created: string;
  updated: string;
  is_public: boolean;
  schedule?: {
    frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly';
    next_run: string;
  };
}

class AnalyticsService {
  // Revenue Analytics
  async getRevenueAnalytics(params?: {
    start_date?: string;
    end_date?: string;
    period?: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
  }) {
    // Mock implementation - replace with real API call
    const mockRevenueAnalytics: RevenueAnalytics = {
      period: "January 2024",
      total_revenue: 45600.00,
      revenue_growth: 12.5,
      average_revenue_per_client: 1824.00,
      revenue_by_service_type: [
        { service_type: "Regular Cleaning", revenue: 18240.00, percentage: 40.0 },
        { service_type: "Deep Cleaning", revenue: 13680.00, percentage: 30.0 },
        { service_type: "Office Cleaning", revenue: 9120.00, percentage: 20.0 },
        { service_type: "Carpet Cleaning", revenue: 4560.00, percentage: 10.0 },
      ],
      monthly_revenue_trend: [
        { month: "Oct 2023", revenue: 38000.00, growth: 5.2 },
        { month: "Nov 2023", revenue: 39500.00, growth: 3.9 },
        { month: "Dec 2023", revenue: 42000.00, growth: 6.3 },
        { month: "Jan 2024", revenue: 45600.00, growth: 8.6 },
      ],
      top_clients: [
        { client_id: 1, client_name: "ABC Corporation", revenue: 4800.00, service_count: 12 },
        { client_id: 2, client_name: "Downtown Restaurant", revenue: 3600.00, service_count: 8 },
        { client_id: 3, client_name: "Johnson Family", revenue: 2400.00, service_count: 6 },
      ],
    };

    return { data: mockRevenueAnalytics };
  }

  // Client Analytics
  async getClientAnalytics(params?: {
    start_date?: string;
    end_date?: string;
    period?: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
  }) {
    // Mock implementation
    const mockClientAnalytics: ClientAnalytics = {
      total_clients: 25,
      new_clients_this_month: 3,
      client_retention_rate: 92.0,
      average_client_lifetime_value: 3650.00,
      client_satisfaction_score: 4.6,
      clients_by_type: [
        { client_type: "Residential", count: 15, percentage: 60.0 },
        { client_type: "Commercial", count: 8, percentage: 32.0 },
        { client_type: "Industrial", count: 2, percentage: 8.0 },
      ],
      client_acquisition_trend: [
        { month: "Oct 2023", new_clients: 2, total_clients: 20 },
        { month: "Nov 2023", new_clients: 1, total_clients: 21 },
        { month: "Dec 2023", new_clients: 1, total_clients: 22 },
        { month: "Jan 2024", new_clients: 3, total_clients: 25 },
      ],
      top_performing_clients: [
        { client_id: 1, client_name: "ABC Corporation", total_spent: 4800.00, service_count: 12, last_service_date: "2024-01-20" },
        { client_id: 2, client_name: "Downtown Restaurant", total_spent: 3600.00, service_count: 8, last_service_date: "2024-01-18" },
        { client_id: 3, client_name: "Johnson Family", total_spent: 2400.00, service_count: 6, last_service_date: "2024-01-15" },
      ],
    };

    return { data: mockClientAnalytics };
  }

  // Operational Analytics
  async getOperationalAnalytics(params?: {
    start_date?: string;
    end_date?: string;
    period?: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
  }) {
    // Mock implementation
    const mockOperationalAnalytics: OperationalAnalytics = {
      total_appointments: 156,
      completed_appointments: 148,
      completion_rate: 94.9,
      average_appointment_duration: 165,
      team_utilization: 85.5,
      equipment_utilization: 78.2,
      service_efficiency: [
        { service_type: "Regular Cleaning", average_duration: 120, completion_rate: 96.0, efficiency_score: 8.5 },
        { service_type: "Deep Cleaning", average_duration: 240, completion_rate: 94.0, efficiency_score: 8.2 },
        { service_type: "Office Cleaning", average_duration: 180, completion_rate: 95.0, efficiency_score: 8.3 },
        { service_type: "Carpet Cleaning", average_duration: 200, completion_rate: 93.0, efficiency_score: 8.0 },
      ],
      team_performance: [
        { team_id: 1, team_name: "Team Alpha", appointments_completed: 45, average_rating: 4.7, utilization_rate: 88.0 },
        { team_id: 2, team_name: "Team Beta", appointments_completed: 38, average_rating: 4.5, utilization_rate: 82.0 },
        { team_id: 3, team_name: "Team Gamma", appointments_completed: 35, average_rating: 4.6, utilization_rate: 85.0 },
        { team_id: 4, team_name: "Team Delta", appointments_completed: 30, average_rating: 4.4, utilization_rate: 78.0 },
      ],
      peak_hours: [
        { hour: "09:00", appointment_count: 12, utilization_rate: 95.0 },
        { hour: "10:00", appointment_count: 15, utilization_rate: 100.0 },
        { hour: "11:00", appointment_count: 14, utilization_rate: 93.0 },
        { hour: "14:00", appointment_count: 13, utilization_rate: 87.0 },
        { hour: "15:00", appointment_count: 11, utilization_rate: 73.0 },
      ],
    };

    return { data: mockOperationalAnalytics };
  }

  // Financial Analytics
  async getFinancialAnalytics(params?: {
    start_date?: string;
    end_date?: string;
    period?: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
  }) {
    // Mock implementation
    const mockFinancialAnalytics: FinancialAnalytics = {
      total_revenue: 45600.00,
      total_expenses: 12300.00,
      net_profit: 33300.00,
      profit_margin: 73.0,
      cash_flow: 28500.00,
      accounts_receivable: 8800.00,
      accounts_payable: 2100.00,
      revenue_breakdown: [
        { category: "Service Revenue", amount: 45600.00, percentage: 100.0 },
      ],
      expense_breakdown: [
        { category: "Labor Costs", amount: 7200.00, percentage: 58.5 },
        { category: "Equipment & Supplies", amount: 2100.00, percentage: 17.1 },
        { category: "Transportation", amount: 1800.00, percentage: 14.6 },
        { category: "Administrative", amount: 1200.00, percentage: 9.8 },
      ],
      profitability_trend: [
        { month: "Oct 2023", revenue: 38000.00, expenses: 11000.00, profit: 27000.00, margin: 71.1 },
        { month: "Nov 2023", revenue: 39500.00, expenses: 11500.00, profit: 28000.00, margin: 70.9 },
        { month: "Dec 2023", revenue: 42000.00, expenses: 12000.00, profit: 30000.00, margin: 71.4 },
        { month: "Jan 2024", revenue: 45600.00, expenses: 12300.00, profit: 33300.00, margin: 73.0 },
      ],
    };

    return { data: mockFinancialAnalytics };
  }

  // Employee Analytics
  async getEmployeeAnalytics(params?: {
    start_date?: string;
    end_date?: string;
    period?: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
  }) {
    // Mock implementation
    const mockEmployeeAnalytics: EmployeeAnalytics = {
      total_employees: 25,
      active_employees: 23,
      employee_turnover_rate: 8.0,
      average_employee_tenure: 18.5,
      productivity_metrics: [
        { employee_id: 1, employee_name: "John Smith", appointments_completed: 45, hours_worked: 160, productivity_score: 8.7 },
        { employee_id: 2, employee_name: "Maria Garcia", appointments_completed: 42, hours_worked: 155, productivity_score: 8.5 },
        { employee_id: 3, employee_name: "Sarah Johnson", appointments_completed: 38, hours_worked: 150, productivity_score: 8.2 },
        { employee_id: 4, employee_name: "Mike Rodriguez", appointments_completed: 35, hours_worked: 145, productivity_score: 8.0 },
      ],
      attendance_analytics: {
        average_attendance_rate: 96.5,
        attendance_trend: [
          { month: "Oct 2023", attendance_rate: 95.2 },
          { month: "Nov 2023", attendance_rate: 96.8 },
          { month: "Dec 2023", attendance_rate: 97.1 },
          { month: "Jan 2024", attendance_rate: 96.5 },
        ],
      },
      performance_analytics: [
        { employee_id: 1, employee_name: "John Smith", average_rating: 4.8, goals_achieved: 9, goals_total: 10, performance_score: 9.2 },
        { employee_id: 2, employee_name: "Maria Garcia", average_rating: 4.6, goals_achieved: 8, goals_total: 10, performance_score: 8.8 },
        { employee_id: 3, employee_name: "Sarah Johnson", average_rating: 4.7, goals_achieved: 9, goals_total: 10, performance_score: 9.0 },
        { employee_id: 4, employee_name: "Mike Rodriguez", average_rating: 4.5, goals_achieved: 7, goals_total: 10, performance_score: 8.5 },
      ],
    };

    return { data: mockEmployeeAnalytics };
  }

  // Inventory Analytics
  async getInventoryAnalytics(params?: {
    start_date?: string;
    end_date?: string;
    period?: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
  }) {
    // Mock implementation
    const mockInventoryAnalytics: InventoryAnalytics = {
      total_inventory_value: 12500.00,
      inventory_turnover_rate: 4.2,
      low_stock_items: 8,
      overstock_items: 3,
      top_consumed_items: [
        { item_name: "All-Purpose Cleaner", quantity_used: 45, cost: 675.00 },
        { item_name: "Microfiber Cloths", quantity_used: 120, cost: 480.00 },
        { item_name: "Vacuum Bags", quantity_used: 80, cost: 320.00 },
        { item_name: "Floor Cleaner", quantity_used: 35, cost: 280.00 },
      ],
      inventory_trend: [
        { month: "Oct 2023", inventory_value: 11800.00, turnover_rate: 3.8 },
        { month: "Nov 2023", inventory_value: 12100.00, turnover_rate: 4.0 },
        { month: "Dec 2023", inventory_value: 12300.00, turnover_rate: 4.1 },
        { month: "Jan 2024", inventory_value: 12500.00, turnover_rate: 4.2 },
      ],
      supplier_performance: [
        { supplier_id: 1, supplier_name: "CleanPro Supplies", total_orders: 12, average_delivery_time: 2.5, quality_rating: 4.7 },
        { supplier_id: 2, supplier_name: "Equipment Pro", total_orders: 8, average_delivery_time: 3.0, quality_rating: 4.5 },
        { supplier_id: 3, supplier_name: "Supply Chain Co", total_orders: 15, average_delivery_time: 2.0, quality_rating: 4.8 },
      ],
    };

    return { data: mockInventoryAnalytics };
  }

  // KPI Dashboard
  async getKPIDashboard() {
    // Mock implementation
    const mockKPIDashboard: KPIDashboard = {
      revenue_kpis: {
        monthly_revenue: 45600.00,
        revenue_growth: 12.5,
        average_revenue_per_client: 1824.00,
        revenue_per_employee: 1982.61,
      },
      operational_kpis: {
        appointment_completion_rate: 94.9,
        team_utilization: 85.5,
        client_satisfaction: 4.6,
        service_efficiency: 8.3,
      },
      financial_kpis: {
        profit_margin: 73.0,
        cash_flow: 28500.00,
        accounts_receivable_turnover: 5.2,
        return_on_investment: 18.5,
      },
      employee_kpis: {
        employee_productivity: 8.4,
        attendance_rate: 96.5,
        turnover_rate: 8.0,
        training_completion_rate: 92.0,
      },
    };

    return { data: mockKPIDashboard };
  }

  // Custom Reports
  async getCustomReports(params?: {
    report_type?: string;
    created_by?: number;
    is_public?: boolean;
    ordering?: string;
    page?: number;
    page_size?: number;
  }) {
    // Mock implementation
    const mockCustomReports: CustomReport[] = [
      {
        id: 1,
        name: "Monthly Revenue Report",
        description: "Comprehensive monthly revenue analysis",
        report_type: "revenue",
        parameters: { period: "monthly", include_breakdown: true },
        created_by: 1,
        created_by_name: "Admin User",
        created: "2024-01-01T10:00:00Z",
        updated: "2024-01-15T14:30:00Z",
        is_public: true,
        schedule: {
          frequency: "monthly",
          next_run: "2024-02-01T09:00:00Z",
        },
      },
      {
        id: 2,
        name: "Team Performance Analysis",
        description: "Detailed team performance metrics",
        report_type: "operational",
        parameters: { include_ratings: true, include_utilization: true },
        created_by: 1,
        created_by_name: "Admin User",
        created: "2024-01-05T10:00:00Z",
        updated: "2024-01-20T16:45:00Z",
        is_public: false,
      },
    ];

    return { data: mockCustomReports };
  }

  async createCustomReport(data: Partial<CustomReport>) {
    // Mock implementation
    const newReport: CustomReport = {
      id: Date.now(),
      name: data.name || "",
      description: data.description || "",
      report_type: data.report_type || "custom",
      parameters: data.parameters || {},
      created_by: data.created_by || 1,
      created_by_name: data.created_by_name,
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
      is_public: data.is_public || false,
      schedule: data.schedule,
    };

    return { data: newReport };
  }

  async updateCustomReport(id: number, data: Partial<CustomReport>) {
    // Mock implementation
    return { data: { ...data, id, updated: new Date().toISOString() } };
  }

  async deleteCustomReport(id: number) {
    // Mock implementation
    return { data: { id } };
  }
}

export const analyticsService = new AnalyticsService();
