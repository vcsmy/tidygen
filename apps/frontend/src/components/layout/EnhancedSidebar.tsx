import * as React from "react";
import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { useTheme } from "@/contexts/ThemeContext";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Button } from "@/components/ui/enhanced-button";
import { Badge } from "@/components/ui/badge";
import {
  Home,
  Package,
  DollarSign,
  Users,
  Calendar,
  BarChart3,
  Building2,
  Settings,
  HelpCircle,
  Bell,
  ChevronRight,
  Sparkles,
  Shield,
  Zap,
} from "lucide-react";

// Navigation Items
const navigationItems = [
  {
    title: "Overview",
    items: [
      {
        title: "Dashboard",
        url: "/dashboard",
        icon: Home,
        badge: null,
      },
    ],
  },
  {
    title: "Business",
    items: [
      {
        title: "Inventory",
        url: "/inventory",
        icon: Package,
        badge: "New",
        badgeVariant: "default" as const,
        items: [
          {
            title: "Products",
            url: "/inventory/products",
          },
          {
            title: "Categories",
            url: "/inventory/categories",
          },
          {
            title: "Suppliers",
            url: "/inventory/suppliers",
          },
          {
            title: "Stock Movements",
            url: "/inventory/stock-movements",
          },
        ],
      },
      {
        title: "Finance",
        url: "/finance",
        icon: DollarSign,
        badge: null,
        items: [
          {
            title: "Invoices",
            url: "/finance/invoices",
          },
          {
            title: "Payments",
            url: "/finance/payments",
          },
          {
            title: "Expenses",
            url: "/finance/expenses",
          },
          {
            title: "Reports",
            url: "/finance/reports",
          },
        ],
      },
      {
        title: "HR Management",
        url: "/hr",
        icon: Users,
        badge: null,
        items: [
          {
            title: "Employees",
            url: "/hr/employees",
          },
          {
            title: "Attendance",
            url: "/hr/attendance",
          },
          {
            title: "Payroll",
            url: "/hr/payroll",
          },
          {
            title: "Performance",
            url: "/hr/performance",
          },
        ],
      },
      {
        title: "Scheduling",
        url: "/scheduling",
        icon: Calendar,
        badge: null,
        items: [
          {
            title: "Appointments",
            url: "/scheduling/appointments",
          },
          {
            title: "Calendar",
            url: "/scheduling/calendar",
          },
          {
            title: "Resources",
            url: "/scheduling/resources",
          },
        ],
      },
      {
        title: "Client Management",
        url: "/clients",
        icon: Building2,
        badge: null,
        items: [
          {
            title: "Clients",
            url: "/clients/list",
          },
          {
            title: "Service Requests",
            url: "/clients/service-requests",
          },
          {
            title: "Communications",
            url: "/clients/communications",
          },
        ],
      },
    ],
  },
  {
    title: "Analytics",
    items: [
      {
        title: "Analytics",
        url: "/analytics",
        icon: BarChart3,
        badge: "Pro",
        badgeVariant: "secondary" as const,
        items: [
          {
            title: "Dashboard",
            url: "/analytics/dashboard",
          },
          {
            title: "Reports",
            url: "/analytics/reports",
          },
          {
            title: "Custom Reports",
            url: "/analytics/custom-reports",
          },
        ],
      },
    ],
  },
  {
    title: "System",
    items: [
      {
        title: "Settings",
        url: "/settings",
        icon: Settings,
        badge: null,
        items: [
          {
            title: "General",
            url: "/settings/general",
          },
          {
            title: "Users",
            url: "/settings/users",
          },
          {
            title: "Integrations",
            url: "/settings/integrations",
          },
        ],
      },
    ],
  },
];

// Sidebar Component
export function EnhancedSidebar() {
  const { isDark } = useTheme();
  const location = useLocation();

  const isActive = (url: string) => {
    return location.pathname === url || location.pathname.startsWith(url + "/");
  };

  const hasActiveChild = (items: any[]) => {
    return items?.some((item) => isActive(item.url));
  };

  return (
    <Sidebar
      className={cn(
        "border-r transition-colors duration-200",
        isDark ? "border-gray-700 bg-gray-900" : "border-gray-200 bg-white"
      )}
    >
      <SidebarHeader className="border-b border-border p-4">
        <div className="flex items-center space-x-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
            <Building2 className="h-5 w-5 text-primary-foreground" />
          </div>
          <div className="flex flex-col">
            <span className="text-lg font-bold">TidyGen</span>
            <span className="text-xs text-muted-foreground">Enterprise Edition</span>
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent className="p-2">
        {navigationItems.map((group, groupIndex) => (
          <SidebarGroup key={groupIndex}>
            <SidebarGroupLabel className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
              {group.title}
            </SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {group.items.map((item) => (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton
                      asChild
                      isActive={isActive(item.url)}
                      className={cn(
                        "w-full justify-start",
                        isActive(item.url) && "bg-primary/10 text-primary"
                      )}
                    >
                      <Link to={item.url}>
                        <item.icon className="h-4 w-4" />
                        <span>{item.title}</span>
                        {item.badge && (
                          <Badge
                            variant={item.badgeVariant || "default"}
                            className="ml-auto text-xs"
                          >
                            {item.badge}
                          </Badge>
                        )}
                        {item.items && (
                          <ChevronRight className="ml-auto h-4 w-4" />
                        )}
                      </Link>
                    </SidebarMenuButton>
                    
                    {item.items && hasActiveChild(item.items) && (
                      <SidebarMenuSub>
                        {item.items.map((subItem) => (
                          <SidebarMenuSubItem key={subItem.title}>
                            <SidebarMenuSubButton
                              asChild
                              isActive={isActive(subItem.url)}
                            >
                              <Link to={subItem.url}>
                                <span>{subItem.title}</span>
                              </Link>
                            </SidebarMenuSubButton>
                          </SidebarMenuSubItem>
                        ))}
                      </SidebarMenuSub>
                    )}
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        ))}
      </SidebarContent>

      <SidebarFooter className="border-t border-border p-4">
        <div className="space-y-2">
          {/* Quick Actions */}
          <div className="space-y-1">
            <Button
              variant="outline"
              size="sm"
              className="w-full justify-start"
            >
              <Bell className="h-4 w-4 mr-2" />
              Notifications
              <Badge variant="destructive" className="ml-auto text-xs">
                3
              </Badge>
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="w-full justify-start"
            >
              <HelpCircle className="h-4 w-4 mr-2" />
              Help & Support
            </Button>
          </div>

          {/* Upgrade Banner */}
          <div className="rounded-lg bg-gradient-to-r from-primary/10 to-accent/10 p-3 border border-primary/20">
            <div className="flex items-center space-x-2 mb-2">
              <Sparkles className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium">Upgrade to Pro</span>
            </div>
            <p className="text-xs text-muted-foreground mb-2">
              Unlock advanced features and AI-powered analytics
            </p>
            <Button size="sm" className="w-full">
              Upgrade Now
            </Button>
          </div>

          {/* Security Badge */}
          <div className="flex items-center space-x-2 text-xs text-muted-foreground">
            <Shield className="h-3 w-3" />
            <span>Enterprise Security</span>
          </div>
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}

// Sidebar Trigger Component
export function SidebarTrigger() {
  return (
    <SidebarTrigger className="hover:bg-accent hover:text-accent-foreground" />
  );
}

// Collapsible Sidebar Hook
export function useSidebar() {
  const [isCollapsed, setIsCollapsed] = React.useState(false);

  const toggle = React.useCallback(() => {
    setIsCollapsed(prev => !prev);
  }, []);

  const collapse = React.useCallback(() => {
    setIsCollapsed(true);
  }, []);

  const expand = React.useCallback(() => {
    setIsCollapsed(false);
  }, []);

  return {
    isCollapsed,
    toggle,
    collapse,
    expand,
  };
}

export default EnhancedSidebar;
