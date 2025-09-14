# Purchasing Management Module

## Overview

The Purchasing Management module provides comprehensive procurement and purchasing functionality for the iNEAT ERP system. It handles the complete purchasing lifecycle from initial procurement requests to final receipt of goods, including supplier performance tracking and analytics.

## Features

### 🛒 Purchase Order Management
- **Purchase Order Creation**: Create and manage purchase orders with multiple items
- **Status Tracking**: Track orders through draft, approval, sent, received, and closed states
- **Priority Management**: Set priority levels (low, medium, high, urgent)
- **Approval Workflow**: Built-in approval process with user tracking
- **Financial Tracking**: Automatic calculation of totals, taxes, shipping, and discounts

### 📦 Purchase Receipt Management
- **Goods Receipt**: Record receipt of ordered items
- **Partial Receipts**: Handle partial deliveries and track remaining quantities
- **Condition Tracking**: Record condition of received items
- **Batch Management**: Track batch numbers and expiry dates
- **Receipt Validation**: Ensure received quantities match ordered quantities

### 📋 Procurement Request Management
- **Request Creation**: Create internal procurement requests before purchase orders
- **Approval Workflow**: Multi-level approval process for procurement requests
- **Budget Tracking**: Link requests to budget codes and cost centers
- **Justification**: Require business justification for all requests
- **Conversion**: Convert approved requests to purchase orders

### 🏆 Supplier Performance Management
- **Performance Metrics**: Track on-time delivery, quality, communication, and price competitiveness
- **Rating System**: 5-star rating system for overall supplier performance
- **Historical Tracking**: Maintain performance history over time
- **Performance Alerts**: Identify top and poor performing suppliers
- **Trend Analysis**: Track supplier performance trends

### 📊 Analytics & Reporting
- **Purchase Analytics**: Comprehensive analytics on purchasing patterns
- **Cost Analysis**: Track savings and cost reduction opportunities
- **Supplier Analysis**: Analyze supplier performance and spending
- **Trend Reporting**: Monthly and quarterly trend analysis
- **Dashboard**: Real-time purchasing dashboard with KPIs

## Models

### Core Models

#### PurchaseOrder
- **Purpose**: Main purchase order entity
- **Key Fields**: PO number, supplier, status, priority, dates, financial totals
- **Relationships**: Links to supplier, user, organization, and items

#### PurchaseOrderItem
- **Purpose**: Individual items within a purchase order
- **Key Fields**: Product details, quantities, pricing, delivery dates
- **Features**: Automatic total calculation, quantity tracking

#### PurchaseReceipt
- **Purpose**: Record of goods received
- **Key Fields**: Receipt number, status, received by, dates
- **Relationships**: Links to purchase order and receipt items

#### PurchaseReceiptItem
- **Purpose**: Individual items within a receipt
- **Key Fields**: Quantities received, condition, batch info
- **Features**: Condition tracking, batch management

#### ProcurementRequest
- **Purpose**: Internal procurement requests
- **Key Fields**: Request number, title, justification, status
- **Relationships**: Links to organization, user, and request items

#### ProcurementRequestItem
- **Purpose**: Individual items within a procurement request
- **Key Fields**: Product details, quantities, estimated pricing
- **Features**: Cost estimation, specification tracking

#### SupplierPerformance
- **Purpose**: Supplier performance evaluation
- **Key Fields**: Ratings, delivery metrics, evaluation dates
- **Features**: Automatic overall rating calculation

#### PurchaseAnalytics
- **Purpose**: Purchasing analytics and metrics
- **Key Fields**: Period data, totals, performance metrics
- **Features**: Trend analysis, cost tracking

## API Endpoints

### Purchase Orders
- `GET /api/v1/purchasing/purchase-orders/` - List purchase orders
- `POST /api/v1/purchasing/purchase-orders/` - Create purchase order
- `GET /api/v1/purchasing/purchase-orders/{id}/` - Get purchase order details
- `PUT /api/v1/purchasing/purchase-orders/{id}/` - Update purchase order
- `DELETE /api/v1/purchasing/purchase-orders/{id}/` - Delete purchase order
- `POST /api/v1/purchasing/purchase-orders/{id}/approve/` - Approve purchase order
- `POST /api/v1/purchasing/purchase-orders/{id}/send-to-supplier/` - Send to supplier
- `POST /api/v1/purchasing/purchase-orders/{id}/cancel/` - Cancel purchase order
- `GET /api/v1/purchasing/purchase-orders/analytics/` - Get purchase analytics

### Purchase Receipts
- `GET /api/v1/purchasing/purchase-receipts/` - List purchase receipts
- `POST /api/v1/purchasing/purchase-receipts/` - Create purchase receipt
- `GET /api/v1/purchasing/purchase-receipts/{id}/` - Get receipt details
- `POST /api/v1/purchasing/purchase-receipts/{id}/mark-complete/` - Mark receipt complete

### Procurement Requests
- `GET /api/v1/purchasing/procurement-requests/` - List procurement requests
- `POST /api/v1/purchasing/procurement-requests/` - Create procurement request
- `GET /api/v1/purchasing/procurement-requests/{id}/` - Get request details
- `POST /api/v1/purchasing/procurement-requests/{id}/approve/` - Approve request
- `POST /api/v1/purchasing/procurement-requests/{id}/reject/` - Reject request
- `POST /api/v1/purchasing/procurement-requests/{id}/convert-to-po/` - Convert to PO

### Supplier Performance
- `GET /api/v1/purchasing/supplier-performance/` - List performance records
- `POST /api/v1/purchasing/supplier-performance/` - Create performance record
- `GET /api/v1/purchasing/supplier-performance/top-performers/` - Get top performers
- `GET /api/v1/purchasing/supplier-performance/performance-trends/` - Get trends

### Analytics
- `GET /api/v1/purchasing/analytics/` - List analytics records
- `GET /api/v1/purchasing/analytics/dashboard/` - Get dashboard data

## Usage Examples

### Creating a Purchase Order

```python
from apps.purchasing.models import PurchaseOrder, PurchaseOrderItem
from apps.inventory.models import Product, Supplier

# Create purchase order
po = PurchaseOrder.objects.create(
    organization=organization,
    supplier=supplier,
    requested_by=user,
    status='draft',
    priority='medium',
    notes='Urgent order for Q1 inventory'
)

# Add items
item = PurchaseOrderItem.objects.create(
    purchase_order=po,
    product=product,
    quantity_ordered=100,
    unit_price=Decimal('25.50')
)

# Submit for approval
po.status = 'pending_approval'
po.save()
```

### Processing a Receipt

```python
from apps.purchasing.models import PurchaseReceipt, PurchaseReceiptItem

# Create receipt
receipt = PurchaseReceipt.objects.create(
    purchase_order=purchase_order,
    received_by=user,
    status='pending'
)

# Add received items
receipt_item = PurchaseReceiptItem.objects.create(
    receipt=receipt,
    purchase_order_item=po_item,
    quantity_received=95,  # 5 items short
    condition='good',
    batch_number='BATCH001'
)

# Mark complete
receipt.status = 'complete'
receipt.save()
```

### Evaluating Supplier Performance

```python
from apps.purchasing.models import SupplierPerformance

# Create performance evaluation
performance = SupplierPerformance.objects.create(
    supplier=supplier,
    organization=organization,
    evaluated_by=user,
    on_time_delivery_rate=Decimal('92.5'),
    quality_rating=Decimal('4.2'),
    communication_rating=Decimal('4.0'),
    price_competitiveness=Decimal('3.8'),
    notes='Good supplier, minor delivery delays'
)

# Overall rating automatically calculated as 4.0
```

## Filters

The module provides comprehensive filtering capabilities:

### Purchase Order Filters
- **Search**: Search across PO number, supplier name, reference number
- **Status**: Filter by order status (draft, approved, sent, etc.)
- **Priority**: Filter by priority level
- **Date Range**: Filter by order date or expected delivery date
- **Financial**: Filter by total amount range
- **Special**: Overdue orders, pending approval

### Purchase Receipt Filters
- **Search**: Search across receipt number, PO number, notes
- **Status**: Filter by receipt status
- **Date Range**: Filter by receipt date
- **Related**: Filter by purchase order or received by user

### Procurement Request Filters
- **Search**: Search across request number, title, description
- **Status**: Filter by request status
- **Priority**: Filter by priority level
- **Date Range**: Filter by request date or required date
- **Special**: Urgent requests, overdue requests

### Supplier Performance Filters
- **Search**: Search across supplier name, notes
- **Rating**: Filter by rating ranges
- **Date Range**: Filter by evaluation date
- **Special**: Top performers, poor performers

## Signals

The module includes comprehensive Django signals for automation:

### Purchase Order Signals
- **Pre-save**: Auto-generate PO numbers, set approval dates
- **Post-save**: Update analytics, log changes
- **Post-delete**: Update analytics

### Purchase Order Item Signals
- **Pre-save**: Store product details, calculate totals
- **Post-save**: Update purchase order totals
- **Post-delete**: Update purchase order totals

### Purchase Receipt Signals
- **Pre-save**: Auto-generate receipt numbers
- **Post-save**: Update purchase order status
- **Post-delete**: Update purchase order status

### Receipt Item Signals
- **Post-save**: Update received quantities
- **Post-delete**: Update received quantities

### Procurement Request Signals
- **Pre-save**: Auto-generate request numbers, set review dates
- **Post-save**: Log status changes
- **Post-delete**: Log deletions

### Request Item Signals
- **Pre-save**: Store product details, calculate estimates
- **Post-save**: Update request estimated cost
- **Post-delete**: Update request estimated cost

### Supplier Performance Signals
- **Pre-save**: Calculate overall rating
- **Post-save**: Log evaluations
- **Post-delete**: Log deletions

## Admin Interface

The Django admin interface provides comprehensive management capabilities:

### Purchase Order Admin
- **List View**: PO number, supplier, status, priority, amounts, dates
- **Detail View**: Complete order information with inline items
- **Filters**: Status, priority, supplier, dates
- **Search**: PO number, supplier name, reference number
- **Actions**: Bulk status updates, export functionality

### Purchase Receipt Admin
- **List View**: Receipt number, PO, status, received by, date
- **Detail View**: Complete receipt information with inline items
- **Filters**: Status, date, received by
- **Search**: Receipt number, PO number, notes

### Procurement Request Admin
- **List View**: Request number, title, status, priority, requester, dates
- **Detail View**: Complete request information with inline items
- **Filters**: Status, priority, requester, dates
- **Search**: Request number, title, description

### Supplier Performance Admin
- **List View**: Supplier, ratings, evaluation date
- **Detail View**: Complete performance metrics
- **Filters**: Supplier, evaluation date, evaluator
- **Search**: Supplier name, notes

### Analytics Admin
- **List View**: Period, totals, metrics
- **Detail View**: Complete analytics data
- **Filters**: Period, organization
- **Search**: Organization name

## Testing

The module includes comprehensive test coverage:

### Model Tests
- **PurchaseOrderModelTest**: Test PO creation, number generation, string representation
- **PurchaseOrderItemModelTest**: Test item creation, calculations, product details storage
- **PurchaseReceiptModelTest**: Test receipt creation, number generation
- **ProcurementRequestModelTest**: Test request creation, number generation
- **SupplierPerformanceModelTest**: Test performance creation, rating calculation

### API Tests
- **PurchaseOrderAPITest**: Test all PO API endpoints, status updates, analytics
- **ProcurementRequestAPITest**: Test request API endpoints, approval/rejection
- **SupplierPerformanceAPITest**: Test performance API endpoints, top performers
- **PurchaseAnalyticsAPITest**: Test analytics API endpoints, dashboard

### Integration Tests
- **PurchasingIntegrationTest**: Test complete workflows, supplier performance tracking

## Configuration

### Settings
The module requires the following Django settings:

```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ... other apps
    'apps.purchasing',
]

# Add to URL patterns
urlpatterns = [
    # ... other patterns
    path('api/v1/purchasing/', include('apps.purchasing.urls')),
]
```

### Permissions
The module uses the following permission classes:
- **IsAuthenticated**: User must be logged in
- **IsOrganizationMember**: User must be a member of the organization

### Dependencies
The module depends on:
- **apps.core**: Base models and permissions
- **apps.organizations**: Self-hosted organization support
- **apps.inventory**: Product and supplier models
- **django-filter**: Advanced filtering capabilities
- **django-rest-framework**: API functionality

## Best Practices

### Purchase Order Management
1. **Always validate quantities** before creating purchase orders
2. **Use appropriate priority levels** for urgent orders
3. **Include detailed notes** for complex orders
4. **Set realistic delivery dates** based on supplier capabilities
5. **Track reference numbers** for external system integration

### Receipt Processing
1. **Verify quantities** against purchase orders
2. **Record condition** of received items
3. **Update batch numbers** for traceability
4. **Handle discrepancies** promptly
5. **Complete receipts** in a timely manner

### Supplier Performance
1. **Evaluate regularly** based on objective criteria
2. **Document performance issues** with specific examples
3. **Use consistent rating scales** across all suppliers
4. **Track trends** over time for improvement
5. **Share feedback** with suppliers for improvement

### Analytics Usage
1. **Monitor key metrics** regularly
2. **Set up alerts** for threshold breaches
3. **Analyze trends** to identify opportunities
4. **Use data** for supplier negotiations
5. **Report findings** to management

## Troubleshooting

### Common Issues

#### PO Number Generation
- **Issue**: Duplicate PO numbers
- **Solution**: Check for concurrent creation, ensure proper locking

#### Status Updates
- **Issue**: Status not updating automatically
- **Solution**: Check signals are properly connected, verify model methods

#### Analytics Calculation
- **Issue**: Analytics not updating
- **Solution**: Check signal handlers, verify organization filtering

#### Permission Errors
- **Issue**: Access denied errors
- **Solution**: Verify user organization membership, check permissions

### Debug Mode
Enable debug logging for detailed signal and calculation information:

```python
LOGGING = {
    'loggers': {
        'apps.purchasing': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

## Future Enhancements

### Planned Features
1. **Automated Reordering**: Based on inventory levels and consumption patterns
2. **Supplier Portal**: Allow suppliers to view and update order status
3. **Contract Management**: Link purchase orders to supplier contracts
4. **Budget Integration**: Real-time budget checking and allocation
5. **Mobile App**: Mobile interface for receipt processing
6. **AI Recommendations**: AI-powered supplier and product recommendations
7. **Blockchain Integration**: Immutable purchase order records
8. **Advanced Analytics**: Machine learning for demand forecasting

### Integration Opportunities
1. **Accounting Systems**: Direct integration with accounting software
2. **Inventory Management**: Real-time inventory updates
3. **Supplier Systems**: EDI integration with supplier systems
4. **Payment Processing**: Automated payment workflows
5. **Document Management**: Digital document storage and retrieval

## Support

For support and questions:
- **Documentation**: Check this README and inline code documentation
- **Issues**: Report bugs and feature requests through the issue tracker
- **Community**: Join the community forum for discussions
- **Training**: Access training materials and video tutorials

## License

This module is part of the iNEAT ERP system and follows the same licensing terms.
