import { useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Users,
  Package,
  Receipt,
  UserCheck,
  BarChart3,
  Settings,
  Bell,
  Calendar,
  FileText,
  ChevronDown,
  Building,
} from "lucide-react";

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarTrigger,
  useSidebar,
  SidebarHeader,
} from "@/components/ui/sidebar";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { cn } from "@/lib/utils";

const mainNavItems = [
  { title: "Dashboard", url: "/", icon: LayoutDashboard },
  { title: "Clients", url: "/clients", icon: Users },
  { title: "Scheduling", url: "/scheduling", icon: Calendar },
  { title: "Inventory", url: "/inventory", icon: Package },
  { title: "Finance", url: "/finance", icon: Receipt },
  { title: "HR & Payroll", url: "/hr", icon: UserCheck },
  { title: "Analytics", url: "/analytics", icon: BarChart3 },
];

const managementItems = [
  { title: "Reports", url: "/reports", icon: FileText },
  { title: "Notifications", url: "/notifications", icon: Bell },
  { title: "Settings", url: "/settings", icon: Settings },
];

export function AppSidebar() {
  const { state } = useSidebar();
  const location = useLocation();
  const currentPath = location.pathname;
  const [managementOpen, setManagementOpen] = useState(true);
  const isCollapsed = state === "collapsed";

  const isActive = (path: string) => currentPath === path;
  const isMainExpanded = mainNavItems.some((item) => isActive(item.url));

  const getNavClass = (path: string) =>
    cn(
      "w-full justify-start gap-3 font-medium transition-all duration-200",
      isActive(path)
        ? "bg-sidebar-accent text-sidebar-primary border-r-2 border-sidebar-primary"
        : "text-sidebar-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-primary"
    );

  return (
    <Sidebar
      className="border-r border-sidebar-border"
      collapsible="icon"
    >
      <SidebarHeader className="border-b border-sidebar-border p-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-primary">
            <Building className="h-6 w-6 text-white" />
          </div>
          {!isCollapsed && (
            <div>
              <h2 className="text-lg font-bold text-sidebar-foreground">TidyGen</h2>
              <p className="text-sm text-sidebar-foreground/70">ERP System</p>
            </div>
          )}
        </div>
      </SidebarHeader>

      <SidebarContent className="py-4">
        <SidebarGroup>
          <SidebarGroupLabel className="text-sidebar-foreground/70">
            Main Menu
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {mainNavItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <NavLink to={item.url} className={getNavClass(item.url)}>
                      <item.icon className="h-5 w-5 flex-shrink-0" />
                      <span>{item.title}</span>
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <Collapsible open={managementOpen} onOpenChange={setManagementOpen}>
          <SidebarGroup>
            <CollapsibleTrigger asChild>
            <SidebarGroupLabel className="cursor-pointer text-sidebar-foreground/70 hover:text-sidebar-foreground flex items-center justify-between">
                <span>Management</span>
                <ChevronDown className={cn("h-4 w-4 transition-transform", managementOpen && "rotate-180")} />
              </SidebarGroupLabel>
            </CollapsibleTrigger>
            <CollapsibleContent>
              <SidebarGroupContent>
                <SidebarMenu>
                  {managementItems.map((item) => (
                    <SidebarMenuItem key={item.title}>
                      <SidebarMenuButton asChild>
                        <NavLink to={item.url} className={getNavClass(item.url)}>
                          <item.icon className="h-5 w-5 flex-shrink-0" />
                          <span>{item.title}</span>
                        </NavLink>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </CollapsibleContent>
          </SidebarGroup>
        </Collapsible>
      </SidebarContent>
    </Sidebar>
  );
}