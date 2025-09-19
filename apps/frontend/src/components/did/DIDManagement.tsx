/**
 * DID Management Component
 * 
 * Provides UI for managing Decentralized Identities (DIDs), roles, and permissions.
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Plus, Trash2, Shield, Key, Users, CheckCircle, XCircle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface DIDDocument {
  id: number;
  did: string;
  status: 'active' | 'deactivated' | 'revoked';
  created_at: string;
  updated_at: string;
  on_chain_registry_status?: string;
  user?: {
    username: string;
    email: string;
  };
}

interface DIDRole {
  id: number;
  role_name: string;
  custom_role_name?: string;
  is_active: boolean;
  granted_at: string;
  expires_at?: string;
  permissions: string[];
  did: {
    did: string;
  };
}

interface DIDPermission {
  id: number;
  name: string;
  display_name: string;
  description: string;
  category: string;
  resource: string;
  action: string;
  is_active: boolean;
}

const DIDManagement: React.FC = () => {
  const [dids, setDids] = useState<DIDDocument[]>([]);
  const [roles, setRoles] = useState<DIDRole[]>([]);
  const [permissions, setPermissions] = useState<DIDPermission[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedDid, setSelectedDid] = useState<string>('');
  const [newRole, setNewRole] = useState({
    role_name: '',
    custom_role_name: '',
    permissions: [] as string[],
    expires_at: ''
  });
  const { toast } = useToast();

  // Fetch DID documents
  const fetchDIDs = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/did-auth/documents/');
      if (response.ok) {
        const data = await response.json();
        setDids(data.results || data);
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch DID documents",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  // Fetch DID roles
  const fetchRoles = async () => {
    try {
      const response = await fetch('/api/v1/did-auth/roles/');
      if (response.ok) {
        const data = await response.json();
        setRoles(data.results || data);
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch DID roles",
        variant: "destructive",
      });
    }
  };

  // Fetch permissions
  const fetchPermissions = async () => {
    try {
      const response = await fetch('/api/v1/did-auth/permissions/');
      if (response.ok) {
        const data = await response.json();
        setPermissions(data.results || data);
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch permissions",
        variant: "destructive",
      });
    }
  };

  // Assign role to DID
  const assignRole = async () => {
    if (!selectedDid || !newRole.role_name) {
      toast({
        title: "Error",
        description: "Please select a DID and role",
        variant: "destructive",
      });
      return;
    }

    try {
      setLoading(true);
      const response = await fetch('/api/v1/did-auth/roles/assign-role/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          did: selectedDid,
          role_name: newRole.role_name,
          custom_role_name: newRole.custom_role_name || undefined,
          permissions: newRole.permissions,
          expires_at: newRole.expires_at || undefined,
        }),
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "Role assigned successfully",
        });
        setNewRole({
          role_name: '',
          custom_role_name: '',
          permissions: [],
          expires_at: ''
        });
        fetchRoles();
      } else {
        const error = await response.json();
        toast({
          title: "Error",
          description: error.error || "Failed to assign role",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to assign role",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  // Sync DID to registry
  const syncToRegistry = async (didId: number) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/did-auth/documents/${didId}/sync-to-registry/`, {
        method: 'POST',
      });

      if (response.ok) {
        const result = await response.json();
        toast({
          title: "Success",
          description: `DID synced to registry. TX: ${result.tx_hash}`,
        });
        fetchDIDs();
      } else {
        const error = await response.json();
        toast({
          title: "Error",
          description: error.error || "Failed to sync to registry",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to sync to registry",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  // Get registry status
  const getRegistryStatus = async (did: string) => {
    try {
      const response = await fetch(`/api/v1/did-auth/documents/registry-status/?did=${encodeURIComponent(did)}`);
      if (response.ok) {
        const result = await response.json();
        return result.status;
      }
    } catch (error) {
      console.error('Failed to get registry status:', error);
    }
    return 'unknown';
  };

  useEffect(() => {
    fetchDIDs();
    fetchRoles();
    fetchPermissions();
  }, []);

  const getStatusBadge = (status: string) => {
    const variants = {
      active: 'default',
      deactivated: 'secondary',
      revoked: 'destructive',
      registered: 'default',
      not_registered: 'secondary',
      unknown: 'outline'
    } as const;

    return (
      <Badge variant={variants[status as keyof typeof variants] || 'outline'}>
        {status}
      </Badge>
    );
  };

  const getRoleIcon = (roleName: string) => {
    const icons = {
      admin: Shield,
      finance_manager: Key,
      hr_manager: Users,
      auditor: Shield,
      field_supervisor: Users,
      cleaner: Users,
      client: Users,
      supplier: Users,
      custom: Shield
    };
    const Icon = icons[roleName as keyof typeof icons] || Shield;
    return <Icon className="h-4 w-4" />;
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">DID Management</h1>
          <p className="text-muted-foreground">
            Manage Decentralized Identities, roles, and permissions
          </p>
        </div>
      </div>

      <Tabs defaultValue="dids" className="space-y-4">
        <TabsList>
          <TabsTrigger value="dids">DID Documents</TabsTrigger>
          <TabsTrigger value="roles">Roles & Permissions</TabsTrigger>
          <TabsTrigger value="assign">Assign Roles</TabsTrigger>
        </TabsList>

        <TabsContent value="dids" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>DID Documents</CardTitle>
              <CardDescription>
                Manage Decentralized Identity documents and their registry status
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex items-center justify-center p-8">
                  <Loader2 className="h-8 w-8 animate-spin" />
                </div>
              ) : (
                <div className="space-y-4">
                  {dids.map((did) => (
                    <div key={did.id} className="border rounded-lg p-4 space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="space-y-1">
                          <div className="font-mono text-sm">{did.did}</div>
                          <div className="flex items-center gap-2">
                            {getStatusBadge(did.status)}
                            {did.on_chain_registry_status && getStatusBadge(did.on_chain_registry_status)}
                          </div>
                          {did.user && (
                            <div className="text-sm text-muted-foreground">
                              User: {did.user.username} ({did.user.email})
                            </div>
                          )}
                        </div>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => syncToRegistry(did.id)}
                            disabled={loading}
                          >
                            Sync to Registry
                          </Button>
                        </div>
                      </div>
                      <div className="text-xs text-muted-foreground">
                        Created: {new Date(did.created_at).toLocaleString()}
                      </div>
                    </div>
                  ))}
                  {dids.length === 0 && (
                    <Alert>
                      <AlertDescription>
                        No DID documents found. Create some DIDs first.
                      </AlertDescription>
                    </Alert>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="roles" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>DID Roles & Permissions</CardTitle>
              <CardDescription>
                View and manage roles assigned to DIDs
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {roles.map((role) => (
                  <div key={role.id} className="border rounded-lg p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {getRoleIcon(role.role_name)}
                        <span className="font-medium">
                          {role.role_name === 'custom' ? role.custom_role_name : role.role_name}
                        </span>
                        <Badge variant={role.is_active ? 'default' : 'secondary'}>
                          {role.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {role.did.did}
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {role.permissions.map((permission) => (
                        <Badge key={permission} variant="outline" className="text-xs">
                          {permission}
                        </Badge>
                      ))}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Granted: {new Date(role.granted_at).toLocaleString()}
                      {role.expires_at && (
                        <span> • Expires: {new Date(role.expires_at).toLocaleString()}</span>
                      )}
                    </div>
                  </div>
                ))}
                {roles.length === 0 && (
                  <Alert>
                    <AlertDescription>
                      No roles assigned yet. Assign roles to DIDs to get started.
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="assign" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Assign Role to DID</CardTitle>
              <CardDescription>
                Assign roles and permissions to existing DIDs
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="did-select">Select DID</Label>
                <Select value={selectedDid} onValueChange={setSelectedDid}>
                  <SelectTrigger>
                    <SelectValue placeholder="Choose a DID" />
                  </SelectTrigger>
                  <SelectContent>
                    {dids.map((did) => (
                      <SelectItem key={did.id} value={did.did}>
                        {did.did}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="role-name">Role Name</Label>
                <Select value={newRole.role_name} onValueChange={(value) => setNewRole({...newRole, role_name: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Choose a role" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="admin">Administrator</SelectItem>
                    <SelectItem value="finance_manager">Finance Manager</SelectItem>
                    <SelectItem value="hr_manager">HR Manager</SelectItem>
                    <SelectItem value="auditor">Auditor</SelectItem>
                    <SelectItem value="field_supervisor">Field Supervisor</SelectItem>
                    <SelectItem value="cleaner">Cleaner</SelectItem>
                    <SelectItem value="client">Client</SelectItem>
                    <SelectItem value="supplier">Supplier</SelectItem>
                    <SelectItem value="custom">Custom Role</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {newRole.role_name === 'custom' && (
                <div className="space-y-2">
                  <Label htmlFor="custom-role-name">Custom Role Name</Label>
                  <Input
                    id="custom-role-name"
                    value={newRole.custom_role_name}
                    onChange={(e) => setNewRole({...newRole, custom_role_name: e.target.value})}
                    placeholder="Enter custom role name"
                  />
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="permissions">Permissions</Label>
                <div className="grid grid-cols-2 gap-2 max-h-32 overflow-y-auto">
                  {permissions.map((permission) => (
                    <div key={permission.id} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id={`permission-${permission.id}`}
                        checked={newRole.permissions.includes(permission.name)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setNewRole({
                              ...newRole,
                              permissions: [...newRole.permissions, permission.name]
                            });
                          } else {
                            setNewRole({
                              ...newRole,
                              permissions: newRole.permissions.filter(p => p !== permission.name)
                            });
                          }
                        }}
                      />
                      <Label htmlFor={`permission-${permission.id}`} className="text-sm">
                        {permission.display_name}
                      </Label>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="expires-at">Expires At (Optional)</Label>
                <Input
                  id="expires-at"
                  type="datetime-local"
                  value={newRole.expires_at}
                  onChange={(e) => setNewRole({...newRole, expires_at: e.target.value})}
                />
              </div>

              <Button onClick={assignRole} disabled={loading || !selectedDid || !newRole.role_name}>
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Assign Role
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default DIDManagement;
