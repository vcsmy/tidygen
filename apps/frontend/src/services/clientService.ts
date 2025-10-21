/**
 * Client service for managing customers and client relationships
 */

import { apiClient } from '@/services/api';

export interface Client {
  id: number;
  display_name?: string;
  contact_person?: string;
  email?: string;
  phone?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  client_type: 'individual' | 'corporate';
  status: 'active' | 'inactive' | 'prospect' | 'suspended';
  priority?: string;
  preferred_contact_method?: 'email' | 'phone' | 'sms' | 'whatsapp';
  notes?: string;
  created: string;
  modified: string;
  full_address?: string;
  // Legacy fields for backwards compatibility
  name?: string;
  address?: string;
  zip_code?: string;
  updated?: string;
  company_name?: string;
  service_frequency?: string;
  last_service_date?: string;
  next_service_date?: string;
  total_services?: number;
  total_revenue?: number;
  organization?: number;
}

export interface ServiceRequest {
  id: number;
  client: number;
  client_name?: string;
  service_type: string;
  description: string;
  scheduled_date: string;
  estimated_duration: number;
  status: 'pending' | 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  assigned_team?: string;
  estimated_cost: number;
  actual_cost?: number;
  notes: string;
  created: string;
  updated: string;
}

export interface ClientNote {
  id: number;
  client: number;
  title: string;
  content: string;
  note_type: 'general' | 'service' | 'billing' | 'complaint' | 'compliment';
  created_by: number;
  created_by_name?: string;
  created: string;
}

export interface ClientSummary {
  total_clients: number;
  active_clients: number;
  new_clients_this_month: number;
  total_revenue: number;
  average_service_frequency: string;
  top_service_types: Array<{
    service_type: string;
    count: number;
  }>;
}

class ClientService {
  // Clients
  async getClients(params?: {
    search?: string;
    status?: string;
    client_type?: string;
    ordering?: string;
    page?: number;
    page_size?: number;
  }) {
    const response = await apiClient.get('/sales/clients/', { params });
    return response.data;
  }

  async getClient(id: number) {
    const response = await apiClient.get(`/sales/clients/${id}/`);
    return response.data;
  }

  async createClient(data: Partial<Client>) {
    const response = await apiClient.post('/sales/clients/', data);
    return response.data;
  }

  async updateClient(id: number, data: Partial<Client>) {
    const response = await apiClient.patch(`/sales/clients/${id}/`, data);
    return response.data;
  }

  async deleteClient(id: number) {
    const response = await apiClient.delete(`/sales/clients/${id}/`);
    return response.data;
  }

  // Service Requests
  async getServiceRequests(params?: {
    client?: number;
    status?: string;
    search?: string;
    ordering?: string;
    page?: number;
    page_size?: number;
  }) {
    // Mock implementation
    const mockRequests: ServiceRequest[] = [
      {
        id: 1,
        client: 1,
        client_name: "John Smith",
        service_type: "Deep Cleaning",
        description: "Full house deep cleaning",
        scheduled_date: "2024-01-25T09:00:00Z",
        estimated_duration: 4,
        status: "scheduled",
        priority: "medium",
        assigned_team: "Team A",
        estimated_cost: 200.00,
        notes: "Focus on kitchen and bathrooms",
        created: "2024-01-20T10:00:00Z",
        updated: "2024-01-20T10:00:00Z",
      },
    ];

    return { data: mockRequests };
  }

  async createServiceRequest(data: Partial<ServiceRequest>) {
    // Mock implementation
    const newRequest: ServiceRequest = {
      id: Date.now(),
      client: data.client || 0,
      service_type: data.service_type || "",
      description: data.description || "",
      scheduled_date: data.scheduled_date || "",
      estimated_duration: data.estimated_duration || 2,
      status: data.status || "pending",
      priority: data.priority || "medium",
      assigned_team: data.assigned_team,
      estimated_cost: data.estimated_cost || 0,
      actual_cost: data.actual_cost,
      notes: data.notes || "",
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
    };

    return { data: newRequest };
  }

  async updateServiceRequest(id: number, data: Partial<ServiceRequest>) {
    // Mock implementation
    return { data: { ...data, id, updated: new Date().toISOString() } };
  }

  // Client Notes
  async getClientNotes(clientId: number) {
    const response = await apiClient.get(`/sales/clients/${clientId}/notes/`);
    return response.data;
  }

  async createClientNote(data: Partial<ClientNote>) {
    const response = await apiClient.post(`/sales/clients/${data.client}/notes/`, data);
    return response.data;
  }

  // Dashboard/Summary
  async getClientSummary() {
    // Return mock summary for now - can be connected to a real analytics endpoint later
    const summary: ClientSummary = {
      total_clients: 0,
      active_clients: 0,
      new_clients_this_month: 0,
      total_revenue: 0,
      average_service_frequency: "monthly",
      top_service_types: [],
    };

    return { data: summary };
  }
}

export const clientService = new ClientService();
