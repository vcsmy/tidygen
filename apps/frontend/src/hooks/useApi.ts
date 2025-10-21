/**
 * React Query hooks for API data fetching
 * Provides typed hooks for all backend endpoints with caching and error handling
 */

import { useQuery, useMutation, useQueryClient, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import { toast } from '@/components/ui/enhanced-notifications';
import apiClient, { 
  ApiResponse, 
  PaginatedResponse,
  User,
  UserProfile,
  LoginCredentials,
  LoginResponse,
  Product,
  ProductCategory,
  StockMovement,
  Supplier,
  PurchaseOrder,
  PurchaseOrderItem,
  Invoice,
  InvoiceItem,
  Customer,
  Payment,
  Expense,
  Employee,
} from '@/services/api';

// Query Keys
export const queryKeys = {
  // Auth
  currentUser: ['auth', 'currentUser'] as const,
  
  // Users
  users: ['users'] as const,
  user: (id: number) => ['users', id] as const,
  
  // Inventory
  products: ['inventory', 'products'] as const,
  product: (id: number) => ['inventory', 'products', id] as const,
  categories: ['inventory', 'categories'] as const,
  category: (id: number) => ['inventory', 'categories', id] as const,
  stockMovements: ['inventory', 'stockMovements'] as const,
  suppliers: ['inventory', 'suppliers'] as const,
  supplier: (id: number) => ['inventory', 'suppliers', id] as const,
  purchaseOrders: ['inventory', 'purchaseOrders'] as const,
  purchaseOrder: (id: number) => ['inventory', 'purchaseOrders', id] as const,
  
  // Finance
  invoices: ['finance', 'invoices'] as const,
  invoice: (id: number) => ['finance', 'invoices', id] as const,
  customers: ['finance', 'customers'] as const,
  customer: (id: number) => ['finance', 'customers', id] as const,
  payments: ['finance', 'payments'] as const,
  payment: (id: number) => ['finance', 'payments', id] as const,
  expenses: ['finance', 'expenses'] as const,
  expense: (id: number) => ['finance', 'expenses', id] as const,
  
  // HR
  employees: ['hr', 'employees'] as const,
  employee: (id: number) => ['hr', 'employees', id] as const,
};

// Generic query options
const defaultQueryOptions = {
  staleTime: 5 * 60 * 1000, // 5 minutes
  cacheTime: 10 * 60 * 1000, // 10 minutes
  retry: (failureCount: number, error: any) => {
    if (error?.status === 401 || error?.status === 403) {
      return false;
    }
    return failureCount < 3;
  },
};

// Auth Hooks
export function useCurrentUser(options?: UseQueryOptions<User>) {
  return useQuery({
    queryKey: queryKeys.currentUser,
    queryFn: async () => {
      if (!apiClient.isAuthenticated()) {
        return null;
      }
      const response = await apiClient.getCurrentUser();
      return response.data;
    },
    enabled: true, // Always enabled to resolve loading state
    ...defaultQueryOptions,
    ...options,
  });
}

export function useLogin(options?: UseMutationOptions<LoginResponse, Error, LoginCredentials>) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (credentials: LoginCredentials) => {
      const response = await apiClient.login(credentials);
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.currentUser, data.user);
      toast.success('Login Successful', 'Welcome back!');
    },
    onError: (error: any) => {
      toast.error('Login Failed', error.message || 'Invalid credentials');
    },
    ...options,
  });
}

export function useLogout(options?: UseMutationOptions<void, Error, void>) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async () => {
      await apiClient.logout();
    },
    onSuccess: () => {
      queryClient.clear();
      toast.success('Logged Out', 'You have been successfully logged out');
    },
    onError: (error: any) => {
      toast.error('Logout Failed', error.message || 'Failed to logout');
    },
    ...options,
  });
}

export default {
  useCurrentUser,
  useLogin,
  useLogout,
};