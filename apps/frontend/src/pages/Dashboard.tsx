import {
  Users,
  Calendar,
  DollarSign,
  Package,
  TrendingUp,
  TrendingDown,
  Activity,
  Clock,
  AlertTriangle,
  Loader2,
} from "lucide-react";
import { KPICard } from "@/components/dashboard/KPICard";
import { DashboardChart } from "@/components/dashboard/DashboardChart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useQuery } from "@tanstack/react-query";
import { dashboardService, DashboardKPIs, RecentActivity, StockAlert } from "@/services/dashboardService";

export default function Dashboard() {
  // Fetch real data from backend
  const { data: kpis, isLoading: kpisLoading, error: kpisError } = useQuery<DashboardKPIs>({
    queryKey: ['dashboard', 'kpis'],
    queryFn: () => dashboardService.getKPIs()
  });
  
  const { data: revenueData, isLoading: revenueLoading } = useQuery({
    queryKey: ['dashboard', 'revenue'],
    queryFn: () => dashboardService.getRevenueTrend()
  });
  
  const { data: serviceDistribution, isLoading: serviceLoading } = useQuery({
    queryKey: ['dashboard', 'services'],
    queryFn: () => dashboardService.getServiceDistribution()
  });
  
  const { data: teamProductivity, isLoading: teamLoading } = useQuery({
    queryKey: ['dashboard', 'team'],
    queryFn: () => dashboardService.getTeamProductivity()
  });
  
  const { data: recentActivities, isLoading: activitiesLoading } = useQuery<RecentActivity[]>({
    queryKey: ['dashboard', 'activities'],
    queryFn: () => dashboardService.getRecentActivities()
  });
  
  const { data: stockAlerts, isLoading: alertsLoading } = useQuery<StockAlert[]>({
    queryKey: ['dashboard', 'alerts'],
    queryFn: () => dashboardService.getStockAlerts()
  });

  const isLoading = kpisLoading || revenueLoading || serviceLoading || teamLoading || activitiesLoading || alertsLoading;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  if (kpisError) {
    return (
      <div className="space-y-6">
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Failed to load dashboard data. Please try refreshing the page.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back! Here's what's happening with your cleaning service.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <KPICard
          title="Total Clients"
          value={kpis?.total_clients?.toString() || "0"}
          change="+12%"
          changeType="positive"
          icon={Users}
          description="Active cleaning contracts"
        />
        <KPICard
          title="Monthly Revenue"
          value={`$${kpis?.monthly_revenue?.toLocaleString() || "0"}`}
          change="+8%"
          changeType="positive"
          icon={DollarSign}
          description="Revenue this month"
        />
        <KPICard
          title="Scheduled Services"
          value={kpis?.scheduled_services?.toString() || "0"}
          change="-3%"
          changeType="negative"
          icon={Calendar}
          description="Services this week"
        />
        <KPICard
          title="Inventory Items"
          value={kpis?.inventory_items?.toString() || "0"}
          change="+2%"
          changeType="positive"
          icon={Package}
          description="Items in stock"
        />
      </div>

      {/* Charts Row */}
      <div className="grid gap-6 md:grid-cols-2">
        <DashboardChart
          title="Monthly Revenue Trend"
          data={revenueData || []}
          type="line"
          dataKey="value"
          color="hsl(var(--primary))"
        />
        <DashboardChart
          title="Service Distribution"
          data={serviceDistribution || []}
          type="pie"
          dataKey="value"
        />
      </div>

      {/* Bottom Row */}
      <div className="grid gap-6 md:grid-cols-3">
        {/* Team Productivity */}
        <DashboardChart
          title="Team Productivity"
          data={teamProductivity || []}
          type="bar"
          dataKey="value"
          color="hsl(var(--accent))"
        />

        {/* Recent Activity */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Recent Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivities?.map((activity) => (
                <div
                  key={activity.id}
                  className="flex items-center justify-between p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors"
                >
                  <div className="flex-1">
                    <p className="font-medium text-sm">{activity.action}</p>
                    <p className="text-muted-foreground text-xs">
                      {activity.client}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge
                      variant={
                        activity.type === "payment"
                          ? "default"
                          : activity.type === "client"
                          ? "secondary"
                          : "outline"
                      }
                      className="text-xs"
                    >
                      {activity.type}
                    </Badge>
                    <div className="flex items-center gap-1 text-xs text-muted-foreground">
                      <Clock className="h-3 w-3" />
                      {activity.time}
                    </div>
                  </div>
                </div>
              )) || (
                <div className="text-center py-8 text-muted-foreground">
                  No recent activities
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Stats */}
      <div className="grid gap-6 md:grid-cols-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Today's Jobs</p>
              <p className="text-2xl font-bold">{kpis?.todays_jobs || 0}</p>
            </div>
            <TrendingUp className="h-8 w-8 text-success" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Active Staff</p>
              <p className="text-2xl font-bold">{kpis?.active_staff || 0}</p>
            </div>
            <Users className="h-8 w-8 text-primary" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Completion Rate</p>
              <p className="text-2xl font-bold">{kpis?.completion_rate || 0}%</p>
            </div>
            <TrendingUp className="h-8 w-8 text-success" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Low Stock Items</p>
              <p className="text-2xl font-bold">{kpis?.low_stock_items || 0}</p>
            </div>
            <TrendingDown className="h-8 w-8 text-warning" />
          </div>
        </Card>
      </div>

      {/* Stock Alerts */}
      {stockAlerts && stockAlerts.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-warning" />
              Stock Alerts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {stockAlerts.slice(0, 5).map((alert) => (
                <div
                  key={alert.product_id}
                  className="flex items-center justify-between p-3 rounded-lg bg-warning-light/20 border border-warning/20"
                >
                  <div className="flex-1">
                    <p className="font-medium text-sm">{alert.product_name}</p>
                    <p className="text-muted-foreground text-xs">
                      SKU: {alert.product_sku} • Current: {alert.current_stock} • Min: {alert.min_stock_level}
                    </p>
                  </div>
                  <Badge
                    variant={alert.alert_type === 'out_of_stock' ? 'destructive' : 'secondary'}
                    className="text-xs"
                  >
                    {alert.alert_type === 'out_of_stock' ? 'Out of Stock' : 'Low Stock'}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}