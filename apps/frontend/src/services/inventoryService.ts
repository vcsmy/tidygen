/**
 * Inventory service for managing products, categories, suppliers, and stock
 */

import { apiClient } from '@/services/api';

export interface Product {
  id: number;
  name: string;
  sku: string;
  description: string;
  category: number | null;
  category_name?: string;
  cost_price: number;
  selling_price: number;
  current_stock: number;
  min_stock_level: number;
  max_stock_level: number;
  weight?: number;
  dimensions?: string;
  barcode?: string;
  image?: string;
  is_active: boolean;
  is_digital: boolean;
  organization: number;
  created: string;
  updated: string;
}

export interface ProductCategory {
  id: number;
  name: string;
  description: string;
  parent: number | null;
  organization: number;
  created: string;
  updated: string;
}

export interface Supplier {
  id: number;
  name: string;
  contact_person: string;
  email: string;
  phone: string;
  address: string;
  payment_terms: string;
  organization: number;
  created: string;
  updated: string;
}

export interface StockMovement {
  id: number;
  product: number;
  product_name?: string;
  movement_type: 'in' | 'out' | 'transfer' | 'adjustment';
  quantity: number;
  reference_number: string;
  notes: string;
  created: string;
  updated: string;
}

export interface PurchaseOrder {
  id: number;
  supplier: number;
  supplier_name?: string;
  order_number: string;
  status: 'draft' | 'sent' | 'confirmed' | 'received' | 'cancelled';
  order_date: string;
  expected_delivery?: string;
  total_amount: number;
  notes: string;
  organization: number;
  created: string;
  updated: string;
  items?: PurchaseOrderItem[];
}

export interface PurchaseOrderItem {
  id: number;
  purchase_order: number;
  product: number;
  product_name?: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  created: string;
  updated: string;
}

export interface InventorySummary {
  total_products: number;
  total_categories: number;
  total_suppliers: number;
  total_stock_value: number;
  low_stock_products: number;
  out_of_stock_products: number;
  recent_movements: number;
  pending_orders: number;
}

export interface StockAlert {
  product_id: number;
  product_name: string;
  product_sku: string;
  current_stock: number;
  min_stock_level: number;
  alert_type: 'low_stock' | 'out_of_stock';
  days_until_stockout: number;
  suggested_order_quantity: number;
}

class InventoryService {
  // Products
  async getProducts(params?: {
    search?: string;
    category?: number;
    is_active?: boolean;
    ordering?: string;
    page?: number;
    page_size?: number;
  }) {
    return apiClient.get('/inventory/products/', params);
  }

  async getProduct(id: number) {
    return apiClient.get(`/inventory/products/${id}/`);
  }

  async createProduct(data: Partial<Product>) {
    return apiClient.post('/inventory/products/', data);
  }

  async updateProduct(id: number, data: Partial<Product>) {
    return apiClient.patch(`/inventory/products/${id}/`, data);
  }

  async deleteProduct(id: number) {
    return apiClient.delete(`/inventory/products/${id}/`);
  }

  async adjustStock(id: number, data: {
    quantity: number;
    movement_type: 'in' | 'out' | 'adjustment';
    notes?: string;
    reference_number?: string;
  }) {
    return apiClient.post(`/inventory/products/${id}/adjust_stock/`, data);
  }

  async getLowStockProducts() {
    return apiClient.get('/inventory/products/low_stock/');
  }

  async getOutOfStockProducts() {
    return apiClient.get('/inventory/products/out_of_stock/');
  }

  async getStockAlerts() {
    return apiClient.get('/inventory/products/stock_alerts/');
  }

  // Categories
  async getCategories(params?: {
    search?: string;
    parent?: number;
    ordering?: string;
  }) {
    return apiClient.get('/inventory/categories/', params);
  }

  async getCategory(id: number) {
    return apiClient.get(`/inventory/categories/${id}/`);
  }

  async createCategory(data: Partial<ProductCategory>) {
    return apiClient.post('/inventory/categories/', data);
  }

  async updateCategory(id: number, data: Partial<ProductCategory>) {
    return apiClient.patch(`/inventory/categories/${id}/`, data);
  }

  async deleteCategory(id: number) {
    return apiClient.delete(`/inventory/categories/${id}/`);
  }

  async getCategoryTree() {
    return apiClient.get('/inventory/categories/tree/');
  }

  async getCategoryProducts(id: number) {
    return apiClient.get(`/inventory/categories/${id}/products/`);
  }

  // Suppliers
  async getSuppliers(params?: {
    search?: string;
    ordering?: string;
    page?: number;
    page_size?: number;
  }) {
    return apiClient.get('/inventory/suppliers/', params);
  }

  async getSupplier(id: number) {
    return apiClient.get(`/inventory/suppliers/${id}/`);
  }

  async createSupplier(data: Partial<Supplier>) {
    return apiClient.post('/inventory/suppliers/', data);
  }

  async updateSupplier(id: number, data: Partial<Supplier>) {
    return apiClient.patch(`/inventory/suppliers/${id}/`, data);
  }

  async deleteSupplier(id: number) {
    return apiClient.delete(`/inventory/suppliers/${id}/`);
  }

  async getSupplierPurchaseOrders(id: number) {
    return apiClient.get(`/inventory/suppliers/${id}/purchase_orders/`);
  }

  async getSupplierPerformance(id: number) {
    return apiClient.get(`/inventory/suppliers/${id}/performance/`);
  }

  // Stock Movements
  async getStockMovements(params?: {
    product?: number;
    movement_type?: string;
    start_date?: string;
    end_date?: string;
    search?: string;
    ordering?: string;
    page?: number;
    page_size?: number;
  }) {
    return apiClient.get('/inventory/stock-movements/', params);
  }

  async createStockMovement(data: Partial<StockMovement>) {
    return apiClient.post('/inventory/stock-movements/', data);
  }

  async getStockMovementSummary(params?: {
    start_date?: string;
    end_date?: string;
  }) {
    return apiClient.get('/inventory/stock-movements/summary/', params);
  }

  // Purchase Orders
  async getPurchaseOrders(params?: {
    supplier?: number;
    status?: string;
    search?: string;
    ordering?: string;
    page?: number;
    page_size?: number;
  }) {
    return apiClient.get('/inventory/purchase-orders/', params);
  }

  async getPurchaseOrder(id: number) {
    return apiClient.get(`/inventory/purchase-orders/${id}/`);
  }

  async createPurchaseOrder(data: Partial<PurchaseOrder>) {
    return apiClient.post('/inventory/purchase-orders/', data);
  }

  async updatePurchaseOrder(id: number, data: Partial<PurchaseOrder>) {
    return apiClient.patch(`/inventory/purchase-orders/${id}/`, data);
  }

  async deletePurchaseOrder(id: number) {
    return apiClient.delete(`/inventory/purchase-orders/${id}/`);
  }

  async addPurchaseOrderItem(id: number, data: Partial<PurchaseOrderItem>) {
    return apiClient.post(`/inventory/purchase-orders/${id}/add_item/`, data);
  }

  async changePurchaseOrderStatus(id: number, status: string) {
    return apiClient.post(`/inventory/purchase-orders/${id}/change_status/`, { status });
  }

  async getPendingPurchaseOrders() {
    return apiClient.get('/inventory/purchase-orders/pending/');
  }

  // Purchase Order Items
  async getPurchaseOrderItems(params?: {
    purchase_order?: number;
    product?: number;
    ordering?: string;
  }) {
    return apiClient.get('/inventory/purchase-order-items/', params);
  }

  async getPurchaseOrderItem(id: number) {
    return apiClient.get(`/inventory/purchase-order-items/${id}/`);
  }

  async createPurchaseOrderItem(data: Partial<PurchaseOrderItem>) {
    return apiClient.post('/inventory/purchase-order-items/', data);
  }

  async updatePurchaseOrderItem(id: number, data: Partial<PurchaseOrderItem>) {
    return apiClient.patch(`/inventory/purchase-order-items/${id}/`, data);
  }

  async deletePurchaseOrderItem(id: number) {
    return apiClient.delete(`/inventory/purchase-order-items/${id}/`);
  }

  // Dashboard
  async getInventorySummary() {
    return apiClient.get('/inventory/dashboard/summary/');
  }

  async getDashboardStockAlerts() {
    return apiClient.get('/inventory/dashboard/stock_alerts/');
  }
}

export const inventoryService = new InventoryService();
