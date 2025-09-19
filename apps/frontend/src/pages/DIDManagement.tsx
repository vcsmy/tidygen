/**
 * DID Management Page
 * 
 * Main page for managing Decentralized Identities in TidyGen ERP.
 */

import React from 'react';
import { Helmet } from 'react-helmet-async';
import DIDManagement from '@/components/did/DIDManagement';
import DIDAuth from '@/components/did/DIDAuth';

const DIDManagementPage: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>DID Management - TidyGen ERP</title>
        <meta name="description" content="Manage Decentralized Identities, roles, and permissions in TidyGen ERP" />
      </Helmet>
      
      <div className="min-h-screen bg-background">
        <div className="container mx-auto py-8 space-y-8">
          <div className="text-center space-y-2">
            <h1 className="text-4xl font-bold tracking-tight">DID Management</h1>
            <p className="text-xl text-muted-foreground">
              Decentralized Identity and Access Control System
            </p>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div>
              <DIDAuth />
            </div>
            <div>
              <DIDManagement />
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default DIDManagementPage;
