import * as React from "react";
import { useNavigate } from "react-router-dom";
import { cn } from "@/lib/utils";
import { useTheme } from "@/contexts/ThemeContext";
import { useAuth } from "@/contexts/EnhancedAuthContext";
import { Button } from "@/components/ui/enhanced-button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Command,
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "@/components/ui/command";
import {
  Bell,
  Search,
  User,
  Settings,
  LogOut,
  Moon,
  Sun,
  Monitor,
  HelpCircle,
  CreditCard,
  Building2,
  ChevronDown,
  Plus,
  Filter,
  Download,
  Upload,
  RefreshCw,
} from "lucide-react";
import { SidebarTrigger } from "./EnhancedSidebar";
import { NetworkStatus } from "@/components/common/NetworkStatus";
import { NotificationBell } from "@/components/ui/enhanced-notifications";

export function EnhancedHeader() {
  const { theme, setTheme, isDark, toggleTheme } = useTheme();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [searchOpen, setSearchOpen] = React.useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const getUserInitials = () => {
    if (user?.first_name && user?.last_name) {
      return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
    }
    return user?.email?.[0]?.toUpperCase() || "U";
  };

  const getUserDisplayName = () => {
    if (user?.first_name && user?.last_name) {
      return `${user.first_name} ${user.last_name}`;
    }
    return user?.email || "User";
  };

  const searchItems = [
    {
      title: "Dashboard",
      description: "View your business overview",
      url: "/dashboard",
      icon: Building2,
    },
    {
      title: "Inventory",
      description: "Manage products and stock",
      url: "/inventory",
      icon: Building2,
    },
    {
      title: "Finance",
      description: "Track invoices and payments",
      url: "/finance",
      icon: Building2,
    },
    {
      title: "HR Management",
      description: "Manage employees and payroll",
      url: "/hr",
      icon: Building2,
    },
    {
      title: "Scheduling",
      description: "Schedule appointments",
      url: "/scheduling",
      icon: Building2,
    },
    {
      title: "Analytics",
      description: "View business analytics",
      url: "/analytics",
      icon: Building2,
    },
  ];

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 px-4 sm:px-6">
      {/* Sidebar Trigger */}
      <SidebarTrigger />

      {/* Search */}
      <div className="relative ml-auto flex-1 md:grow-0">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search clients, invoices, inventory..."
            className="pl-10 w-80 bg-background"
            onFocus={() => setSearchOpen(true)}
          />
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        {/* Network Status */}
        <NetworkStatus />

        {/* Quick Actions */}
        <Button variant="ghost" size="icon" title="Add New">
          <Plus className="h-4 w-4" />
        </Button>

        <Button variant="ghost" size="icon" title="Filter">
          <Filter className="h-4 w-4" />
        </Button>

        <Button variant="ghost" size="icon" title="Export">
          <Download className="h-4 w-4" />
        </Button>

        <Button variant="ghost" size="icon" title="Import">
          <Upload className="h-4 w-4" />
        </Button>

        <Button variant="ghost" size="icon" title="Refresh">
          <RefreshCw className="h-4 w-4" />
        </Button>

        {/* Notifications */}
        <NotificationBell count={3} />

        {/* Theme Toggle */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon">
              <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
              <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
              <span className="sr-only">Toggle theme</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => setTheme("light")}>
              <Sun className="mr-2 h-4 w-4" />
              Light
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setTheme("dark")}>
              <Moon className="mr-2 h-4 w-4" />
              Dark
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setTheme("system")}>
              <Monitor className="mr-2 h-4 w-4" />
              System
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* User Menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="relative h-10 w-10 rounded-full">
              <Avatar className="h-10 w-10">
                <AvatarImage src={user?.avatar} alt={getUserDisplayName()} />
                <AvatarFallback>{getUserInitials()}</AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56" align="end" forceMount>
            <DropdownMenuLabel className="font-normal">
              <div className="flex flex-col space-y-1">
                <p className="text-sm font-medium leading-none">
                  {getUserDisplayName()}
                </p>
                <p className="text-xs leading-none text-muted-foreground">
                  {user?.email || "user@example.com"}
                </p>
                <Badge variant="secondary" className="w-fit text-xs">
                  Enterprise
                </Badge>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <User className="mr-2 h-4 w-4" />
              <span>Profile</span>
            </DropdownMenuItem>
            <DropdownMenuItem>
              <Settings className="mr-2 h-4 w-4" />
              <span>Settings</span>
            </DropdownMenuItem>
            <DropdownMenuItem>
              <CreditCard className="mr-2 h-4 w-4" />
              <span>Billing</span>
            </DropdownMenuItem>
            <DropdownMenuItem>
              <HelpCircle className="mr-2 h-4 w-4" />
              <span>Help & Support</span>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-destructive" onClick={handleLogout}>
              <LogOut className="mr-2 h-4 w-4" />
              <span>Log out</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Command Dialog */}
      <CommandDialog open={searchOpen} onOpenChange={setSearchOpen}>
        <CommandInput placeholder="Search for pages, features, or actions..." />
        <CommandList>
          <CommandEmpty>No results found.</CommandEmpty>
          <CommandGroup heading="Pages">
            {searchItems.map((item) => (
              <CommandItem
                key={item.title}
                onSelect={() => {
                  navigate(item.url);
                  setSearchOpen(false);
                }}
              >
                <item.icon className="mr-2 h-4 w-4" />
                <div className="flex flex-col">
                  <span>{item.title}</span>
                  <span className="text-xs text-muted-foreground">
                    {item.description}
                  </span>
                </div>
              </CommandItem>
            ))}
          </CommandGroup>
          <CommandSeparator />
          <CommandGroup heading="Quick Actions">
            <CommandItem onSelect={() => setSearchOpen(false)}>
              <Plus className="mr-2 h-4 w-4" />
              <span>Add New Client</span>
            </CommandItem>
            <CommandItem onSelect={() => setSearchOpen(false)}>
              <Plus className="mr-2 h-4 w-4" />
              <span>Create Invoice</span>
            </CommandItem>
            <CommandItem onSelect={() => setSearchOpen(false)}>
              <Plus className="mr-2 h-4 w-4" />
              <span>Schedule Appointment</span>
            </CommandItem>
          </CommandGroup>
        </CommandList>
      </CommandDialog>
    </header>
  );
}

// Header Actions Component
interface HeaderActionsProps {
  onAddNew?: () => void;
  onFilter?: () => void;
  onExport?: () => void;
  onImport?: () => void;
  onRefresh?: () => void;
  className?: string;
}

export function HeaderActions({
  onAddNew,
  onFilter,
  onExport,
  onImport,
  onRefresh,
  className,
}: HeaderActionsProps) {
  return (
    <div className={cn("flex items-center gap-2", className)}>
      {onAddNew && (
        <Button variant="ghost" size="icon" onClick={onAddNew} title="Add New">
          <Plus className="h-4 w-4" />
        </Button>
      )}
      {onFilter && (
        <Button variant="ghost" size="icon" onClick={onFilter} title="Filter">
          <Filter className="h-4 w-4" />
        </Button>
      )}
      {onExport && (
        <Button variant="ghost" size="icon" onClick={onExport} title="Export">
          <Download className="h-4 w-4" />
        </Button>
      )}
      {onImport && (
        <Button variant="ghost" size="icon" onClick={onImport} title="Import">
          <Upload className="h-4 w-4" />
        </Button>
      )}
      {onRefresh && (
        <Button variant="ghost" size="icon" onClick={onRefresh} title="Refresh">
          <RefreshCw className="h-4 w-4" />
        </Button>
      )}
    </div>
  );
}

export default EnhancedHeader;
