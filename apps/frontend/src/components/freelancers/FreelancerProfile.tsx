import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { MapPin, Star, Clock, DollarSign, Shield, Globe, Award } from 'lucide-react';

interface FreelancerProfileProps {
  freelancerId?: string;
}

interface Freelancer {
  id: string;
  freelancer_id: string;
  first_name: string;
  last_name: string;
  city: string;
  state: string;
  rating: number;
  total_jobs_completed: number;
  on_time_percentage: number;
  completion_rate: number;
  hourly_rate: number;
  currency: string;
  cleaning_types: string[];
  special_skills: string;
  years_of_experience: number;
  profile_picture?: string;
  wallet_address?: string;
  blockchain_verified: boolean;
  status: string;
  bio: string;
  documents: any[];
  availability_slots: any[];
  skill_assignments: any[];
  reviews: any[];
}

export const FreelancerProfile: React.FC<FreelancerProfileProps> = ({ freelancerId }) => {
  const [freelancer, setFreelancer] = useState<Freelancer | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (freelancerId) {
      fetchFreelancerProfile(freelancerId);
    } else {
      fetchMyProfile();
    }
  }, [freelancerId]);

  const fetchFreelancerProfile = async (id: string) => {
    try {
      // API call to fetch freelancer profile
      const response = await fetch(`/api/v1/freelancers/${id}/`);
      const data = await response.json();
      setFreelancer(data);
    } catch (error) {
      console.error('Error fetching freelancer profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMyProfile = async () => {
    try {
      // API call to fetch current user's freelancer profile
      const response = await fetch('/api/v1/freelancers/me/');
      const data = await response.json();
      setFreelancer(data);
    } catch (error) {
      console.error('Error fetching my profile:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex justify-center p-8">Loading...</div>;
  }

  if (!freelancer) {
    return <div className="text-center p-8">Freelancer profile not found.</div>;
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'pending_verification': return 'bg-yellow-100 text-yellow-800';
      case 'inactive': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header Card */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-start space-x-6">
            <Avatar className="h-24 w-24">
              <AvatarImage src={freelancer.profile_picture} />
              <AvatarFallback>
                {freelancer.first_name?.[0]}{freelancer.last_name?.[0]}
              </AvatarFallback>
            </Avatar>
            
            <div className="flex-1">
              <div className="flex items-center space-x-4 mb-2">
                <h1 className="text-3xl font-bold">
                  {freelancer.first_name} {freelancer.last_name}
                </h1>
                <Badge className={getStatusColor(freelancer.status)}>
                  {freelancer.status.replace('_', ' ')}
                </Badge>
                {freelancer.blockchain_verified && (
                  <Badge variant="secondary" className="flex items-center space-x-1">
                    <Shield className="h-3 w-3" />
                    <span>Verified</span>
                  </Badge>
                )}
              </div>
              
              <div className="flex items-center space-x-6 text-sm text-gray-600 mb-4">
                <div className="flex items-center space-x-1">
                  <MapPin className="h-4 w-4" />
                  <span>{freelancer.city}, {freelancer.state}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <DollarSign className="h-4 w-4" />
                  <span>${freelancer.hourly_rate}/{freelancer.currency}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Clock className="h-4 w-4" />
                  <span>{freelancer.years_of_experience} years experience</span>
                </div>
              </div>

              <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-1">
                  <Star className="h-4 w-4 text-yellow-500" />
                  <span className="font-medium">{freelancer.rating}</span>
                  <span className="text-sm text-gray-500">({freelancer.reviews?.length || 0} reviews)</span>
                </div>
                <div>
                  <span className="font-medium">{freelancer.total_jobs_completed}</span>
                  <span className="text-sm text-gray-500"> jobs completed</span>
                </div>
                <div>
                  <span className="font-medium">{freelancer.on_time_percentage}%</span>
                  <span className="text-sm text-gray-500"> on time</span>
                </div>
                <div>
                  <span className="font-medium">{freelancer.completion_rate}%</span>
                  <span className="text-sm text-gray-500"> completion rate</span>
                </div>
              </div>
            </div>

            <div className="flex flex-col space-y-2">
              <Button>Contact</Button>
              <Button variant="outline">View Reviews</Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Content */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="skills">Skills</TabsTrigger>
          <TabsTrigger value="availability">Availability</TabsTrigger>
          <TabsTrigger value="reviews">Reviews</TabsTrigger>
          <TabsTrigger value="web3">Web3</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* About */}
            <Card>
              <CardHeader>
                <CardTitle>About</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700">{freelancer.bio || 'No bio available.'}</p>
                
                <Separator className="my-4" />
                
                <div>
                  <h4 className="font-medium mb-2">Services</h4>
                  <div className="flex flex-wrap gap-2">
                    {freelancer.cleaning_types?.map((type, index) => (
                      <Badge key={index} variant="outline">
                        {type.replace('_', ' ')}
                      </Badge>
                    ))}
                  </div>
                </div>

                {freelancer.special_skills && (
                  <>
                    <Separator className="my-4" />
                    <div>
                      <h4 className="font-medium mb-2">Special Skills</h4>
                      <p className="text-gray-700">{freelancer.special_skills}</p>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>

            {/* Contact & Web3 */}
            <Card>
              <CardHeader>
                <CardTitle>Contact & Web3</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {freelancer.wallet_address && (
                  <div className="flex items-center space-x-2">
                    <Globe className="h-4 w-4" />
                    <span className="text-sm font-medium">Wallet:</span>
                    <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                      {freelancer.wallet_address.slice(0, 10)}...{freelancer.wallet_address.slice(-8)}
                    </code>
                  </div>
                )}
                
                <div className="flex items-center space-x-2">
                  <Award className="h-4 w-4" />
                  <span className="text-sm font-medium">ID:</span>
                  <span className="text-sm">{freelancer.freelancer_id}</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="skills" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Skills & Certifications</CardTitle>
            </CardHeader>
            <CardContent>
              {freelancer.skill_assignments?.length ? (
                <div className="space-y-4">
                  {freelancer.skill_assignments.map((skill, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-medium">{skill.skill?.name}</h4>
                        <Badge variant="outline">{skill.proficiency_level}</Badge>
                      </div>
                      <div className="text-sm text-gray-600">
                        {skill.years_of_experience} years experience
                      </div>
                      {skill.certification_body && (
                        <div className="text-sm text-gray-600 mt-1">
                          Certified by: {skill.certification_body}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No skills listed.</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="availability" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Availability Schedule</CardTitle>
            </CardHeader>
            <CardContent>
              {freelancer.availability_slots?.length ? (
                <div className="space-y-4">
                  {/* Availability display logic would go here */}
                  <p className="text-gray-500">Availability details would be displayed here.</p>
                </div>
              ) : (
                <p className="text-gray-500">No availability schedule set.</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reviews" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Client Reviews</CardTitle>
            </CardHeader>
            <CardContent>
              {freelancer.reviews?.length ? (
                <div className="space-y-4">
                  {freelancer.reviews.map((review, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-center space-x-4 mb-2">
                        <div className="flex items-center space-x-1">
                          {[...Array(5)].map((_, i) => (
                            <Star
                              key={i}
                              className={`h-4 w-4 ${
                                i < review.overall_rating ? 'text-yellow-500' : 'text-gray-300'
                              }`}
                              fill={i < review.overall_rating ? 'currentColor' : 'none'}
                            />
                          ))}
                        </div>
                        <span className="font-medium">{review.reviewer_name}</span>
                      </div>
                      <h4 className="font-medium mb-1">{review.title}</h4>
                      <p className="text-gray-700">{review.comment}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No reviews yet.</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="web3" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Web3 Integration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center space-x-2">
                <Shield className="h-4 w-4" />
                <span className="font-medium">Blockchain Verification:</span>
                <Badge variant={freelancer.blockchain_verified ? "default" : "secondary"}>
                  {freelancer.blockchain_verified ? "Verified" : "Not Verified"}
                </Badge>
              </div>
              
              {freelancer.wallet_address && (
                <div>
                  <span className="font-medium">Wallet Address:</span>
                  <div className="mt-1 p-2 bg-gray-100 rounded text-sm font-mono">
                    {freelancer.wallet_address}
                  </div>
                </div>
              )}
              
              {/* NFT badges and other Web3 features would be displayed here */}
              <div className="text-sm text-gray-600">
                Web3 features like NFT badges, smart contracts, and reputation tokens would be shown here.
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default FreelancerProfile;
