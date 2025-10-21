import { useState, useEffect } from "react";
import { Plus, Search, Filter, Download, Upload, Users, Phone, Mail, MapPin, Calendar, DollarSign, Edit, Eye, MessageSquare } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DataTable } from "@/components/common/DataTable";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { clientService, Client, ServiceRequest, ClientNote, ClientSummary } from "@/services/clientService";
import { ClientForm } from "@/components/clients/ClientForm";
import { ServiceRequestForm } from "@/components/clients/ServiceRequestForm";
import { ClientNotesForm } from "@/components/clients/ClientNotesForm";
import { ClientDetailsModal } from "@/components/clients/ClientDetailsModal";

export default function ClientManagement() {
  const [searchTerm, setSearchTerm] = useState("");
  const [activeTab, setActiveTab] = useState("clients");
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [isClientFormOpen, setIsClientFormOpen] = useState(false);
  const [isServiceRequestFormOpen, setIsServiceRequestFormOpen] = useState(false);
  const [isClientNotesFormOpen, setIsClientNotesFormOpen] = useState(false);
  const [isClientDetailsOpen, setIsClientDetailsOpen] = useState(false);

  // Fetch data from backend
  const { data: clientSummaryResponse, isLoading: summaryLoading, refetch: refetchSummary } = useQuery({
    queryKey: ['clientSummary'],
    queryFn: () => clientService.getClientSummary()
  });

  const { data: clientsResponse, isLoading: clientsLoading, refetch: refetchClients } = useQuery({
    queryKey: ['clients', searchTerm],
    queryFn: () => clientService.getClients({ search: searchTerm, page_size: 100 })
  });

  const { data: serviceRequestsResponse, isLoading: requestsLoading, refetch: refetchRequests } = useQuery({
    queryKey: ['serviceRequests'],
    queryFn: () => clientService.getServiceRequests({ page_size: 50 })
  });

  const clientSummary = clientSummaryResponse?.data;
  const clients = clientsResponse?.results || clientsResponse?.data || [];
  const serviceRequests = serviceRequestsResponse?.results || serviceRequestsResponse?.data || [];

  const isLoading = summaryLoading || clientsLoading || requestsLoading;

  // Client columns
  const clientColumns = [
    {
      key: "display_name",
      header: "Client Name",
      render: (row: Client) => (
        <div>
          <div className="font-medium">{row.display_name || row.name || 'N/A'}</div>
          <div className="text-sm text-muted-foreground">{row.client_type}</div>
        </div>
      ),
    },
    {
      key: "contact",
      header: "Contact",
      render: (row: Client) => (
        <div>
          <div className="font-medium text-sm">{row.contact_person || row.display_name || 'N/A'}</div>
          <div className="text-xs text-muted-foreground">{row.email || 'N/A'}</div>
          <div className="text-xs text-muted-foreground">{row.phone || 'N/A'}</div>
        </div>
      ),
    },
    {
      key: "location",
      header: "Location",
      render: (row: Client) => (
        <div className="text-sm">
          <div>{row.city || 'N/A'}, {row.state || 'N/A'}</div>
          <div className="text-muted-foreground">{row.postal_code || row.zip_code || 'N/A'}</div>
        </div>
      ),
    },
    {
      key: "status",
      header: "Status",
      render: (row: Client) => (
        <Badge variant={
          row.status === 'active' ? 'default' :
          row.status === 'prospect' ? 'secondary' :
          row.status === 'suspended' ? 'destructive' : 'outline'
        }>
          {row.status}
        </Badge>
      ),
    },
    {
      key: "service_frequency",
      header: "Frequency",
      render: (row: Client) => (
        <Badge variant="outline">
          {row.service_frequency || 'N/A'}
        </Badge>
      ),
    },
    {
      key: "total_revenue",
      header: "Revenue",
      render: (row: Client) => row.total_revenue ? `$${row.total_revenue.toLocaleString()}` : '$0',
    },
    {
      key: "next_service_date",
      header: "Next Service",
      render: (row: Client) => (
        <div className="text-sm">
          {row.next_service_date ? new Date(row.next_service_date).toLocaleDateString() : "Not scheduled"}
        </div>
      ),
    },
    {
      key: "actions",
      header: "Actions",
      render: (row: Client) => (
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setSelectedClient(row);
              setIsClientDetailsOpen(true);
            }}
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setSelectedClient(row);
              setIsClientFormOpen(true);
            }}
          >
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setSelectedClient(row);
              setIsServiceRequestFormOpen(true);
            }}
          >
            <Calendar className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setSelectedClient(row);
              setIsClientNotesFormOpen(true);
            }}
          >
            <MessageSquare className="h-4 w-4" />
          </Button>
        </div>
      ),
    },
  ];

  // Service request columns
  const serviceRequestColumns = [
    {
      key: "client_name",
      header: "Client",
    },
    {
      key: "service_type",
      header: "Service Type",
    },
    {
      key: "scheduled_date",
      header: "Scheduled Date",
      render: (row: ServiceRequest) => new Date(row.scheduled_date).toLocaleDateString(),
    },
    {
      key: "status",
      header: "Status",
      render: (row: ServiceRequest) => (
        <Badge variant={
          row.status === 'completed' ? 'default' :
          row.status === 'scheduled' ? 'secondary' :
          row.status === 'in_progress' ? 'outline' :
          row.status === 'cancelled' ? 'destructive' : 'secondary'
        }>
          {row.status}
        </Badge>
      ),
    },
    {
      key: "priority",
      header: "Priority",
      render: (row: ServiceRequest) => (
        <Badge variant={
          row.priority === 'urgent' ? 'destructive' :
          row.priority === 'high' ? 'secondary' :
          row.priority === 'medium' ? 'outline' : 'secondary'
        }>
          {row.priority}
        </Badge>
      ),
    },
    {
      key: "estimated_cost",
      header: "Cost",
      render: (row: ServiceRequest) => `$${row.estimated_cost.toFixed(2)}`,
    },
  ];

  const handleFormSuccess = () => {
    setIsClientFormOpen(false);
    setIsServiceRequestFormOpen(false);
    setIsClientNotesFormOpen(false);
    setSelectedClient(null);
    refetchClients();
    refetchRequests();
    refetchSummary();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading client data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Client Management</h1>
          <p className="text-muted-foreground">
            Manage your cleaning service clients and contracts
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
          <Button variant="outline" size="sm">
            <Upload className="mr-2 h-4 w-4" />
            Import
          </Button>
          {activeTab === "clients" && (
            <Button size="sm" onClick={() => setIsClientFormOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Add Client
            </Button>
          )}
          {activeTab === "requests" && (
            <Button size="sm" onClick={() => setIsServiceRequestFormOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              New Request
            </Button>
          )}
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Clients</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{clientSummary?.total_clients || 0}</div>
            <p className="text-xs text-muted-foreground">+{clientSummary?.new_clients_this_month || 0} this month</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Clients</CardTitle>
            <Phone className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{clientSummary?.active_clients || 0}</div>
            <p className="text-xs text-muted-foreground">Currently active</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${clientSummary?.total_revenue?.toLocaleString() || 0}</div>
            <p className="text-xs text-muted-foreground">All time revenue</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Frequency</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{clientSummary?.average_service_frequency || "N/A"}</div>
            <p className="text-xs text-muted-foreground">Service frequency</p>
          </CardContent>
        </Card>
      </div>

      {/* Top Service Types */}
      {clientSummary?.top_service_types && clientSummary.top_service_types.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Top Service Types</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {clientSummary.top_service_types.map((service, index) => (
                <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-muted/30">
                  <div>
                    <p className="font-medium text-sm">{service.service_type}</p>
                    <p className="text-xs text-muted-foreground">{service.count} services</p>
                  </div>
                  <Badge variant="outline">{service.count}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="clients">Clients</TabsTrigger>
          <TabsTrigger value="requests">Service Requests</TabsTrigger>
        </TabsList>

        <TabsContent value="clients" className="space-y-4">
          {/* Filters */}
          <div className="flex items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search clients..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button variant="outline" size="sm">
              <Filter className="mr-2 h-4 w-4" />
              Filter
            </Button>
          </div>

          {/* Clients Table */}
          <Card>
            <CardHeader>
              <CardTitle>All Clients</CardTitle>
            </CardHeader>
            <CardContent>
              <DataTable data={clients || []} columns={clientColumns} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="requests" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Service Requests</CardTitle>
            </CardHeader>
            <CardContent>
              <DataTable data={serviceRequests || []} columns={serviceRequestColumns} />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Forms */}
      <ClientForm
        open={isClientFormOpen}
        onOpenChange={setIsClientFormOpen}
        client={selectedClient}
        onSuccess={handleFormSuccess}
      />

      <ServiceRequestForm
        open={isServiceRequestFormOpen}
        onOpenChange={setIsServiceRequestFormOpen}
        client={selectedClient}
        onSuccess={handleFormSuccess}
      />

      <ClientNotesForm
        open={isClientNotesFormOpen}
        onOpenChange={setIsClientNotesFormOpen}
        client={selectedClient}
        onSuccess={handleFormSuccess}
      />

      <ClientDetailsModal
        open={isClientDetailsOpen}
        onOpenChange={setIsClientDetailsOpen}
        client={selectedClient}
      />
    </div>
  );
}