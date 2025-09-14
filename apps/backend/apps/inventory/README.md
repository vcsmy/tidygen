# Inventory Management Module

## Overview

The Inventory Management module provides comprehensive functionality for managing products, stock levels, suppliers, and purchase orders in a self-hosted ERP system. It includes real-time stock tracking, automated alerts, and integrated procurement workflows.

## Features

### 🏷️ Product Management
- **Product Catalog**: Complete product information with SKU, descriptions, pricing, and specifications
- **Category Hierarchy**: Hierarchical product categorization with unlimited nesting levels
- **Stock Tracking**: Real-time inventory levels with minimum/maximum stock thresholds
- **Digital Products**: Support for both physical and digital product types
- **Barcode Support**: Integration with barcode scanning systems

### 📦 Stock Management
- **Stock Movements**: Track all inventory changes (in, out, transfer, adjustment)
- **Automated Alerts**: Low stock and out-of-stock notifications
- **Stock Forecasting**: Predict stockout dates based on historical movement patterns
- **Audit Trail**: Complete history of all stock changes with timestamps

### 🏢 Supplier Management
- **Supplier Directory**: Comprehensive supplier information and contact details
- **Performance Metrics**: Track supplier performance, delivery times, and order history
- **Payment Terms**: Manage supplier payment terms and conditions
- **Spend Analysis**: Analyze total spend and order patterns by supplier

### 📋 Purchase Order Management
- **Order Creation**: Streamlined purchase order creation with automatic numbering
- **Item Management**: Add, modify, and remove items from purchase orders
- **Status Tracking**: Track order status from draft to received
- **Delivery Scheduling**: Manage expected delivery dates and track on-time performance

### 📊 Dashboard & Analytics
- **Inventory Summary**: Overview of total products, categories, and stock value
- **Stock Alerts**: Real-time notifications for low stock and out-of-stock items
- **Movement Analytics**: Stock movement summaries with date range filtering
- **Performance Metrics**: Key performance indicators for inventory operations

## API Endpoints

### Products
- `GET /api/v1/inventory/products/` - List all products
- `POST /api/v1/inventory/products/` - Create new product
- `GET /api/v1/inventory/products/{id}/` - Get product details
- `PUT /api/v1/inventory/products/{id}/` - Update product
- `DELETE /api/v1/inventory/products/{id}/` - Delete product
- `POST /api/v1/inventory/products/{id}/adjust_stock/` - Adjust stock levels
- `GET /api/v1/inventory/products/low_stock/` - Get low stock products
- `GET /api/v1/inventory/products/out_of_stock/` - Get out of stock products
- `GET /api/v1/inventory/products/stock_alerts/` - Get stock alerts

### Product Categories
- `GET /api/v1/inventory/categories/` - List all categories
- `POST /api/v1/inventory/categories/` - Create new category
- `GET /api/v1/inventory/categories/{id}/` - Get category details
- `PUT /api/v1/inventory/categories/{id}/` - Update category
- `DELETE /api/v1/inventory/categories/{id}/` - Delete category
- `GET /api/v1/inventory/categories/{id}/products/` - Get products in category
- `GET /api/v1/inventory/categories/tree/` - Get category tree structure

### Stock Movements
- `GET /api/v1/inventory/stock-movements/` - List all stock movements
- `POST /api/v1/inventory/stock-movements/` - Create new stock movement
- `GET /api/v1/inventory/stock-movements/{id}/` - Get movement details
- `PUT /api/v1/inventory/stock-movements/{id}/` - Update movement
- `DELETE /api/v1/inventory/stock-movements/{id}/` - Delete movement
- `GET /api/v1/inventory/stock-movements/summary/` - Get movement summary

### Suppliers
- `GET /api/v1/inventory/suppliers/` - List all suppliers
- `POST /api/v1/inventory/suppliers/` - Create new supplier
- `GET /api/v1/inventory/suppliers/{id}/` - Get supplier details
- `PUT /api/v1/inventory/suppliers/{id}/` - Update supplier
- `DELETE /api/v1/inventory/suppliers/{id}/` - Delete supplier
- `GET /api/v1/inventory/suppliers/{id}/purchase_orders/` - Get supplier orders
- `GET /api/v1/inventory/suppliers/{id}/performance/` - Get supplier performance

### Purchase Orders
- `GET /api/v1/inventory/purchase-orders/` - List all purchase orders
- `POST /api/v1/inventory/purchase-orders/` - Create new purchase order
- `GET /api/v1/inventory/purchase-orders/{id}/` - Get order details
- `PUT /api/v1/inventory/purchase-orders/{id}/` - Update order
- `DELETE /api/v1/inventory/purchase-orders/{id}/` - Delete order
- `POST /api/v1/inventory/purchase-orders/{id}/add_item/` - Add item to order
- `POST /api/v1/inventory/purchase-orders/{id}/change_status/` - Change order status
- `GET /api/v1/inventory/purchase-orders/pending/` - Get pending orders

### Purchase Order Items
- `GET /api/v1/inventory/purchase-order-items/` - List all order items
- `POST /api/v1/inventory/purchase-order-items/` - Create new order item
- `GET /api/v1/inventory/purchase-order-items/{id}/` - Get item details
- `PUT /api/v1/inventory/purchase-order-items/{id}/` - Update item
- `DELETE /api/v1/inventory/purchase-order-items/{id}/` - Delete item

### Dashboard
- `GET /api/v1/inventory/dashboard/summary/` - Get inventory summary
- `GET /api/v1/inventory/dashboard/stock_alerts/` - Get stock alerts

## Models

### Product
- Basic information (name, SKU, description)
- Pricing (cost price, selling price)
- Stock levels (current, minimum, maximum)
- Product details (weight, dimensions, barcode, image)
- Status flags (active, digital)
- Organization relationship

### ProductCategory
- Hierarchical structure with parent-child relationships
- Organization isolation
- Product count tracking

### StockMovement
- Movement types (in, out, transfer, adjustment)
- Quantity tracking
- Reference numbers and notes
- Timestamp and audit trail

### Supplier
- Contact information
- Payment terms
- Organization relationship
- Performance metrics

### PurchaseOrder
- Order details and status tracking
- Supplier relationship
- Delivery scheduling
- Automatic order numbering
- Total amount calculation

### PurchaseOrderItem
- Item details and quantities
- Pricing information
- Automatic total calculation

## Business Logic

### Stock Management
- **Automatic Stock Updates**: Stock levels are automatically updated when movements are created
- **Stock Alerts**: Low stock and out-of-stock alerts are generated automatically
- **Stock Forecasting**: Predicts stockout dates based on historical movement patterns
- **Movement Validation**: Prevents negative stock levels and validates movement types

### Purchase Order Management
- **Automatic Numbering**: Purchase orders receive sequential order numbers
- **Total Calculation**: Order totals are automatically calculated and updated
- **Status Management**: Order status changes are tracked and validated
- **Item Management**: Items can be added, modified, and removed with automatic total updates

### Multi-tenancy
- **Organization Isolation**: All data is automatically filtered by user's organization
- **Permission Control**: Access is controlled through organization membership
- **Data Segregation**: Complete separation of data between organizations

## Signals

The module uses Django signals to maintain data consistency:

- **Stock Movement Signals**: Automatically update product stock levels
- **Purchase Order Signals**: Automatically recalculate order totals
- **Product Signals**: Create initial stock movements for new products

## Admin Interface

Comprehensive Django admin interface with:

- **Product Management**: Full CRUD operations with stock status indicators
- **Category Management**: Hierarchical category management
- **Stock Movement Tracking**: Complete movement history with filtering
- **Supplier Management**: Supplier information with performance metrics
- **Purchase Order Management**: Order management with inline item editing

## Testing

The module includes comprehensive test coverage:

- **Model Tests**: Test model creation, validation, and business logic
- **API Tests**: Test all API endpoints and functionality
- **Permission Tests**: Test organization isolation and access control
- **Business Logic Tests**: Test stock management and purchase order workflows

## Usage Examples

### Creating a Product
```python
from apps.inventory.models import Product, ProductCategory

# Create category
category = ProductCategory.objects.create(
    name='Electronics',
    organization=user.organization
)

# Create product
product = Product.objects.create(
    name='Smartphone',
    sku='PHONE-001',
    category=category,
    cost_price=200.00,
    selling_price=299.99,
    current_stock=50,
    min_stock_level=10,
    max_stock_level=100,
    organization=user.organization
)
```

### Adjusting Stock
```python
from apps.inventory.models import StockMovement

# Add stock
movement = StockMovement.objects.create(
    product=product,
    movement_type='in',
    quantity=25,
    reference_number='PO-001',
    notes='Received from supplier'
)

# Stock is automatically updated
product.refresh_from_db()
print(product.current_stock)  # 75
```

### Creating Purchase Order
```python
from apps.inventory.models import PurchaseOrder, PurchaseOrderItem

# Create purchase order
po = PurchaseOrder.objects.create(
    supplier=supplier,
    order_date=date.today(),
    expected_delivery=date.today() + timedelta(days=7),
    organization=user.organization
)

# Add items
item = PurchaseOrderItem.objects.create(
    purchase_order=po,
    product=product,
    quantity=10,
    unit_price=200.00
)

# Total is automatically calculated
po.refresh_from_db()
print(po.total_amount)  # 2000.00
```

## Configuration

### Settings
The module integrates with the core Django settings and requires:

- `django_filters` for advanced filtering
- `django_rest_framework` for API functionality
- Proper database configuration for decimal fields
- File storage configuration for product images

### Permissions
- **IsAuthenticated**: Users must be authenticated
- **IsOrganizationMember**: Users must belong to the organization

### Filters
Advanced filtering is available for all models:

- **Text Search**: Search by name, description, SKU, etc.
- **Range Filters**: Filter by price, stock levels, dates
- **Status Filters**: Filter by active status, stock status, order status
- **Relationship Filters**: Filter by category, supplier, organization

## Performance Considerations

- **Database Indexes**: Proper indexing on frequently queried fields
- **Query Optimization**: Efficient queries with select_related and prefetch_related
- **Caching**: Consider caching for dashboard summaries and stock alerts
- **Pagination**: API endpoints support pagination for large datasets

## Security Features

- **Organization Isolation**: Complete data separation between organizations
- **Permission Control**: Role-based access control through organization membership
- **Input Validation**: Comprehensive validation of all input data
- **Audit Trail**: Complete tracking of all data changes

## Future Enhancements

- **Barcode Integration**: Advanced barcode scanning and management
- **Inventory Forecasting**: Machine learning-based demand forecasting
- **Supplier Portal**: Self-service portal for suppliers
- **Mobile App**: Mobile inventory management application
- **Integration APIs**: Integration with external systems and marketplaces
