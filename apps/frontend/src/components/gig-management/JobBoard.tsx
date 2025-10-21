import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { MapPin, Clock, DollarSign, User, Search, Filter, Plus } from 'lucide-react';

interface GigJob {
  id: string;
  job_id: string;
  title: string;
  description: string;
  category_name: string;
  city_state: string;
  service_type: string;
  property_type: string;
  preferred_start_date: string;
  estimated_duration_hours: number;
  payment_method: string;
  hourly_rate?: number;
  fixed_price?: number;
  currency: string;
  total_cost: number;
  status: string;
  priority: string;
  client_name: string;
  created: string;
}

export const JobBoard: React.FC = () => {
  const [jobs, setJobs] = useState<GigJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    category: '',
    city: '',
    paymentMethod: '',
    status: 'published',
    maxRate: ''
  });

  useEffect(() => {
    fetchJobs();
  }, [filters]);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      
      if (searchQuery) params.append('search', searchQuery);
      if (filters.category) params.append('category', filters.category);
      if (filters.city) params.append('city', filters.city);
      if (filters.paymentMethod) params.append('payment_method', filters.paymentMethod);
      if (filters.status) params.append('status', filters.status);
      if (filters.maxRate) params.append('max_rate', filters.maxRate);

      const response = await fetch(`/api/v1/gig-management/jobs/?${params.toString()}`);
      const data = await response.json();
      setJobs(data.results || data);
    } catch (error) {
      console.error('Error fetching jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    fetchJobs();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published': return 'bg-blue-100 text-blue-800';
      case 'assigned': return 'bg-purple-100 text-purple-800';
      case 'in_progress': return 'bg-orange-100 text-orange-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Job Board</h1>
          <p className="text-gray-600">Find cleaning and maintenance jobs in your area</p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Post Job
        </Button>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="space-y-4">
            {/* Search Bar */}
            <div className="flex space-x-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search jobs by title, description, or location..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Button onClick={handleSearch}>Search</Button>
            </div>

            {/* Filters */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Category</label>
                <Select value={filters.category} onValueChange={(value) => setFilters({...filters, category: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Any Category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="residential_cleaning">Residential Cleaning</SelectItem>
                    <SelectItem value="commercial_cleaning">Commercial Cleaning</SelectItem>
                    <SelectItem value="deep_cleaning">Deep Cleaning</SelectItem>
                    <SelectItem value="maintenance">Maintenance</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="text-sm font-medium mb-2 block">City</label>
                <Input
                  placeholder="Enter city"
                  value={filters.city}
                  onChange={(e) => setFilters({...filters, city: e.target.value})}
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Payment Method</label>
                <Select value={filters.paymentMethod} onValueChange={(value) => setFilters({...filters, paymentMethod: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Any" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="hourly">Hourly</SelectItem>
                    <SelectItem value="fixed">Fixed Price</SelectItem>
                    <SelectItem value="performance">Performance Based</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Status</label>
                <Select value={filters.status} onValueChange={(value) => setFilters({...filters, status: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Any" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="published">Published</SelectItem>
                    <SelectItem value="assigned">Assigned</SelectItem>
                    <SelectItem value="in_progress">In Progress</SelectItem>
                    <SelectItem value="completed">Completed</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Max Rate</label>
                <Input
                  type="number"
                  placeholder="$100"
                  value={filters.maxRate}
                  onChange={(e) => setFilters({...filters, maxRate: e.target.value})}
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Job Listings */}
      {loading ? (
        <div className="flex justify-center p-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        </div>
      ) : (
        <div className="space-y-4">
          {jobs.map((job) => (
            <Card key={job.id} className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-xl font-semibold">{job.title}</h3>
                      <Badge className={getStatusColor(job.status)}>
                        {job.status.replace('_', ' ')}
                      </Badge>
                      <Badge variant="outline" className={getPriorityColor(job.priority)}>
                        {job.priority} priority
                      </Badge>
                    </div>
                    
                    <div className="flex items-center space-x-6 text-sm text-gray-600 mb-3">
                      <div className="flex items-center space-x-1">
                        <User className="h-4 w-4" />
                        <span>{job.client_name}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <MapPin className="h-4 w-4" />
                        <span>{job.city_state}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <span className="font-medium">{job.category_name}</span>
                      </div>
                    </div>

                    <p className="text-gray-700 mb-4 line-clamp-2">
                      {job.description}
                    </p>
                  </div>
                </div>

                <div className="flex justify-between items-end">
                  <div className="flex items-center space-x-6 text-sm">
                    <div className="flex items-center space-x-1">
                      <DollarSign className="h-4 w-4 text-green-600" />
                      <span className="font-medium">${job.total_cost}</span>
                      <span className="text-gray-500">
                        {job.payment_method === 'hourly' ? '/hour' : ' fixed'}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-1">
                      <Clock className="h-4 w-4 text-blue-600" />
                      <span>{job.estimated_duration_hours}h estimated</span>
                    </div>
                    
                    <div>
                      <span className="text-gray-500">Posted </span>
                      <span>{formatDate(job.created)}</span>
                    </div>
                  </div>

                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm">View Details</Button>
                    <Button size="sm">Apply Now</Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {!loading && jobs.length === 0 && (
        <Card>
          <CardContent className="p-12 text-center">
            <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs found</h3>
            <p className="text-gray-600">Try adjusting your search criteria or check back later.</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default JobBoard;
