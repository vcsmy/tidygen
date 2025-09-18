import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Truck, 
  Users, 
  MapPin, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  TrendingUp,
  Calendar,
  Wrench,
  Route
} from 'lucide-react';

interface FieldTeam {
  id: number;
  name: string;
  team_type: string;
  status: string;
  max_capacity: number;
  current_capacity: number;
  total_jobs_completed: number;
  average_rating: number;
  on_time_percentage: number;
  assigned_vehicle_name?: string;
  home_base_name?: string;
}

interface ServiceRoute {
  id: number;
  name: string;
  route_type: string;
  status: string;
  scheduled_date: string;
  start_time: string;
  total_stops: number;
  completed_stops: number;
  efficiency_rating: number;
  assigned_team_name?: string;
}

interface FieldJob {
  id: number;
  job_number: string;
  title: string;
  job_type: string;
  priority: string;
  status: string;
  client_name?: string;
  assigned_team_name?: string;
  scheduled_date: string;
  scheduled_start_time: string;
  estimated_cost: number;
  payment_released: boolean;
}

interface DashboardSummary {
  total_teams: number;
  active_teams: number;
  total_members: number;
  team_types: Array<{ team_type: string; count: number }>;
  status_distribution: Array<{ status: string; count: number }>;
}

const FieldOperationsDashboard: React.FC = () => {
  const [teams, setTeams] = useState<FieldTeam[]>([]);
  const [routes, setRoutes] = useState<ServiceRoute[]>([]);
  const [jobs, setJobs] = useState<FieldJob[]>([]);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch teams
      const teamsResponse = await fetch('/api/v1/field-operations/teams/');
      if (teamsResponse.ok) {
        const teamsData = await teamsResponse.json();
        setTeams(teamsData.results || teamsData);
      }

      // Fetch routes
      const routesResponse = await fetch('/api/v1/field-operations/routes/');
      if (routesResponse.ok) {
        const routesData = await routesResponse.json();
        setRoutes(routesData.results || routesData);
      }

      // Fetch jobs
      const jobsResponse = await fetch('/api/v1/field-operations/jobs/');
      if (jobsResponse.ok) {
        const jobsData = await jobsResponse.json();
        setJobs(jobsData.results || jobsData);
      }

      // Fetch dashboard summary
      const summaryResponse = await fetch('/api/v1/field-operations/teams/dashboard-summary/');
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
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      case 'scheduled':
      case 'planned':
        return 'bg-yellow-100 text-yellow-800';
      case 'urgent':
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading Field Operations Dashboard...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Field Operations Dashboard</h1>
        <Button onClick={fetchDashboardData} variant="outline">
          Refresh Data
        </Button>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Teams</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary.total_teams}</div>
              <p className="text-xs text-muted-foreground">
                {summary.active_teams} active teams
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Team Members</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary.total_members}</div>
              <p className="text-xs text-muted-foreground">
                Active field personnel
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Routes</CardTitle>
              <Route className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {routes.filter(r => r.status === 'active').length}
              </div>
              <p className="text-xs text-muted-foreground">
                Currently in progress
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Jobs Today</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {jobs.filter(j => j.scheduled_date === new Date().toISOString().split('T')[0]).length}
              </div>
              <p className="text-xs text-muted-foreground">
                Scheduled for today
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content Tabs */}
      <Tabs defaultValue="teams" className="space-y-4">
        <TabsList>
          <TabsTrigger value="teams">Field Teams</TabsTrigger>
          <TabsTrigger value="routes">Service Routes</TabsTrigger>
          <TabsTrigger value="jobs">Field Jobs</TabsTrigger>
        </TabsList>

        {/* Field Teams Tab */}
        <TabsContent value="teams" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {teams.map((team) => (
              <Card key={team.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{team.name}</CardTitle>
                    <Badge className={getStatusColor(team.status)}>
                      {team.status}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {team.team_type} • {team.current_capacity}/{team.max_capacity} members
                  </p>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Jobs Completed</p>
                      <p className="font-semibold">{team.total_jobs_completed}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Rating</p>
                      <p className="font-semibold">{team.average_rating}/5.0</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">On-Time %</p>
                      <p className="font-semibold">{team.on_time_percentage}%</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Vehicle</p>
                      <p className="font-semibold text-xs">
                        {team.assigned_vehicle_name || 'Not assigned'}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <TrendingUp className="h-4 w-4 text-green-500" />
                    <span className="text-sm text-green-600">
                      High performance team
                    </span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Service Routes Tab */}
        <TabsContent value="routes" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {routes.map((route) => (
              <Card key={route.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{route.name}</CardTitle>
                    <Badge className={getStatusColor(route.status)}>
                      {route.status}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {route.route_type} • {route.assigned_team_name}
                  </p>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Scheduled Date</p>
                      <p className="font-semibold">
                        {new Date(route.scheduled_date).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Start Time</p>
                      <p className="font-semibold">{route.start_time}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Progress</p>
                      <p className="font-semibold">
                        {route.completed_stops}/{route.total_stops} stops
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Efficiency</p>
                      <p className="font-semibold">{route.efficiency_rating}/5.0</p>
                    </div>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full" 
                      style={{ 
                        width: `${(route.completed_stops / route.total_stops) * 100}%` 
                      }}
                    ></div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Field Jobs Tab */}
        <TabsContent value="jobs" className="space-y-4">
          <div className="space-y-4">
            {jobs.map((job) => (
              <Card key={job.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg">{job.title}</CardTitle>
                      <p className="text-sm text-muted-foreground">
                        {job.job_number} • {job.client_name}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge className={getPriorityColor(job.priority)}>
                        {job.priority}
                      </Badge>
                      <Badge className={getStatusColor(job.status)}>
                        {job.status}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Job Type</p>
                      <p className="font-semibold">{job.job_type}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Assigned Team</p>
                      <p className="font-semibold">
                        {job.assigned_team_name || 'Unassigned'}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Scheduled</p>
                      <p className="font-semibold">
                        {new Date(job.scheduled_date).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Cost</p>
                      <p className="font-semibold">${job.estimated_cost}</p>
                    </div>
                  </div>
                  <div className="flex items-center justify-between mt-4">
                    <div className="flex items-center space-x-2">
                      {job.payment_released ? (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      ) : (
                        <Clock className="h-4 w-4 text-yellow-500" />
                      )}
                      <span className="text-sm">
                        {job.payment_released ? 'Payment Released' : 'Payment Pending'}
                      </span>
                    </div>
                    <Button variant="outline" size="sm">
                      View Details
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default FieldOperationsDashboard;
