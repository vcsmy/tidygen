/**
 * HR service for managing employees, payroll, attendance, and performance
 */

import { apiClient } from '@/services/api';

export interface Employee {
  id: number;
  employee_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  country: string;
  date_of_birth: string;
  hire_date: string;
  position: string;
  department: string;
  employment_type: 'full_time' | 'part_time' | 'contract' | 'intern';
  status: 'active' | 'inactive' | 'terminated' | 'on_leave';
  salary: number;
  hourly_rate?: number;
  manager_id?: number;
  manager_name?: string;
  emergency_contact_name: string;
  emergency_contact_phone: string;
  emergency_contact_relationship: string;
  skills: string[];
  certifications: string[];
  notes: string;
  created: string;
  updated: string;
  organization: number;
}

export interface Attendance {
  id: number;
  employee: number;
  employee_name?: string;
  date: string;
  check_in_time?: string;
  check_out_time?: string;
  total_hours?: number;
  overtime_hours?: number;
  status: 'present' | 'absent' | 'late' | 'half_day' | 'sick_leave' | 'vacation' | 'personal_leave';
  notes: string;
  approved_by?: number;
  approved_by_name?: string;
  created: string;
  updated: string;
}

export interface Payroll {
  id: number;
  employee: number;
  employee_name?: string;
  pay_period_start: string;
  pay_period_end: string;
  gross_salary: number;
  overtime_pay: number;
  bonuses: number;
  deductions: number;
  net_salary: number;
  status: 'draft' | 'approved' | 'paid' | 'cancelled';
  payment_date?: string;
  payment_method: 'direct_deposit' | 'check' | 'cash';
  notes: string;
  created: string;
  updated: string;
}

export interface PerformanceReview {
  id: number;
  employee: number;
  employee_name?: string;
  review_period_start: string;
  review_period_end: string;
  reviewer_id: number;
  reviewer_name?: string;
  overall_rating: number;
  goals_achieved: number;
  goals_total: number;
  strengths: string[];
  areas_for_improvement: string[];
  goals_for_next_period: string[];
  comments: string;
  status: 'draft' | 'submitted' | 'approved' | 'completed';
  created: string;
  updated: string;
}

export interface LeaveRequest {
  id: number;
  employee: number;
  employee_name?: string;
  leave_type: 'vacation' | 'sick_leave' | 'personal_leave' | 'maternity_leave' | 'paternity_leave' | 'bereavement' | 'other';
  start_date: string;
  end_date: string;
  total_days: number;
  reason: string;
  status: 'pending' | 'approved' | 'rejected' | 'cancelled';
  approved_by?: number;
  approved_by_name?: string;
  approved_date?: string;
  comments: string;
  created: string;
  updated: string;
}

export interface HRSummary {
  total_employees: number;
  active_employees: number;
  new_employees_this_month: number;
  employees_on_leave: number;
  total_payroll_cost: number;
  average_salary: number;
  attendance_rate: number;
  pending_leave_requests: number;
  upcoming_birthdays: number;
  performance_reviews_due: number;
}

class HRService {
  // Employees
  async getEmployees(params?: {
    search?: string;
    department?: string;
    position?: string;
    status?: string;
    employment_type?: string;
    ordering?: string;
    page?: number;
    page_size?: number;
  }) {
    // Mock implementation - replace with real API call
    const mockEmployees: Employee[] = [
      {
        id: 1,
        employee_id: "EMP001",
        first_name: "John",
        last_name: "Smith",
        email: "john.smith@company.com",
        phone: "+1 (555) 123-4567",
        address: "123 Main St",
        city: "New York",
        state: "NY",
        zip_code: "10001",
        country: "USA",
        date_of_birth: "1985-06-15",
        hire_date: "2023-01-15",
        position: "Senior Cleaner",
        department: "Operations",
        employment_type: "full_time",
        status: "active",
        salary: 45000,
        hourly_rate: 22.50,
        manager_id: 3,
        manager_name: "Sarah Johnson",
        emergency_contact_name: "Jane Smith",
        emergency_contact_phone: "+1 (555) 987-6543",
        emergency_contact_relationship: "Spouse",
        skills: ["Deep Cleaning", "Carpet Cleaning", "Equipment Maintenance"],
        certifications: ["OSHA Safety", "Green Cleaning"],
        notes: "Excellent performance, reliable team member",
        created: "2023-01-15T10:00:00Z",
        updated: "2024-01-20T14:30:00Z",
        organization: 1,
      },
      {
        id: 2,
        employee_id: "EMP002",
        first_name: "Maria",
        last_name: "Garcia",
        email: "maria.garcia@company.com",
        phone: "+1 (555) 234-5678",
        address: "456 Oak Ave",
        city: "Los Angeles",
        state: "CA",
        zip_code: "90210",
        country: "USA",
        date_of_birth: "1990-03-22",
        hire_date: "2023-03-01",
        position: "Cleaning Specialist",
        department: "Operations",
        employment_type: "full_time",
        status: "active",
        salary: 42000,
        hourly_rate: 21.00,
        manager_id: 3,
        manager_name: "Sarah Johnson",
        emergency_contact_name: "Carlos Garcia",
        emergency_contact_phone: "+1 (555) 345-6789",
        emergency_contact_relationship: "Brother",
        skills: ["Window Cleaning", "Floor Care", "Customer Service"],
        certifications: ["Window Cleaning Specialist"],
        notes: "Great customer service skills",
        created: "2023-03-01T10:00:00Z",
        updated: "2024-01-18T16:45:00Z",
        organization: 1,
      },
      {
        id: 3,
        employee_id: "EMP003",
        first_name: "Sarah",
        last_name: "Johnson",
        email: "sarah.johnson@company.com",
        phone: "+1 (555) 345-6789",
        address: "789 Pine St",
        city: "Chicago",
        state: "IL",
        zip_code: "60601",
        country: "USA",
        date_of_birth: "1982-11-08",
        hire_date: "2022-08-15",
        position: "Team Lead",
        department: "Operations",
        employment_type: "full_time",
        status: "active",
        salary: 55000,
        hourly_rate: 27.50,
        emergency_contact_name: "Michael Johnson",
        emergency_contact_phone: "+1 (555) 456-7890",
        emergency_contact_relationship: "Husband",
        skills: ["Team Management", "Quality Control", "Training"],
        certifications: ["Management Certification", "Safety Training"],
        notes: "Strong leadership skills, excellent team builder",
        created: "2022-08-15T10:00:00Z",
        updated: "2024-01-22T09:15:00Z",
        organization: 1,
      },
    ];

    return { data: mockEmployees };
  }

  async getEmployee(id: number) {
    // Mock implementation
    const mockEmployee: Employee = {
      id,
      employee_id: `EMP${id.toString().padStart(3, '0')}`,
      first_name: "John",
      last_name: "Smith",
      email: "john.smith@company.com",
      phone: "+1 (555) 123-4567",
      address: "123 Main St",
      city: "New York",
      state: "NY",
      zip_code: "10001",
      country: "USA",
      date_of_birth: "1985-06-15",
      hire_date: "2023-01-15",
      position: "Senior Cleaner",
      department: "Operations",
      employment_type: "full_time",
      status: "active",
      salary: 45000,
      hourly_rate: 22.50,
      manager_id: 3,
      manager_name: "Sarah Johnson",
      emergency_contact_name: "Jane Smith",
      emergency_contact_phone: "+1 (555) 987-6543",
      emergency_contact_relationship: "Spouse",
      skills: ["Deep Cleaning", "Carpet Cleaning", "Equipment Maintenance"],
      certifications: ["OSHA Safety", "Green Cleaning"],
      notes: "Excellent performance, reliable team member",
      created: "2023-01-15T10:00:00Z",
      updated: "2024-01-20T14:30:00Z",
      organization: 1,
    };

    return { data: mockEmployee };
  }

  async createEmployee(data: Partial<Employee>) {
    // Mock implementation
    const newEmployee: Employee = {
      id: Date.now(),
      employee_id: `EMP${Date.now().toString().slice(-3)}`,
      first_name: data.first_name || "",
      last_name: data.last_name || "",
      email: data.email || "",
      phone: data.phone || "",
      address: data.address || "",
      city: data.city || "",
      state: data.state || "",
      zip_code: data.zip_code || "",
      country: data.country || "USA",
      date_of_birth: data.date_of_birth || "",
      hire_date: data.hire_date || new Date().toISOString().split('T')[0],
      position: data.position || "",
      department: data.department || "",
      employment_type: data.employment_type || "full_time",
      status: data.status || "active",
      salary: data.salary || 0,
      hourly_rate: data.hourly_rate,
      manager_id: data.manager_id,
      manager_name: data.manager_name,
      emergency_contact_name: data.emergency_contact_name || "",
      emergency_contact_phone: data.emergency_contact_phone || "",
      emergency_contact_relationship: data.emergency_contact_relationship || "",
      skills: data.skills || [],
      certifications: data.certifications || [],
      notes: data.notes || "",
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
      organization: 1,
    };

    return { data: newEmployee };
  }

  async updateEmployee(id: number, data: Partial<Employee>) {
    // Mock implementation
    return { data: { ...data, id, updated: new Date().toISOString() } };
  }

  async deleteEmployee(id: number) {
    // Mock implementation
    return { data: { id } };
  }

  // Attendance
  async getAttendance(params?: {
    employee?: number;
    start_date?: string;
    end_date?: string;
    status?: string;
    ordering?: string;
    page?: number;
    page_size?: number;
  }) {
    // Mock implementation
    const mockAttendance: Attendance[] = [
      {
        id: 1,
        employee: 1,
        employee_name: "John Smith",
        date: "2024-01-20",
        check_in_time: "08:00:00",
        check_out_time: "17:00:00",
        total_hours: 8,
        overtime_hours: 0,
        status: "present",
        notes: "",
        created: "2024-01-20T08:00:00Z",
        updated: "2024-01-20T17:00:00Z",
      },
      {
        id: 2,
        employee: 2,
        employee_name: "Maria Garcia",
        date: "2024-01-20",
        check_in_time: "08:15:00",
        check_out_time: "16:45:00",
        total_hours: 8.5,
        overtime_hours: 0.5,
        status: "present",
        notes: "Stayed late to finish project",
        created: "2024-01-20T08:15:00Z",
        updated: "2024-01-20T16:45:00Z",
      },
    ];

    return { data: mockAttendance };
  }

  async createAttendance(data: Partial<Attendance>) {
    // Mock implementation
    const newAttendance: Attendance = {
      id: Date.now(),
      employee: data.employee || 0,
      date: data.date || new Date().toISOString().split('T')[0],
      check_in_time: data.check_in_time,
      check_out_time: data.check_out_time,
      total_hours: data.total_hours,
      overtime_hours: data.overtime_hours || 0,
      status: data.status || "present",
      notes: data.notes || "",
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
    };

    return { data: newAttendance };
  }

  // Payroll
  async getPayroll(params?: {
    employee?: number;
    pay_period_start?: string;
    pay_period_end?: string;
    status?: string;
    ordering?: string;
    page?: number;
    page_size?: number;
  }) {
    // Mock implementation
    const mockPayroll: Payroll[] = [
      {
        id: 1,
        employee: 1,
        employee_name: "John Smith",
        pay_period_start: "2024-01-01",
        pay_period_end: "2024-01-15",
        gross_salary: 1875.00,
        overtime_pay: 0,
        bonuses: 100.00,
        deductions: 450.00,
        net_salary: 1525.00,
        status: "paid",
        payment_date: "2024-01-16",
        payment_method: "direct_deposit",
        notes: "Regular bi-weekly payroll",
        created: "2024-01-15T10:00:00Z",
        updated: "2024-01-16T09:00:00Z",
      },
    ];

    return { data: mockPayroll };
  }

  async createPayroll(data: Partial<Payroll>) {
    // Mock implementation
    const newPayroll: Payroll = {
      id: Date.now(),
      employee: data.employee || 0,
      employee_name: data.employee_name,
      pay_period_start: data.pay_period_start || "",
      pay_period_end: data.pay_period_end || "",
      gross_salary: data.gross_salary || 0,
      overtime_pay: data.overtime_pay || 0,
      bonuses: data.bonuses || 0,
      deductions: data.deductions || 0,
      net_salary: data.net_salary || 0,
      status: data.status || "draft",
      payment_date: data.payment_date,
      payment_method: data.payment_method || "direct_deposit",
      notes: data.notes || "",
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
    };

    return { data: newPayroll };
  }

  // Performance Reviews
  async getPerformanceReviews(params?: {
    employee?: number;
    reviewer?: number;
    status?: string;
    ordering?: string;
    page?: number;
    page_size?: number;
  }) {
    // Mock implementation
    const mockReviews: PerformanceReview[] = [
      {
        id: 1,
        employee: 1,
        employee_name: "John Smith",
        review_period_start: "2023-07-01",
        review_period_end: "2023-12-31",
        reviewer_id: 3,
        reviewer_name: "Sarah Johnson",
        overall_rating: 4.5,
        goals_achieved: 8,
        goals_total: 10,
        strengths: ["Reliability", "Quality work", "Team collaboration"],
        areas_for_improvement: ["Time management", "Communication"],
        goals_for_next_period: ["Improve efficiency", "Take on more responsibilities"],
        comments: "Excellent performance this period. John consistently delivers high-quality work.",
        status: "completed",
        created: "2024-01-01T10:00:00Z",
        updated: "2024-01-15T14:30:00Z",
      },
    ];

    return { data: mockReviews };
  }

  async createPerformanceReview(data: Partial<PerformanceReview>) {
    // Mock implementation
    const newReview: PerformanceReview = {
      id: Date.now(),
      employee: data.employee || 0,
      employee_name: data.employee_name,
      review_period_start: data.review_period_start || "",
      review_period_end: data.review_period_end || "",
      reviewer_id: data.reviewer_id || 0,
      reviewer_name: data.reviewer_name,
      overall_rating: data.overall_rating || 0,
      goals_achieved: data.goals_achieved || 0,
      goals_total: data.goals_total || 0,
      strengths: data.strengths || [],
      areas_for_improvement: data.areas_for_improvement || [],
      goals_for_next_period: data.goals_for_next_period || [],
      comments: data.comments || "",
      status: data.status || "draft",
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
    };

    return { data: newReview };
  }

  // Leave Requests
  async getLeaveRequests(params?: {
    employee?: number;
    leave_type?: string;
    status?: string;
    start_date?: string;
    end_date?: string;
    ordering?: string;
    page?: number;
    page_size?: number;
  }) {
    // Mock implementation
    const mockLeaveRequests: LeaveRequest[] = [
      {
        id: 1,
        employee: 1,
        employee_name: "John Smith",
        leave_type: "vacation",
        start_date: "2024-02-15",
        end_date: "2024-02-19",
        total_days: 5,
        reason: "Family vacation",
        status: "approved",
        approved_by: 3,
        approved_by_name: "Sarah Johnson",
        approved_date: "2024-01-20",
        comments: "Approved for family vacation",
        created: "2024-01-15T10:00:00Z",
        updated: "2024-01-20T14:30:00Z",
      },
    ];

    return { data: mockLeaveRequests };
  }

  async createLeaveRequest(data: Partial<LeaveRequest>) {
    // Mock implementation
    const newLeaveRequest: LeaveRequest = {
      id: Date.now(),
      employee: data.employee || 0,
      employee_name: data.employee_name,
      leave_type: data.leave_type || "vacation",
      start_date: data.start_date || "",
      end_date: data.end_date || "",
      total_days: data.total_days || 0,
      reason: data.reason || "",
      status: data.status || "pending",
      approved_by: data.approved_by,
      approved_by_name: data.approved_by_name,
      approved_date: data.approved_date,
      comments: data.comments || "",
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
    };

    return { data: newLeaveRequest };
  }

  async updateLeaveRequest(id: number, data: Partial<LeaveRequest>) {
    // Mock implementation
    return { data: { ...data, id, updated: new Date().toISOString() } };
  }

  // Dashboard/Summary
  async getHRSummary() {
    // Mock implementation
    const summary: HRSummary = {
      total_employees: 25,
      active_employees: 23,
      new_employees_this_month: 2,
      employees_on_leave: 1,
      total_payroll_cost: 125000,
      average_salary: 50000,
      attendance_rate: 96.5,
      pending_leave_requests: 3,
      upcoming_birthdays: 2,
      performance_reviews_due: 5,
    };

    return { data: summary };
  }
}

export const hrService = new HRService();
