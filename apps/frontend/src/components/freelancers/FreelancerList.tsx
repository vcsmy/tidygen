import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { MapPin, Star, Clock, DollarSign, Filter, Search } from 'lucide-react';

interface Freelancer {
  id: string;
  freelancer_id: string;
  full_name: string;
  city_state: string;
  rating: number;
  total_jobs_completed: number;
  cleaning_types: string[];
  hourly_rate: number;
  currency: string;
  is_available: boolean;
  status: string;
  profile_picture?: string;
}

export const FreelancerList: React.FC = () => {
  const [freelancers, setFreelancers] = useState<Freelancer[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    city: '',
    minRating: '',
    maxRate: '',
    cleaningType: '',
    status: ''
  });

  useEffect(() => {
    fetchFreelancers();
  }, [filters]);

  const fetchFreelancers = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      
      if (searchQuery) params.append('search', searchQuery);
      if (filters.city) params.append('city', filters.city);
      if (filters.minRating) params.append('min_rating', filters.minRating);
      if (filters.maxRate) params.append('max_rate', filters.maxRate);
      if (filters.cleaningType) params.append('cleaning_types', filters.cleaningType);
      if (filters.status) params.append('status', filters.status);

      const response = await fetch(`/api/v1/freelancers/?${params.toString()}`);
      const data = await response.json();
      setFreelancers(data.results || data);
    } catch (error) {
      console.error('Error fetching freelancers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    fetchFreelancers();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'pending_verification': return 'bg-yellow-100 text-yellow-800';
      case 'inactive': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Find Freelancers</h1>
          <p className="text-gray-600">Browse available domestic cleaners and contractors</p>
        </div>
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
                  placeholder="Search by name, skills, or location..."
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
                <label className="text-sm font-medium mb-2 block">City</label>
                <Input
                  placeholder="Enter city"
                  value={filters.city}
                  onChange={(e) => setFilters({...filters, city: e.target.value})}
                />
              </div>
              
              <div>
                <label className="text-sm font-medium mb-2 block">Min Rating</label>
                <Select value={filters.minRating} onValueChange={(value) => setFilters({...filters, minRating: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Any" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">1+ Stars</SelectItem>
                    <SelectItem value="2">2+ Stars</SelectItem>
                    <SelectItem value="3">3+ Stars</SelectItem>
                    <SelectItem value="4">4+ Stars</SelectItem>
                    <SelectItem value="5">5 Stars</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Max Rate</label>
                <Input
                  type="number"
                  placeholder="$50"
                  value={filters.maxRate}
                  onChange={(e) => setFilters({...filters, maxRate: e.target.value})}
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Service Type</label>
                <Select value={filters.cleaningType} onValueChange={(value) => setFilters({...filters, cleaningType: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Any" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="residential">Residential</SelectItem>
                    <SelectItem value="commercial">Commercial</SelectItem>
                    <SelectItem value="deep_cleaning">Deep Cleaning</SelectItem>
                    <SelectItem value="maintenance">Maintenance</SelectItem>
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
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="available">Available</SelectItem>
                    <SelectItem value="verified">Verified</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      {loading ? (
        <div className="flex justify-center p-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {freelancers.map((freelancer) => (
            <Card key={freelancer.id} className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start space-x-4 mb-4">
                  <Avatar className="h-16 w-16">
                    <AvatarImage src={freelancer.profile_picture} />
                    <AvatarFallback>
                      {freelancer.full_name?.split(' ').map(n => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                  
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <h3 className="font-semibold">{freelancer.full_name}</h3>
                      <Badge className={getStatusColor(freelancer.status)} size="sm">
                        {freelancer.status.replace('_', ' ')}
                      </Badge>
                    </div>
                    
                    <div className="flex items-center space-x-1 text-sm text-gray-600 mb-2">
                      <MapPin className="h-3 w-3" />
                      <span>{freelancer.city_state}</span>
                    </div>

                    <div className="flex items-center space-x-1 mb-2">
                      <Star className="h-4 w-4 text-yellow-500" />
                      <span className="font-medium">{freelancer.rating}</span>
                      <span className="text-sm text-gray-500">
                        ({freelancer.total_jobs_completed} jobs)
                      </span>
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center space-x-4 text-sm">
                    <div className="flex items-center space-x-1">
                      <DollarSign className="h-4 w-4 text-green-600" />
                      <span className="font-medium">${freelancer.hourly_rate}</span>
                      <span className="text-gray-500">/{freelancer.currency}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Clock className="h-4 w-4 text-blue-600" />
                      <span className={freelancer.is_available ? 'text-green-600' : 'text-red-600'}>
                        {freelancer.is_available ? 'Available' : 'Busy'}
                      </span>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-1">
                    {freelancer.cleaning_types?.slice(0, 3).map((type, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {type.replace('_', ' ')}
                      </Badge>
                    ))}
                    {freelancer.cleaning_types?.length > 3 && (
                      <Badge variant="outline" className="text-xs">
                        +{freelancer.cleaning_types.length - 3} more
                      </Badge>
                    )}
                  </div>

                  <div className="flex space-x-2 pt-3">
                    <Button size="sm" className="flex-1">View Profile</Button>
                    <Button size="sm" variant="outline">Contact</Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {!loading && freelancers.length === 0 && (
        <Card>
          <CardContent className="p-12 text-center">
            <h3 className="text-lg font-medium text-gray-900 mb-2">No freelancers found</h3>
            <p className="text-gray-600">Try adjusting your search criteria or filters.</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default FreelancerList;
