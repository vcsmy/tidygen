import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import FreelancerList from '@/components/freelancers/FreelancerList';
import FreelancerProfile from '@/components/freelancers/FreelancerProfile';
import JobBoard from '@/components/gig-management/JobBoard';

export const FreelancerManagement: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Freelancer & Gig Management
          </h1>
          <p className="text-gray-600">
            Manage individual contractors, browse jobs, and handle the freelance ecosystem
          </p>
        </div>

        <Tabs defaultValue="freelancers" className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-6">
            <TabsTrigger value="freelancers">Find Freelancers</TabsTrigger>
            <TabsTrigger value="jobs">Job Board</TabsTrigger>
            <TabsTrigger value="profile">My Profile</TabsTrigger>
          </TabsList>

          <TabsContent value="freelancers" className="space-y-6">
            <FreelancerList />
          </TabsContent>

          <TabsContent value="jobs" className="space-y-6">
            <JobBoard />
          </TabsContent>

          <TabsContent value="profile" className="space-y-6">
            <FreelancerProfile />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default FreelancerManagement;
