/**
 * Scheduling service for managing appointments, services, and team assignments
 */

import { apiClient } from '@/services/api';

export interface Appointment {
  id: number;
  appointment_number: string;
  client: number;
  client_name?: string;
  client_email?: string;
  client_phone?: string;
  client_address?: string;
  service_type: string;
  service_description: string;
  scheduled_date: string;
  scheduled_time: string;
  estimated_duration: number; // in minutes
  actual_duration?: number; // in minutes
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled' | 'rescheduled' | 'no_show';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  assigned_team: number[];
  assigned_team_names?: string[];
  team_lead?: number;
  team_lead_name?: string;
  special_instructions: string;
  equipment_needed: string[];
  estimated_cost: number;
  actual_cost?: number;
  notes: string;
  created_by: number;
  created_by_name?: string;
  created: string;
  updated: string;
  organization: number;
}

export interface ServiceTemplate {
  id: number;
  name: string;
  description: string;
  service_type: string;
  estimated_duration: number; // in minutes
  base_cost: number;
  equipment_required: string[];
  skills_required: string[];
  is_recurring: boolean;
  recurrence_pattern?: 'daily' | 'weekly' | 'monthly' | 'quarterly';
  recurrence_interval?: number;
  is_active: boolean;
  created: string;
  updated: string;
}

export interface Team {
  id: number;
  name: string;
  description: string;
  team_lead: number;
  team_lead_name?: string;
  members: number[];
  member_names?: string[];
  specializations: string[];
  max_capacity: number;
  current_load: number;
  is_active: boolean;
  created: string;
  updated: string;
}

export interface ScheduleConflict {
  id: number;
  appointment_id: number;
  conflict_type: 'double_booking' | 'resource_conflict' | 'time_overlap' | 'capacity_exceeded';
  conflicting_appointment_id?: number;
  conflicting_resource?: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  resolved: boolean;
  resolution_notes?: string;
  created: string;
  updated: string;
}

export interface ScheduleSummary {
  total_appointments: number;
  scheduled_today: number;
  completed_today: number;
  pending_appointments: number;
  overdue_appointments: number;
  team_utilization: number;
  average_duration: number;
  revenue_today: number;
  upcoming_appointments: number;
  conflicts_resolved: number;
}

export interface CalendarEvent {
  id: number;
  title: string;
  start: string;
  end: string;
  allDay: boolean;
  type: 'appointment' | 'maintenance' | 'training' | 'meeting' | 'other';
  status: string;
  color: string;
  description?: string;
  location?: string;
  attendees?: string[];
}

class SchedulingService {
  // Appointments
  async getAppointments(params?: {
    client?: number;
    team?: number;
    status?: string;
    start_date?: string;
    end_date?: string;
    priority?: string;
    search?: string;
    ordering?: string;
    page?: number;
    page_size?: number;
  }) {
    // Mock implementation - replace with real API call
    const mockAppointments: Appointment[] = [
      {
        id: 1,
        appointment_number: "APT-2024-001",
        client: 1,
        client_name: "John Smith",
        client_email: "john.smith@email.com",
        client_phone: "+1 (555) 123-4567",
        client_address: "123 Main St, New York, NY 10001",
        service_type: "Deep Cleaning",
        service_description: "Complete deep cleaning of 3-bedroom house",
        scheduled_date: "2024-01-25",
        scheduled_time: "09:00:00",
        estimated_duration: 240,
        actual_duration: 240,
        status: "scheduled",
        priority: "medium",
        assigned_team: [1, 2],
        assigned_team_names: ["Team Alpha", "Team Beta"],
        team_lead: 3,
        team_lead_name: "Sarah Johnson",
        special_instructions: "Focus on kitchen and bathrooms, client has allergies to strong chemicals",
        equipment_needed: ["Vacuum", "Steam Cleaner", "All-purpose Cleaner"],
        estimated_cost: 350.00,
        actual_cost: 350.00,
        notes: "Client prefers morning appointments",
        created_by: 1,
        created_by_name: "Admin User",
        created: "2024-01-20T10:00:00Z",
        updated: "2024-01-20T10:00:00Z",
        organization: 1,
      },
      {
        id: 2,
        appointment_number: "APT-2024-002",
        client: 2,
        client_name: "ABC Corporation",
        client_email: "contact@abccorp.com",
        client_phone: "+1 (555) 234-5678",
        client_address: "456 Business Ave, Los Angeles, CA 90210",
        service_type: "Office Cleaning",
        service_description: "Weekly office cleaning service",
        scheduled_date: "2024-01-25",
        scheduled_time: "14:00:00",
        estimated_duration: 180,
        status: "scheduled",
        priority: "high",
        assigned_team: [1],
        assigned_team_names: ["Team Alpha"],
        team_lead: 3,
        team_lead_name: "Sarah Johnson",
        special_instructions: "After hours cleaning, security code required",
        equipment_needed: ["Commercial Vacuum", "Floor Buffer"],
        estimated_cost: 280.00,
        notes: "Recurring weekly appointment",
        created_by: 1,
        created_by_name: "Admin User",
        created: "2024-01-22T14:30:00Z",
        updated: "2024-01-22T14:30:00Z",
        organization: 1,
      },
      {
        id: 3,
        appointment_number: "APT-2024-003",
        client: 3,
        client_name: "Johnson Family",
        client_email: "johnson.family@email.com",
        client_phone: "+1 (555) 345-6789",
        client_address: "789 Oak St, Chicago, IL 60601",
        service_type: "Regular Cleaning",
        service_description: "Bi-weekly house cleaning",
        scheduled_date: "2024-01-24",
        scheduled_time: "10:00:00",
        estimated_duration: 120,
        actual_duration: 120,
        status: "completed",
        priority: "low",
        assigned_team: [2],
        assigned_team_names: ["Team Beta"],
        team_lead: 4,
        team_lead_name: "Mike Rodriguez",
        special_instructions: "Pet-friendly products only",
        equipment_needed: ["Vacuum", "Microfiber Cloths"],
        estimated_cost: 150.00,
        actual_cost: 150.00,
        notes: "Completed on time, client satisfied",
        created_by: 1,
        created_by_name: "Admin User",
        created: "2024-01-15T09:00:00Z",
        updated: "2024-01-24T12:00:00Z",
        organization: 1,
      },
    ];

    return { data: mockAppointments };
  }

  async getAppointment(id: number) {
    // Mock implementation
    const mockAppointment: Appointment = {
      id,
      appointment_number: `APT-2024-${id.toString().padStart(3, '0')}`,
      client: 1,
      client_name: "John Smith",
      client_email: "john.smith@email.com",
      client_phone: "+1 (555) 123-4567",
      client_address: "123 Main St, New York, NY 10001",
      service_type: "Deep Cleaning",
      service_description: "Complete deep cleaning of 3-bedroom house",
      scheduled_date: "2024-01-25",
      scheduled_time: "09:00:00",
      estimated_duration: 240,
      status: "scheduled",
      priority: "medium",
      assigned_team: [1, 2],
      assigned_team_names: ["Team Alpha", "Team Beta"],
      team_lead: 3,
      team_lead_name: "Sarah Johnson",
      special_instructions: "Focus on kitchen and bathrooms",
      equipment_needed: ["Vacuum", "Steam Cleaner"],
      estimated_cost: 350.00,
      notes: "Client prefers morning appointments",
      created_by: 1,
      created_by_name: "Admin User",
      created: "2024-01-20T10:00:00Z",
      updated: "2024-01-20T10:00:00Z",
      organization: 1,
    };

    return { data: mockAppointment };
  }

  async createAppointment(data: Partial<Appointment>) {
    // Mock implementation
    const newAppointment: Appointment = {
      id: Date.now(),
      appointment_number: `APT-2024-${Date.now().toString().slice(-3)}`,
      client: data.client || 0,
      client_name: data.client_name,
      client_email: data.client_email,
      client_phone: data.client_phone,
      client_address: data.client_address,
      service_type: data.service_type || "",
      service_description: data.service_description || "",
      scheduled_date: data.scheduled_date || new Date().toISOString().split('T')[0],
      scheduled_time: data.scheduled_time || "09:00:00",
      estimated_duration: data.estimated_duration || 120,
      actual_duration: data.actual_duration,
      status: data.status || "scheduled",
      priority: data.priority || "medium",
      assigned_team: data.assigned_team || [],
      assigned_team_names: data.assigned_team_names,
      team_lead: data.team_lead,
      team_lead_name: data.team_lead_name,
      special_instructions: data.special_instructions || "",
      equipment_needed: data.equipment_needed || [],
      estimated_cost: data.estimated_cost || 0,
      actual_cost: data.actual_cost,
      notes: data.notes || "",
      created_by: data.created_by || 1,
      created_by_name: data.created_by_name,
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
      organization: 1,
    };

    return { data: newAppointment };
  }

  async updateAppointment(id: number, data: Partial<Appointment>) {
    // Mock implementation
    return { data: { ...data, id, updated: new Date().toISOString() } };
  }

  async deleteAppointment(id: number) {
    // Mock implementation
    return { data: { id } };
  }

  async rescheduleAppointment(id: number, newDate: string, newTime: string) {
    // Mock implementation
    return { data: { id, scheduled_date: newDate, scheduled_time: newTime, status: "rescheduled", updated: new Date().toISOString() } };
  }

  async completeAppointment(id: number, actualDuration: number, actualCost: number, notes: string) {
    // Mock implementation
    return { data: { id, status: "completed", actual_duration: actualDuration, actual_cost: actualCost, notes, updated: new Date().toISOString() } };
  }

  // Service Templates
  async getServiceTemplates(params?: {
    service_type?: string;
    is_active?: boolean;
    search?: string;
    ordering?: string;
    page?: number;
    page_size?: number;
  }) {
    // Mock implementation
    const mockTemplates: ServiceTemplate[] = [
      {
        id: 1,
        name: "Standard House Cleaning",
        description: "Regular house cleaning service",
        service_type: "Regular Cleaning",
        estimated_duration: 120,
        base_cost: 150.00,
        equipment_required: ["Vacuum", "All-purpose Cleaner", "Microfiber Cloths"],
        skills_required: ["Basic Cleaning", "Time Management"],
        is_recurring: true,
        recurrence_pattern: "weekly",
        recurrence_interval: 1,
        is_active: true,
        created: "2024-01-01T10:00:00Z",
        updated: "2024-01-01T10:00:00Z",
      },
      {
        id: 2,
        name: "Deep Cleaning Service",
        description: "Comprehensive deep cleaning",
        service_type: "Deep Cleaning",
        estimated_duration: 240,
        base_cost: 350.00,
        equipment_required: ["Vacuum", "Steam Cleaner", "Heavy-duty Cleaners", "Scrub Brushes"],
        skills_required: ["Deep Cleaning", "Equipment Operation", "Attention to Detail"],
        is_recurring: false,
        is_active: true,
        created: "2024-01-01T10:00:00Z",
        updated: "2024-01-01T10:00:00Z",
      },
    ];

    return { data: mockTemplates };
  }

  async createServiceTemplate(data: Partial<ServiceTemplate>) {
    // Mock implementation
    const newTemplate: ServiceTemplate = {
      id: Date.now(),
      name: data.name || "",
      description: data.description || "",
      service_type: data.service_type || "",
      estimated_duration: data.estimated_duration || 120,
      base_cost: data.base_cost || 0,
      equipment_required: data.equipment_required || [],
      skills_required: data.skills_required || [],
      is_recurring: data.is_recurring || false,
      recurrence_pattern: data.recurrence_pattern,
      recurrence_interval: data.recurrence_interval,
      is_active: data.is_active !== undefined ? data.is_active : true,
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
    };

    return { data: newTemplate };
  }

  // Teams
  async getTeams(params?: {
    is_active?: boolean;
    search?: string;
    ordering?: string;
    page?: number;
    page_size?: number;
  }) {
    // Mock implementation
    const mockTeams: Team[] = [
      {
        id: 1,
        name: "Team Alpha",
        description: "Primary cleaning team for residential services",
        team_lead: 3,
        team_lead_name: "Sarah Johnson",
        members: [1, 2, 3],
        member_names: ["John Smith", "Maria Garcia", "Sarah Johnson"],
        specializations: ["Residential Cleaning", "Deep Cleaning"],
        max_capacity: 5,
        current_load: 3,
        is_active: true,
        created: "2024-01-01T10:00:00Z",
        updated: "2024-01-20T10:00:00Z",
      },
      {
        id: 2,
        name: "Team Beta",
        description: "Commercial cleaning specialists",
        team_lead: 4,
        team_lead_name: "Mike Rodriguez",
        members: [4, 5, 6],
        member_names: ["Mike Rodriguez", "Lisa Chen", "David Wilson"],
        specializations: ["Commercial Cleaning", "Office Cleaning"],
        max_capacity: 4,
        current_load: 2,
        is_active: true,
        created: "2024-01-01T10:00:00Z",
        updated: "2024-01-20T10:00:00Z",
      },
    ];

    return { data: mockTeams };
  }

  async createTeam(data: Partial<Team>) {
    // Mock implementation
    const newTeam: Team = {
      id: Date.now(),
      name: data.name || "",
      description: data.description || "",
      team_lead: data.team_lead || 0,
      team_lead_name: data.team_lead_name,
      members: data.members || [],
      member_names: data.member_names,
      specializations: data.specializations || [],
      max_capacity: data.max_capacity || 5,
      current_load: 0,
      is_active: data.is_active !== undefined ? data.is_active : true,
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
    };

    return { data: newTeam };
  }

  // Schedule Conflicts
  async getScheduleConflicts(params?: {
    resolved?: boolean;
    severity?: string;
    start_date?: string;
    end_date?: string;
    ordering?: string;
    page?: number;
    page_size?: number;
  }) {
    // Mock implementation
    const mockConflicts: ScheduleConflict[] = [
      {
        id: 1,
        appointment_id: 1,
        conflict_type: "double_booking",
        conflicting_appointment_id: 2,
        description: "Team Alpha double-booked for 2:00 PM slot",
        severity: "high",
        resolved: false,
        created: "2024-01-24T10:00:00Z",
        updated: "2024-01-24T10:00:00Z",
      },
    ];

    return { data: mockConflicts };
  }

  async resolveConflict(id: number, resolutionNotes: string) {
    // Mock implementation
    return { data: { id, resolved: true, resolution_notes: resolutionNotes, updated: new Date().toISOString() } };
  }

  // Calendar Events
  async getCalendarEvents(params?: {
    start_date?: string;
    end_date?: string;
    type?: string;
    ordering?: string;
  }) {
    // Mock implementation
    const mockEvents: CalendarEvent[] = [
      {
        id: 1,
        title: "Deep Cleaning - John Smith",
        start: "2024-01-25T09:00:00Z",
        end: "2024-01-25T13:00:00Z",
        allDay: false,
        type: "appointment",
        status: "scheduled",
        color: "#3b82f6",
        description: "Complete deep cleaning of 3-bedroom house",
        location: "123 Main St, New York, NY 10001",
        attendees: ["Team Alpha", "Team Beta"],
      },
      {
        id: 2,
        title: "Office Cleaning - ABC Corp",
        start: "2024-01-25T14:00:00Z",
        end: "2024-01-25T17:00:00Z",
        allDay: false,
        type: "appointment",
        status: "scheduled",
        color: "#10b981",
        description: "Weekly office cleaning service",
        location: "456 Business Ave, Los Angeles, CA 90210",
        attendees: ["Team Alpha"],
      },
    ];

    return { data: mockEvents };
  }

  // Dashboard/Summary
  async getScheduleSummary() {
    // Mock implementation
    const summary: ScheduleSummary = {
      total_appointments: 45,
      scheduled_today: 8,
      completed_today: 6,
      pending_appointments: 12,
      overdue_appointments: 2,
      team_utilization: 85.5,
      average_duration: 165,
      revenue_today: 1250.00,
      upcoming_appointments: 15,
      conflicts_resolved: 3,
    };

    return { data: summary };
  }
}

export const schedulingService = new SchedulingService();
