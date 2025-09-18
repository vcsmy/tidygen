/**
 * Finance service for managing invoices, payments, expenses, and financial reporting
 */

import { apiClient } from '@/services/api';

export interface Invoice {
  id: number;
  invoice_number: string;
  client: number;
  client_name?: string;
  client_email?: string;
  client_address?: string;
  issue_date: string;
  due_date: string;
  status: 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled';
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  total_amount: number;
  currency: string;
  notes: string;
  terms_conditions: string;
  payment_terms: string;
  items: InvoiceItem[];
  payments: Payment[];
  created: string;
  updated: string;
  organization: number;
}

export interface InvoiceItem {
  id: number;
  invoice: number;
  description: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  service_type?: string;
  created: string;
}

export interface Payment {
  id: number;
  invoice: number;
  amount: number;
  payment_date: string;
  payment_method: 'cash' | 'check' | 'credit_card' | 'bank_transfer' | 'online' | 'other';
  reference_number: string;
  notes: string;
  status: 'pending' | 'completed' | 'failed' | 'refunded';
  created: string;
  updated: string;
}

export interface Expense {
  id: number;
  category: string;
  description: string;
  amount: number;
  expense_date: string;
  vendor: string;
  payment_method: 'cash' | 'check' | 'credit_card' | 'bank_transfer' | 'online';
  reference_number: string;
  receipt_url?: string;
  status: 'pending' | 'approved' | 'rejected';
  approved_by?: number;
  approved_by_name?: string;
  notes: string;
  created: string;
  updated: string;
  organization: number;
}

export interface FinancialSummary {
  total_revenue: number;
  total_expenses: number;
  net_profit: number;
  outstanding_invoices: number;
  overdue_invoices: number;
  monthly_revenue: number;
  monthly_expenses: number;
  profit_margin: number;
  average_invoice_amount: number;
  payment_collection_rate: number;
}

export interface RevenueReport {
  period: string;
  total_revenue: number;
  invoice_count: number;
  paid_invoices: number;
  outstanding_amount: number;
  breakdown: Array<{
    service_type: string;
    amount: number;
    count: number;
  }>;
}

export interface ExpenseReport {
  period: string;
  total_expenses: number;
  expense_count: number;
  breakdown: Array<{
    category: string;
    amount: number;
    count: number;
  }>;
}

class FinanceService {
  // Invoices
  async getInvoices(params?: {
    client?: number;
    status?: string;
    search?: string;
    start_date?: string;
    end_date?: string;
    ordering?: string;
    page?: number;
    page_size?: number;
  }) {
    // Mock implementation - replace with real API call
    const mockInvoices: Invoice[] = [
      {
        id: 1,
        invoice_number: "INV-2024-001",
        client: 1,
        client_name: "John Smith",
        client_email: "john.smith@email.com",
        client_address: "123 Main St, New York, NY 10001",
        issue_date: "2024-01-15",
        due_date: "2024-02-15",
        status: "paid",
        subtotal: 200.00,
        tax_amount: 20.00,
        discount_amount: 0.00,
        total_amount: 220.00,
        currency: "USD",
        notes: "Weekly cleaning service",
        terms_conditions: "Payment due within 30 days",
        payment_terms: "Net 30",
        items: [
          {
            id: 1,
            invoice: 1,
            description: "Weekly House Cleaning",
            quantity: 4,
            unit_price: 50.00,
            total_price: 200.00,
            service_type: "Regular Cleaning",
            created: "2024-01-15T10:00:00Z",
          },
        ],
        payments: [
          {
            id: 1,
            invoice: 1,
            amount: 220.00,
            payment_date: "2024-01-20",
            payment_method: "credit_card",
            reference_number: "CC-123456",
            notes: "Payment received",
            status: "completed",
            created: "2024-01-20T14:30:00Z",
            updated: "2024-01-20T14:30:00Z",
          },
        ],
        created: "2024-01-15T10:00:00Z",
        updated: "2024-01-20T14:30:00Z",
        organization: 1,
      },
      {
        id: 2,
        invoice_number: "INV-2024-002",
        client: 2,
        client_name: "ABC Corporation",
        client_email: "contact@abccorp.com",
        client_address: "456 Business Ave, Los Angeles, CA 90210",
        issue_date: "2024-01-20",
        due_date: "2024-02-20",
        status: "sent",
        subtotal: 800.00,
        tax_amount: 80.00,
        discount_amount: 0.00,
        total_amount: 880.00,
        currency: "USD",
        notes: "Monthly office cleaning",
        terms_conditions: "Payment due within 30 days",
        payment_terms: "Net 30",
        items: [
          {
            id: 2,
            invoice: 2,
            description: "Monthly Office Cleaning",
            quantity: 1,
            unit_price: 800.00,
            total_price: 800.00,
            service_type: "Commercial Cleaning",
            created: "2024-01-20T10:00:00Z",
          },
        ],
        payments: [],
        created: "2024-01-20T10:00:00Z",
        updated: "2024-01-20T10:00:00Z",
        organization: 1,
      },
    ];

    return { data: mockInvoices };
  }

  async getInvoice(id: number) {
    // Mock implementation
    const mockInvoice: Invoice = {
      id,
      invoice_number: `INV-2024-${id.toString().padStart(3, '0')}`,
      client: 1,
      client_name: "John Smith",
      client_email: "john.smith@email.com",
      client_address: "123 Main St, New York, NY 10001",
      issue_date: "2024-01-15",
      due_date: "2024-02-15",
      status: "paid",
      subtotal: 200.00,
      tax_amount: 20.00,
      discount_amount: 0.00,
      total_amount: 220.00,
      currency: "USD",
      notes: "Weekly cleaning service",
      terms_conditions: "Payment due within 30 days",
      payment_terms: "Net 30",
      items: [],
      payments: [],
      created: "2024-01-15T10:00:00Z",
      updated: "2024-01-20T14:30:00Z",
      organization: 1,
    };

    return { data: mockInvoice };
  }

  async createInvoice(data: Partial<Invoice>) {
    // Mock implementation
    const newInvoice: Invoice = {
      id: Date.now(),
      invoice_number: `INV-2024-${Date.now().toString().slice(-3)}`,
      client: data.client || 0,
      client_name: data.client_name,
      client_email: data.client_email,
      client_address: data.client_address,
      issue_date: data.issue_date || new Date().toISOString().split('T')[0],
      due_date: data.due_date || new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      status: data.status || "draft",
      subtotal: data.subtotal || 0,
      tax_amount: data.tax_amount || 0,
      discount_amount: data.discount_amount || 0,
      total_amount: data.total_amount || 0,
      currency: data.currency || "USD",
      notes: data.notes || "",
      terms_conditions: data.terms_conditions || "Payment due within 30 days",
      payment_terms: data.payment_terms || "Net 30",
      items: data.items || [],
      payments: [],
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
      organization: 1,
    };

    return { data: newInvoice };
  }

  async updateInvoice(id: number, data: Partial<Invoice>) {
    // Mock implementation
    return { data: { ...data, id, updated: new Date().toISOString() } };
  }

  async deleteInvoice(id: number) {
    // Mock implementation
    return { data: { id } };
  }

  async sendInvoice(id: number) {
    // Mock implementation
    return { data: { id, status: "sent", updated: new Date().toISOString() } };
  }

  async markInvoicePaid(id: number) {
    // Mock implementation
    return { data: { id, status: "paid", updated: new Date().toISOString() } };
  }

  // Payments
  async getPayments(params?: {
    invoice?: number;
    payment_method?: string;
    status?: string;
    start_date?: string;
    end_date?: string;
    ordering?: string;
    page?: number;
    page_size?: number;
  }) {
    // Mock implementation
    const mockPayments: Payment[] = [
      {
        id: 1,
        invoice: 1,
        amount: 220.00,
        payment_date: "2024-01-20",
        payment_method: "credit_card",
        reference_number: "CC-123456",
        notes: "Payment received",
        status: "completed",
        created: "2024-01-20T14:30:00Z",
        updated: "2024-01-20T14:30:00Z",
      },
    ];

    return { data: mockPayments };
  }

  async createPayment(data: Partial<Payment>) {
    // Mock implementation
    const newPayment: Payment = {
      id: Date.now(),
      invoice: data.invoice || 0,
      amount: data.amount || 0,
      payment_date: data.payment_date || new Date().toISOString().split('T')[0],
      payment_method: data.payment_method || "cash",
      reference_number: data.reference_number || "",
      notes: data.notes || "",
      status: data.status || "completed",
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
    };

    return { data: newPayment };
  }

  // Expenses
  async getExpenses(params?: {
    category?: string;
    vendor?: string;
    status?: string;
    start_date?: string;
    end_date?: string;
    search?: string;
    ordering?: string;
    page?: number;
    page_size?: number;
  }) {
    // Mock implementation
    const mockExpenses: Expense[] = [
      {
        id: 1,
        category: "Supplies",
        description: "Cleaning supplies purchase",
        amount: 150.00,
        expense_date: "2024-01-15",
        vendor: "CleanPro Supplies",
        payment_method: "credit_card",
        reference_number: "CC-789012",
        receipt_url: "/receipts/receipt-001.pdf",
        status: "approved",
        approved_by: 1,
        approved_by_name: "Manager",
        notes: "Monthly supplies order",
        created: "2024-01-15T10:00:00Z",
        updated: "2024-01-15T10:00:00Z",
        organization: 1,
      },
      {
        id: 2,
        category: "Equipment",
        description: "New vacuum cleaner",
        amount: 299.99,
        expense_date: "2024-01-18",
        vendor: "Equipment Pro",
        payment_method: "bank_transfer",
        reference_number: "BT-345678",
        status: "pending",
        notes: "Replacement for broken unit",
        created: "2024-01-18T14:00:00Z",
        updated: "2024-01-18T14:00:00Z",
        organization: 1,
      },
    ];

    return { data: mockExpenses };
  }

  async createExpense(data: Partial<Expense>) {
    // Mock implementation
    const newExpense: Expense = {
      id: Date.now(),
      category: data.category || "",
      description: data.description || "",
      amount: data.amount || 0,
      expense_date: data.expense_date || new Date().toISOString().split('T')[0],
      vendor: data.vendor || "",
      payment_method: data.payment_method || "cash",
      reference_number: data.reference_number || "",
      receipt_url: data.receipt_url,
      status: data.status || "pending",
      approved_by: data.approved_by,
      approved_by_name: data.approved_by_name,
      notes: data.notes || "",
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
      organization: 1,
    };

    return { data: newExpense };
  }

  async updateExpense(id: number, data: Partial<Expense>) {
    // Mock implementation
    return { data: { ...data, id, updated: new Date().toISOString() } };
  }

  async approveExpense(id: number, approvedBy: number) {
    // Mock implementation
    return { data: { id, status: "approved", approved_by: approvedBy, updated: new Date().toISOString() } };
  }

  // Financial Reports
  async getFinancialSummary() {
    // Mock implementation
    const summary: FinancialSummary = {
      total_revenue: 45600.00,
      total_expenses: 12300.00,
      net_profit: 33300.00,
      outstanding_invoices: 8800.00,
      overdue_invoices: 1200.00,
      monthly_revenue: 15200.00,
      monthly_expenses: 4100.00,
      profit_margin: 73.0,
      average_invoice_amount: 550.00,
      payment_collection_rate: 92.5,
    };

    return { data: summary };
  }

  async getRevenueReport(params?: {
    start_date?: string;
    end_date?: string;
    period?: 'daily' | 'weekly' | 'monthly' | 'yearly';
  }) {
    // Mock implementation
    const report: RevenueReport = {
      period: "January 2024",
      total_revenue: 15200.00,
      invoice_count: 28,
      paid_invoices: 25,
      outstanding_amount: 8800.00,
      breakdown: [
        { service_type: "Regular Cleaning", amount: 8000.00, count: 20 },
        { service_type: "Deep Cleaning", amount: 4500.00, count: 5 },
        { service_type: "Commercial Cleaning", amount: 2700.00, count: 3 },
      ],
    };

    return { data: report };
  }

  async getExpenseReport(params?: {
    start_date?: string;
    end_date?: string;
    period?: 'daily' | 'weekly' | 'monthly' | 'yearly';
  }) {
    // Mock implementation
    const report: ExpenseReport = {
      period: "January 2024",
      total_expenses: 4100.00,
      expense_count: 15,
      breakdown: [
        { category: "Supplies", amount: 1800.00, count: 8 },
        { category: "Equipment", amount: 1200.00, count: 3 },
        { category: "Transportation", amount: 600.00, count: 2 },
        { category: "Utilities", amount: 500.00, count: 2 },
      ],
    };

    return { data: report };
  }
}

export const financeService = new FinanceService();
