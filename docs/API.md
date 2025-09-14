# API Documentation

## 🌐 **API Overview**

The TidyGen ERP system provides a comprehensive RESTful API built with Django REST Framework. All endpoints follow REST conventions and return JSON responses.

### **Base URL**
- **Development**: `http://localhost:8000/api`
- **Production**: `https://your-domain.com/api`

### **Authentication**
The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## 🔐 **Authentication Endpoints**

### **Login**
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@tidygen-demo.com",
    "first_name": "Admin",
    "last_name": "User",
    "is_active": true,
    "date_joined": "2024-01-01T00:00:00Z"
  }
}
```

### **Register**
```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123",
  "password_confirm": "password123",
  "first_name": "New",
  "last_name": "User"
}
```

### **Refresh Token**
```http
POST /api/auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### **Logout**
```http
POST /api/auth/logout/
Authorization: Bearer <token>
```

## 👥 **User Management**

### **Users**
```http
# List users
GET /api/users/

# Create user
POST /api/users/
{
  "username": "newuser",
  "email": "user@example.com",
  "first_name": "New",
  "last_name": "User",
  "is_active": true
}

# Get user
GET /api/users/{id}/

# Update user
PUT /api/users/{id}/
PATCH /api/users/{id}/

# Delete user
DELETE /api/users/{id}/
```

### **Roles**
```http
# List roles
GET /api/roles/

# Create role
POST /api/roles/
{
  "name": "manager",
  "display_name": "Manager",
  "permissions": [1, 2, 3]
}

# Get role
GET /api/roles/{id}/

# Update role
PUT /api/roles/{id}/
PATCH /api/roles/{id}/

# Delete role
DELETE /api/roles/{id}/
```

### **Permissions**
```http
# List permissions
GET /api/permissions/

# Create permission
POST /api/permissions/
{
  "name": "manage_users",
  "codename": "manage_users"
}

# Get permission
GET /api/permissions/{id}/

# Update permission
PUT /api/permissions/{id}/
PATCH /api/permissions/{id}/

# Delete permission
DELETE /api/permissions/{id}/
```

## 💰 **Finance Management**

### **Accounts**
```http
# List accounts
GET /api/finance/accounts/

# Create account
POST /api/finance/accounts/
{
  "name": "Cash Account",
  "account_type": "asset",
  "category": "Current Assets",
  "balance": 10000.00
}

# Get account
GET /api/finance/accounts/{id}/

# Update account
PUT /api/finance/accounts/{id}/
PATCH /api/finance/accounts/{id}/

# Delete account
DELETE /api/finance/accounts/{id}/
```

### **Invoices**
```http
# List invoices
GET /api/finance/invoices/

# Create invoice
POST /api/finance/invoices/
{
  "invoice_number": "INV-2024-001",
  "customer_name": "Customer Name",
  "customer_email": "customer@example.com",
  "amount": 1000.00,
  "status": "draft",
  "due_date": "2024-12-31"
}

# Get invoice
GET /api/finance/invoices/{id}/

# Update invoice
PUT /api/finance/invoices/{id}/
PATCH /api/finance/invoices/{id}/

# Delete invoice
DELETE /api/finance/invoices/{id}/
```

### **Payments**
```http
# List payments
GET /api/finance/payments/

# Create payment
POST /api/finance/payments/
{
  "payment_number": "PAY-2024-001",
  "customer_name": "Customer Name",
  "amount": 1000.00,
  "payment_method": "credit_card",
  "status": "completed",
  "payment_date": "2024-01-01"
}

# Get payment
GET /api/finance/payments/{id}/

# Update payment
PUT /api/finance/payments/{id}/
PATCH /api/finance/payments/{id}/

# Delete payment
DELETE /api/finance/payments/{id}/
```

## 📦 **Inventory Management**

### **Products**
```http
# List products
GET /api/inventory/products/

# Create product
POST /api/inventory/products/
{
  "name": "Product Name",
  "sku": "PROD-001",
  "description": "Product description",
  "category": 1,
  "cost_price": 10.00,
  "selling_price": 20.00,
  "current_stock": 100,
  "min_stock_level": 10,
  "max_stock_level": 200
}

# Get product
GET /api/inventory/products/{id}/

# Update product
PUT /api/inventory/products/{id}/
PATCH /api/inventory/products/{id}/

# Delete product
DELETE /api/inventory/products/{id}/
```

### **Stock Items**
```http
# List stock items
GET /api/inventory/stock-items/

# Create stock item
POST /api/inventory/stock-items/
{
  "product": 1,
  "warehouse": 1,
  "quantity": 100,
  "reserved_quantity": 0,
  "available_quantity": 100
}

# Get stock item
GET /api/inventory/stock-items/{id}/

# Update stock item
PUT /api/inventory/stock-items/{id}/
PATCH /api/inventory/stock-items/{id}/

# Delete stock item
DELETE /api/inventory/stock-items/{id}/
```

### **Warehouses**
```http
# List warehouses
GET /api/inventory/warehouses/

# Create warehouse
POST /api/inventory/warehouses/
{
  "name": "Main Warehouse",
  "location": "San Francisco, CA",
  "description": "Primary storage facility",
  "capacity": 5000
}

# Get warehouse
GET /api/inventory/warehouses/{id}/

# Update warehouse
PUT /api/inventory/warehouses/{id}/
PATCH /api/inventory/warehouses/{id}/

# Delete warehouse
DELETE /api/inventory/warehouses/{id}/
```

### **Suppliers**
```http
# List suppliers
GET /api/inventory/suppliers/

# Create supplier
POST /api/inventory/suppliers/
{
  "name": "Supplier Name",
  "contact_person": "John Doe",
  "email": "supplier@example.com",
  "phone": "+1-555-0123",
  "address": "123 Supplier Street",
  "city": "San Francisco",
  "state": "CA",
  "country": "USA",
  "postal_code": "94105",
  "payment_terms": "net_30"
}

# Get supplier
GET /api/inventory/suppliers/{id}/

# Update supplier
PUT /api/inventory/suppliers/{id}/
PATCH /api/inventory/suppliers/{id}/

# Delete supplier
DELETE /api/inventory/suppliers/{id}/
```

## 👨‍💼 **HR Management**

### **Employees**
```http
# List employees
GET /api/hr/employees/

# Create employee
POST /api/hr/employees/
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@company.com",
  "employee_id": "EMP-001",
  "department": 1,
  "position": "Software Engineer",
  "salary": 75000.00,
  "hire_date": "2024-01-01",
  "status": "active"
}

# Get employee
GET /api/hr/employees/{id}/

# Update employee
PUT /api/hr/employees/{id}/
PATCH /api/hr/employees/{id}/

# Delete employee
DELETE /api/hr/employees/{id}/
```

### **Departments**
```http
# List departments
GET /api/hr/departments/

# Create department
POST /api/hr/departments/
{
  "name": "Engineering",
  "description": "Software development team"
}

# Get department
GET /api/hr/departments/{id}/

# Update department
PUT /api/hr/departments/{id}/
PATCH /api/hr/departments/{id}/

# Delete department
DELETE /api/hr/departments/{id}/
```

## 🛒 **Sales Management**

### **Customers**
```http
# List customers
GET /api/sales/customers/

# Create customer
POST /api/sales/customers/
{
  "name": "Customer Company",
  "customer_code": "CUST-001",
  "email": "customer@company.com",
  "phone": "+1-555-0123",
  "customer_type": "business",
  "status": "active"
}

# Get customer
GET /api/sales/customers/{id}/

# Update customer
PUT /api/sales/customers/{id}/
PATCH /api/sales/customers/{id}/

# Delete customer
DELETE /api/sales/customers/{id}/
```

### **Sales Orders**
```http
# List sales orders
GET /api/sales/sales-orders/

# Create sales order
POST /api/sales/sales-orders/
{
  "order_number": "SO-2024-001",
  "customer": 1,
  "status": "draft",
  "total_amount": 1000.00,
  "order_date": "2024-01-01"
}

# Get sales order
GET /api/sales/sales-orders/{id}/

# Update sales order
PUT /api/sales/sales-orders/{id}/
PATCH /api/sales/sales-orders/{id}/

# Delete sales order
DELETE /api/sales/sales-orders/{id}/
```

## 🛍️ **Purchasing Management**

### **Vendors**
```http
# List vendors
GET /api/purchasing/vendors/

# Create vendor
POST /api/purchasing/vendors/
{
  "name": "Vendor Company",
  "vendor_code": "VEND-001",
  "email": "vendor@company.com",
  "phone": "+1-555-0123",
  "business_type": "manufacturer",
  "status": "active",
  "payment_terms": "net_30",
  "credit_limit": 50000.00
}

# Get vendor
GET /api/purchasing/vendors/{id}/

# Update vendor
PUT /api/purchasing/vendors/{id}/
PATCH /api/purchasing/vendors/{id}/

# Delete vendor
DELETE /api/purchasing/vendors/{id}/
```

### **Purchase Orders**
```http
# List purchase orders
GET /api/purchasing/purchase-orders/

# Create purchase order
POST /api/purchasing/purchase-orders/
{
  "po_number": "PO-2024-001",
  "vendor": 1,
  "status": "draft",
  "total_amount": 5000.00,
  "order_date": "2024-01-01",
  "expected_delivery_date": "2024-01-15"
}

# Get purchase order
GET /api/purchasing/purchase-orders/{id}/

# Update purchase order
PUT /api/purchasing/purchase-orders/{id}/
PATCH /api/purchasing/purchase-orders/{id}/

# Delete purchase order
DELETE /api/purchasing/purchase-orders/{id}/
```

## ⛓️ **Web3 Integration**

### **Wallets**
```http
# List wallets
GET /api/web3/wallets/

# Create wallet
POST /api/web3/wallets/
{
  "name": "Main Wallet",
  "address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
  "blockchain": "ethereum",
  "wallet_type": "external",
  "is_active": true
}

# Get wallet
GET /api/web3/wallets/{id}/

# Update wallet
PUT /api/web3/wallets/{id}/
PATCH /api/web3/wallets/{id}/

# Delete wallet
DELETE /api/web3/wallets/{id}/
```

### **Blockchain Transactions**
```http
# List transactions
GET /api/web3/transactions/

# Create transaction
POST /api/web3/transactions/
{
  "wallet": 1,
  "tx_hash": "0x1234567890abcdef...",
  "transaction_type": "send",
  "amount": 1.5,
  "status": "confirmed",
  "gas_used": 21000,
  "gas_price": 20.0
}

# Get transaction
GET /api/web3/transactions/{id}/

# Update transaction
PUT /api/web3/transactions/{id}/
PATCH /api/web3/transactions/{id}/

# Delete transaction
DELETE /api/web3/transactions/{id}/
```

## 📊 **Common Query Parameters**

### **Pagination**
```http
GET /api/users/?page=1&page_size=20
```

### **Filtering**
```http
GET /api/products/?category=1&status=active
```

### **Searching**
```http
GET /api/customers/?search=company
```

### **Ordering**
```http
GET /api/orders/?ordering=-created_at
```

## 🔍 **Error Responses**

### **400 Bad Request**
```json
{
  "error": "Validation failed",
  "details": {
    "field_name": ["This field is required."]
  }
}
```

### **401 Unauthorized**
```json
{
  "error": "Authentication credentials were not provided."
}
```

### **403 Forbidden**
```json
{
  "error": "You do not have permission to perform this action."
}
```

### **404 Not Found**
```json
{
  "error": "Not found."
}
```

### **500 Internal Server Error**
```json
{
  "error": "Internal server error."
}
```

## 📚 **Interactive API Documentation**

Access the interactive API documentation at:
- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`

## 🔧 **API Testing**

### **Using curl**
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Get users (with token)
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer <your-token>"
```

### **Using Postman**
1. Import the OpenAPI specification from `/api/schema/`
2. Set up authentication with JWT tokens
3. Test all endpoints with the provided examples

## 🚀 **Rate Limiting**

The API implements rate limiting to prevent abuse:
- **Authenticated users**: 1000 requests per hour
- **Anonymous users**: 100 requests per hour

## 🔒 **Security**

- All endpoints require authentication except login/register
- JWT tokens expire after 1 hour (configurable)
- CORS is configured for frontend domains
- Input validation and sanitization on all endpoints
- SQL injection protection through Django ORM
