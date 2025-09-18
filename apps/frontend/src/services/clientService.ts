/**
 * Client service for managing customers and client relationships
 */

import { apiClient } from '@/services/api';

export interface Client {
  id: number;
  name: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  country: string;
  contact_person: string;
  company_name?: string;
  client_type: 'individual' | 'business' | 'residential' | 'commercial';
  status: 'active' | 'inactive' | 'prospect' | 'suspended';
  service_frequency: 'weekly' | 'bi-weekly' | 'monthly' | 'one-time' | 'custom';
  preferred_contact_method: 'email' | 'phone' | 'sms';
  notes: string;
  created: string;
  updated: string;
  last_service_date?: string;
  next_service_date?: string;
  total_services: number;
  total_revenue: number;
  organization: number;
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
    // Mock implementation - replace with real API call
    const mockClients: Client[] = [
      {
        id: 1,
        name: "John Smith",
        email: "john.smith@email.com",
        phone: "+1 (555) 123-4567",
        address: "123 Main St",
        city: "New York",
        state: "NY",
        zip_code: "10001",
        country: "USA",
        contact_person: "John Smith",
        client_type: "residential",
        status: "active",
        service_frequency: "weekly",
        preferred_contact_method: "email",
        notes: "Prefers morning appointments",
        created: "2024-01-15T10:00:00Z",
        updated: "2024-01-20T14:30:00Z",
        last_service_date: "2024-01-18T09:00:00Z",
        next_service_date: "2024-01-25T09:00:00Z",
        total_services: 12,
        total_revenue: 2400.00,
        organization: 1,
      },
      {
        id: 2,
        name: "ABC Corporation",
        email: "contact@abccorp.com",
        phone: "+1 (555) 987-6543",
        address: "456 Business Ave",
        city: "Los Angeles",
        state: "CA",
        zip_code: "90210",
        country: "USA",
        contact_person: "Jane Doe",
        company_name: "ABC Corporation",
        client_type: "commercial",
        status: "active",
        service_frequency: "bi-weekly",
        preferred_contact_method: "phone",
        notes: "Large office building, requires special equipment",
        created: "2024-01-10T08:00:00Z",
        updated: "2024-01-22T16:45:00Z",
        last_service_date: "2024-01-20T08:00:00Z",
        next_service_date: "2024-02-03T08:00:00Z",
        total_services: 8,
        total_revenue: 4800.00,
        organization: 1,
      },
    ];

    return { data: mockClients };
  }

  async getClient(id: number) {
    // Mock implementation
    const mockClient: Client = {
      id,
      name: "John Smith",
      email: "john.smith@email.com",
      phone: "+1 (555) 123-4567",
      address: "123 Main St",
      city: "New York",
      state: "NY",
      zip_code: "10001",
      country: "USA",
      contact_person: "John Smith",
      client_type: "residential",
      status: "active",
      service_frequency: "weekly",
      preferred_contact_method: "email",
      notes: "Prefers morning appointments",
      created: "2024-01-15T10:00:00Z",
      updated: "2024-01-20T14:30:00Z",
      last_service_date: "2024-01-18T09:00:00Z",
      next_service_date: "2024-01-25T09:00:00Z",
      total_services: 12,
      total_revenue: 2400.00,
      organization: 1,
    };

    return { data: mockClient };
  }

  async createClient(data: Partial<Client>) {
    // Mock implementation
    const newClient: Client = {
      id: Date.now(),
      name: data.name || "",
      email: data.email || "",
      phone: data.phone || "",
      address: data.address || "",
      city: data.city || "",
      state: data.state || "",
      zip_code: data.zip_code || "",
      country: data.country || "USA",
      contact_person: data.contact_person || data.name || "",
      company_name: data.company_name,
      client_type: data.client_type || "individual",
      status: data.status || "prospect",
      service_frequency: data.service_frequency || "one-time",
      preferred_contact_method: data.preferred_contact_method || "email",
      notes: data.notes || "",
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
      total_services: 0,
      total_revenue: 0,
      organization: 1,
    };

    return { data: newClient };
  }

  async updateClient(id: number, data: Partial<Client>) {
    // Mock implementation
    return { data: { ...data, id, updated: new Date().toISOString() } };
  }

  async deleteClient(id: number) {
    // Mock implementation
    return { data: { id } };
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
    // Mock implementation
    const mockNotes: ClientNote[] = [
      {
        id: 1,
        client: clientId,
        title: "Service Feedback",
        content: "Client was very satisfied with the last cleaning service.",
        note_type: "compliment",
        created_by: 1,
        created_by_name: "Jane Manager",
        created: "2024-01-18T15:30:00Z",
      },
    ];

    return { data: mockNotes };
  }

  async createClientNote(data: Partial<ClientNote>) {
    // Mock implementation
    const newNote: ClientNote = {
      id: Date.now(),
      client: data.client || 0,
      title: data.title || "",
      content: data.content || "",
      note_type: data.note_type || "general",
      created_by: 1,
      created_by_name: "Current User",
      created: new Date().toISOString(),
    };

    return { data: newNote };
  }

  // Dashboard/Summary
  async getClientSummary() {
    // Mock implementation
    const summary: ClientSummary = {
      total_clients: 156,
      active_clients: 142,
      new_clients_this_month: 8,
      total_revenue: 45600.00,
      average_service_frequency: "bi-weekly",
      top_service_types: [
        { service_type: "Regular Cleaning", count: 45 },
        { service_type: "Deep Cleaning", count: 32 },
        { service_type: "Carpet Cleaning", count: 18 },
        { service_type: "Window Cleaning", count: 12 },
      ],
    };

    return { data: summary };
  }
}

export const clientService = new ClientService();
