import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Building, 
  Truck, 
  Wrench, 
  Package, 
  MapPin, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  TrendingUp,
  Calendar,
  DollarSign,
  Shield
} from 'lucide-react';

interface Facility {
  id: number;
  name: string;
  facility_type: string;
  address: string;
  city: string;
  state: string;
  is_active: boolean;
  vehicle_count?: number;
  equipment_count?: number;
}

interface Vehicle {
  id: number;
  make: string;
  model: string;
  year: number;
  license_plate: string;
  vehicle_type: string;
  status: string;
  current_mileage: number;
  home_facility_name?: string;
  maintenance_count?: number;
}

interface Equipment {
  id: number;
  name: string;
  equipment_type: string;
  brand: string;
  model: string;
  status: string;
  condition: string;
  current_facility_name?: string;
  assigned_to_name?: string;
  maintenance_count?: number;
}

interface MaintenanceRecord {
  id: number;
  title: string;
  maintenance_type: string;
  priority: string;
  status: string;
  scheduled_date: string;
  completed_date?: string;
  estimated_cost: number;
  actual_cost?: number;
  vehicle_name?: string;
  equipment_name?: string;
}

interface Asset {
  id: number;
  name: string;
  asset_type: string;
  description: string;
  purchase_price: number;
  current_value: number;
  location_name?: string;
  is_tokenized: boolean;
  nft_token_id?: string;
}

interface DashboardSummary {
  total_facilities: number;
  active_facilities: number;
  total_vehicles: number;
  total_equipment: number;
  facility_types: Array<{ facility_type: string; count: number }>;
}

const FacilityManagementDashboard: React.FC = () => {
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [maintenance, setMaintenance] = useState<MaintenanceRecord[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch facilities
      const facilitiesResponse = await fetch('/api/v1/facility-management/facilities/');
      if (facilitiesResponse.ok) {
        const facilitiesData = await facilitiesResponse.json();
        setFacilities(facilitiesData.results || facilitiesData);
      }

      // Fetch vehicles
      const vehiclesResponse = await fetch('/api/v1/facility-management/vehicles/');
      if (vehiclesResponse.ok) {
        const vehiclesData = await vehiclesResponse.json();
        setVehicles(vehiclesData.results || vehiclesData);
      }

      // Fetch equipment
      const equipmentResponse = await fetch('/api/v1/facility-management/equipment/');
      if (equipmentResponse.ok) {
        const equipmentData = await equipmentResponse.json();
        setEquipment(equipmentData.results || equipmentData);
      }

      // Fetch maintenance records
      const maintenanceResponse = await fetch('/api/v1/facility-management/maintenance-records/');
      if (maintenanceResponse.ok) {
        const maintenanceData = await maintenanceResponse.json();
        setMaintenance(maintenanceData.results || maintenanceData);
      }

      // Fetch assets
      const assetsResponse = await fetch('/api/v1/facility-management/assets/');
      if (assetsResponse.ok) {
        const assetsData = await assetsResponse.json();
        setAssets(assetsData.results || assetsData);
      }

      // Fetch dashboard summary
      const summaryResponse = await fetch('/api/v1/facility-management/facilities/dashboard-summary/');
      if (summaryResponse.ok) {
        const summaryData = await summaryResponse.json();
        setSummary(summaryData);
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
      case 'operational':
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
      case 'maintenance':
        return 'bg-blue-100 text-blue-800';
      case 'scheduled':
      case 'planned':
        return 'bg-yellow-100 text-yellow-800';
      case 'urgent':
      case 'retired':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'urgent':
        return 'bg-red-100 text-red-800';
      case 'high':
        return 'bg-orange-100 text-orange-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getConditionColor = (condition: string) => {
    switch (condition.toLowerCase()) {
      case 'excellent':
        return 'bg-green-100 text-green-800';
      case 'good':
        return 'bg-blue-100 text-blue-800';
      case 'fair':
        return 'bg-yellow-100 text-yellow-800';
      case 'poor':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading Facility Management Dashboard...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Facility Management Dashboard</h1>
        <Button onClick={fetchDashboardData} variant="outline">
          Refresh Data
        </Button>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Facilities</CardTitle>
              <Building className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary.total_facilities}</div>
              <p className="text-xs text-muted-foreground">
                {summary.active_facilities} active facilities
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Fleet Vehicles</CardTitle>
              <Truck className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary.total_vehicles}</div>
              <p className="text-xs text-muted-foreground">
                {vehicles.filter(v => v.status === 'active').length} active
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Equipment</CardTitle>
              <Wrench className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary.total_equipment}</div>
              <p className="text-xs text-muted-foreground">
                {equipment.filter(e => e.status === 'active').length} operational
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Maintenance Due</CardTitle>
              <AlertCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {maintenance.filter(m => m.status === 'scheduled').length}
              </div>
              <p className="text-xs text-muted-foreground">
                Scheduled maintenance
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content Tabs */}
      <Tabs defaultValue="facilities" className="space-y-4">
        <TabsList>
          <TabsTrigger value="facilities">Facilities</TabsTrigger>
          <TabsTrigger value="vehicles">Fleet</TabsTrigger>
          <TabsTrigger value="equipment">Equipment</TabsTrigger>
          <TabsTrigger value="maintenance">Maintenance</TabsTrigger>
          <TabsTrigger value="assets">Assets</TabsTrigger>
        </TabsList>

        {/* Facilities Tab */}
        <TabsContent value="facilities" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {facilities.map((facility) => (
              <Card key={facility.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{facility.name}</CardTitle>
                    <Badge className={getStatusColor(facility.is_active ? 'active' : 'inactive')}>
                      {facility.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {facility.facility_type} • {facility.city}, {facility.state}
                  </p>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <MapPin className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">{facility.address}</span>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Vehicles</p>
                      <p className="font-semibold">{facility.vehicle_count || 0}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Equipment</p>
                      <p className="font-semibold">{facility.equipment_count || 0}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Vehicles Tab */}
        <TabsContent value="vehicles" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {vehicles.map((vehicle) => (
              <Card key={vehicle.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">
                      {vehicle.year} {vehicle.make} {vehicle.model}
                    </CardTitle>
                    <Badge className={getStatusColor(vehicle.status)}>
                      {vehicle.status}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {vehicle.license_plate} • {vehicle.vehicle_type}
                  </p>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Mileage</p>
                      <p className="font-semibold">{vehicle.current_mileage.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Home Base</p>
                      <p className="font-semibold text-xs">
                        {vehicle.home_facility_name || 'Not assigned'}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Maintenance</p>
                      <p className="font-semibold">{vehicle.maintenance_count || 0} records</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Type</p>
                      <p className="font-semibold capitalize">{vehicle.vehicle_type}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Equipment Tab */}
        <TabsContent value="equipment" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {equipment.map((item) => (
              <Card key={item.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{item.name}</CardTitle>
                    <div className="flex space-x-2">
                      <Badge className={getStatusColor(item.status)}>
                        {item.status}
                      </Badge>
                      <Badge className={getConditionColor(item.condition)}>
                        {item.condition}
                      </Badge>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {item.brand} {item.model} • {item.equipment_type}
                  </p>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Location</p>
                      <p className="font-semibold text-xs">
                        {item.current_facility_name || 'Not assigned'}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Assigned To</p>
                      <p className="font-semibold text-xs">
                        {item.assigned_to_name || 'Unassigned'}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Maintenance</p>
                      <p className="font-semibold">{item.maintenance_count || 0} records</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Type</p>
                      <p className="font-semibold capitalize">{item.equipment_type}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Maintenance Tab */}
        <TabsContent value="maintenance" className="space-y-4">
          <div className="space-y-4">
            {maintenance.map((record) => (
              <Card key={record.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg">{record.title}</CardTitle>
                      <p className="text-sm text-muted-foreground">
                        {record.maintenance_type} • {record.vehicle_name || record.equipment_name}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge className={getPriorityColor(record.priority)}>
                        {record.priority}
                      </Badge>
                      <Badge className={getStatusColor(record.status)}>
                        {record.status}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Scheduled</p>
                      <p className="font-semibold">
                        {new Date(record.scheduled_date).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Completed</p>
                      <p className="font-semibold">
                        {record.completed_date 
                          ? new Date(record.completed_date).toLocaleDateString()
                          : 'Pending'
                        }
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Estimated Cost</p>
                      <p className="font-semibold">${record.estimated_cost}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Actual Cost</p>
                      <p className="font-semibold">
                        {record.actual_cost ? `$${record.actual_cost}` : 'TBD'}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Assets Tab */}
        <TabsContent value="assets" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {assets.map((asset) => (
              <Card key={asset.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{asset.name}</CardTitle>
                    <div className="flex space-x-2">
                      <Badge variant="outline">
                        {asset.asset_type}
                      </Badge>
                      {asset.is_tokenized && (
                        <Badge className="bg-purple-100 text-purple-800">
                          <Shield className="h-3 w-3 mr-1" />
                          NFT
                        </Badge>
                      )}
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {asset.description}
                  </p>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Purchase Price</p>
                      <p className="font-semibold">${asset.purchase_price}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Current Value</p>
                      <p className="font-semibold">${asset.current_value}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Location</p>
                      <p className="font-semibold text-xs">
                        {asset.location_name || 'Not assigned'}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Token ID</p>
                      <p className="font-semibold text-xs">
                        {asset.nft_token_id || 'Not tokenized'}
                      </p>
                    </div>
                  </div>
                  {asset.is_tokenized && (
                    <div className="flex items-center space-x-2">
                      <Shield className="h-4 w-4 text-purple-500" />
                      <span className="text-sm text-purple-600">
                        Tokenized on blockchain
                      </span>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default FacilityManagementDashboard;
