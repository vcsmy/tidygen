# Sales Management Module

## Overview

The Sales Management module provides comprehensive functionality for managing the entire sales lifecycle, from lead generation to order fulfillment and invoicing. This module is designed to support multi-tenant organizations with robust customer relationship management, sales order processing, and financial tracking capabilities.

## Features

### Customer Management
- **Customer Profiles**: Complete customer information including contact details, business information, and financial terms
- **Contact Management**: Multiple contacts per customer with primary contact designation
- **Customer Classification**: Business type categorization and status management
- **Credit Management**: Credit limits, payment terms, and outstanding balance tracking
- **Customer Analytics**: Sales history, order patterns, and performance metrics

### Sales Order Management
- **Order Processing**: Complete sales order lifecycle from draft to delivery
- **Approval Workflow**: Multi-level approval process with notes and tracking
- **Item Management**: Detailed product specifications, quantities, and pricing
- **Shipping Tracking**: Delivery status, tracking numbers, and shipping methods
- **Priority Management**: Order prioritization and delivery scheduling

### Invoicing System
- **Invoice Generation**: Automatic invoice creation from sales orders
- **Payment Tracking**: Payment recording, partial payments, and outstanding balances
- **Status Management**: Invoice lifecycle from draft to paid
- **Overdue Monitoring**: Automatic overdue status updates and notifications
- **Payment Methods**: Support for various payment methods and reference tracking

### Lead Management
- **Lead Capture**: Comprehensive lead information and source tracking
- **Lead Scoring**: Automated scoring based on contact information, estimated value, and source
- **Assignment System**: Sales representative assignment and workload management
- **Follow-up Tracking**: Scheduled follow-ups and contact history
- **Lead Conversion**: Seamless conversion from leads to opportunities

### Opportunity Management
- **Sales Pipeline**: Stage-based opportunity tracking and management
- **Probability Assessment**: Win probability estimation and forecasting
- **Value Tracking**: Estimated and actual opportunity values
- **Timeline Management**: Expected and actual close dates
- **Performance Metrics**: Sales representative performance and win rates

### Dashboard & Analytics
- **Sales Summary**: Key performance indicators and metrics
- **Customer Analytics**: Customer performance and behavior analysis
- **Revenue Analysis**: Revenue trends, category breakdown, and payment methods
- **Sales Performance**: Representative performance metrics and rankings
- **Forecasting**: Sales pipeline analysis and revenue projections

## API Endpoints

### Customers
- `GET /api/sales/customers/` - List all customers
- `POST /api/sales/customers/` - Create new customer
- `GET /api/sales/customers/{id}/` - Get customer details
- `PUT /api/sales/customers/{id}/` - Update customer
- `DELETE /api/sales/customers/{id}/` - Delete customer
- `GET /api/sales/customers/{id}/sales-orders/` - Get customer orders
- `GET /api/sales/customers/{id}/invoices/` - Get customer invoices
- `GET /api/sales/customers/{id}/opportunities/` - Get customer opportunities
- `GET /api/sales/customers/active-customers/` - Get active customers
- `GET /api/sales/customers/top-customers/` - Get top customers
- `GET /api/sales/customers/credit-limit-exceeded/` - Get customers exceeding credit limit

### Customer Contacts
- `GET /api/sales/customer-contacts/` - List all contacts
- `POST /api/sales/customer-contacts/` - Create new contact
- `GET /api/sales/customer-contacts/{id}/` - Get contact details
- `PUT /api/sales/customer-contacts/{id}/` - Update contact
- `DELETE /api/sales/customer-contacts/{id}/` - Delete contact

### Sales Orders
- `GET /api/sales/sales-orders/` - List all orders
- `POST /api/sales/sales-orders/` - Create new order
- `GET /api/sales/sales-orders/{id}/` - Get order details
- `PUT /api/sales/sales-orders/{id}/` - Update order
- `DELETE /api/sales/sales-orders/{id}/` - Delete order
- `POST /api/sales/sales-orders/{id}/approve/` - Approve order
- `POST /api/sales/sales-orders/{id}/confirm/` - Confirm order
- `POST /api/sales/sales-orders/{id}/ship-order/` - Ship order
- `GET /api/sales/sales-orders/{id}/items/` - Get order items
- `GET /api/sales/sales-orders/pending-approval/` - Get pending approval orders
- `GET /api/sales/sales-orders/approved-orders/` - Get approved orders
- `GET /api/sales/sales-orders/overdue-orders/` - Get overdue orders

### Sales Order Items
- `GET /api/sales/sales-order-items/` - List all order items
- `POST /api/sales/sales-order-items/` - Create new item
- `GET /api/sales/sales-order-items/{id}/` - Get item details
- `PUT /api/sales/sales-order-items/{id}/` - Update item
- `DELETE /api/sales/sales-order-items/{id}/` - Delete item
- `POST /api/sales/sales-order-items/{id}/ship-item/` - Ship item

### Sales Invoices
- `GET /api/sales/sales-invoices/` - List all invoices
- `POST /api/sales/sales-invoices/` - Create new invoice
- `GET /api/sales/sales-invoices/{id}/` - Get invoice details
- `PUT /api/sales/sales-invoices/{id}/` - Update invoice
- `DELETE /api/sales/sales-invoices/{id}/` - Delete invoice
- `POST /api/sales/sales-invoices/{id}/send-invoice/` - Send invoice
- `POST /api/sales/sales-invoices/{id}/record-payment/` - Record payment
- `GET /api/sales/sales-invoices/{id}/items/` - Get invoice items
- `GET /api/sales/sales-invoices/overdue-invoices/` - Get overdue invoices
- `GET /api/sales/sales-invoices/paid-invoices/` - Get paid invoices

### Sales Invoice Items
- `GET /api/sales/sales-invoice-items/` - List all invoice items
- `POST /api/sales/sales-invoice-items/` - Create new item
- `GET /api/sales/sales-invoice-items/{id}/` - Get item details
- `PUT /api/sales/sales-invoice-items/{id}/` - Update item
- `DELETE /api/sales/sales-invoice-items/{id}/` - Delete item

### Sales Leads
- `GET /api/sales/sales-leads/` - List all leads
- `POST /api/sales/sales-leads/` - Create new lead
- `GET /api/sales/sales-leads/{id}/` - Get lead details
- `PUT /api/sales/sales-leads/{id}/` - Update lead
- `DELETE /api/sales/sales-leads/{id}/` - Delete lead
- `POST /api/sales/sales-leads/{id}/assign-representative/` - Assign representative
- `POST /api/sales/sales-leads/{id}/update-status/` - Update lead status
- `GET /api/sales/sales-leads/qualified-leads/` - Get qualified leads
- `GET /api/sales/sales-leads/overdue-follow-ups/` - Get overdue follow-ups

### Sales Opportunities
- `GET /api/sales/sales-opportunities/` - List all opportunities
- `POST /api/sales/sales-opportunities/` - Create new opportunity
- `GET /api/sales/sales-opportunities/{id}/` - Get opportunity details
- `PUT /api/sales/sales-opportunities/{id}/` - Update opportunity
- `DELETE /api/sales/sales-opportunities/{id}/` - Delete opportunity
- `POST /api/sales/sales-opportunities/{id}/update-stage/` - Update opportunity stage
- `GET /api/sales/sales-opportunities/won-opportunities/` - Get won opportunities
- `GET /api/sales/sales-opportunities/overdue-opportunities/` - Get overdue opportunities

### Dashboard
- `GET /api/sales/dashboard/summary/` - Get sales summary
- `GET /api/sales/dashboard/customer-summary/` - Get customer summary
- `GET /api/sales/dashboard/sales-order-summary/` - Get order summary
- `GET /api/sales/dashboard/invoice-summary/` - Get invoice summary
- `GET /api/sales/dashboard/lead-summary/` - Get lead summary
- `GET /api/sales/dashboard/opportunity-summary/` - Get opportunity summary
- `GET /api/sales/dashboard/revenue-analysis/` - Get revenue analysis
- `GET /api/sales/dashboard/sales-performance/` - Get sales performance

## Models

### Customer
- **Basic Information**: Name, customer code, type, status
- **Contact Information**: Contact person, email, phone, website
- **Address Information**: Billing and shipping addresses
- **Business Information**: Tax ID, registration number, industry, company size
- **Financial Information**: Credit limit, payment terms, currency, discount rate
- **Sales Information**: Sales representative, lead source, lead score
- **Analytics**: Total orders, total sales, average order value, outstanding balance

### CustomerContact
- **Contact Details**: Name, title, email, phone, mobile
- **Relationship**: Primary contact designation, department
- **Notes**: Additional information and notes

### SalesOrder
- **Order Information**: Order number, customer, status, priority
- **Dates**: Order date, expected delivery, actual delivery
- **Financial Information**: Subtotal, tax, shipping, discount, total amount
- **Approval Information**: Created by, approved by, approval date, notes
- **Shipping Information**: Address, method, tracking number, notes
- **Analytics**: Items count, completion percentage, overdue status

### SalesOrderItem
- **Item Details**: Product, description, quantity, unit price
- **Shipping Information**: Shipped quantity, delivery dates
- **Financial Information**: Total price, tax, discount
- **Status Information**: Item status and shipping progress
- **Analytics**: Remaining quantity, shipping status

### SalesInvoice
- **Invoice Information**: Invoice number, customer, sales order, status
- **Dates**: Invoice date, due date, payment date
- **Financial Information**: Subtotal, tax, shipping, discount, total, paid, balance
- **Payment Information**: Terms, method, reference number
- **Analytics**: Items count, payment percentage, overdue status

### SalesInvoiceItem
- **Item Details**: Product, description, quantity, unit price
- **Financial Information**: Total price, tax rate, discount rate
- **Notes**: Additional information

### SalesLead
- **Lead Information**: Lead number, company name, contact person
- **Contact Details**: Email, phone
- **Lead Details**: Status, source, lead score, estimated value
- **Assignment**: Sales representative, assigned date
- **Follow-up**: Last contact date, next follow-up date
- **Analytics**: Overdue follow-up status

### SalesOpportunity
- **Opportunity Information**: Opportunity number, title, description
- **Customer & Lead**: Customer relationship, lead source
- **Stage Management**: Current stage, probability
- **Financial Information**: Estimated value, actual value, currency
- **Timeline**: Expected close date, actual close date
- **Assignment**: Sales representative, assigned date
- **Analytics**: Overdue status, days in current stage

## Business Logic

### Automatic Calculations
- **Order Totals**: Automatic calculation of subtotals, taxes, and final amounts
- **Invoice Balances**: Real-time balance calculation based on payments
- **Lead Scoring**: Automated scoring based on multiple factors
- **Status Updates**: Automatic status changes based on business rules

### Workflow Management
- **Order Approval**: Multi-step approval process with validation
- **Shipping Process**: Item-level shipping with status updates
- **Payment Processing**: Payment recording with automatic status updates
- **Lead Conversion**: Seamless transition from leads to opportunities

### Data Validation
- **Credit Limits**: Validation against customer credit limits
- **Quantity Checks**: Validation of shipped quantities against ordered amounts
- **Date Validation**: Validation of delivery and payment dates
- **Status Transitions**: Validation of status change workflows

## Security

### Multi-tenancy
- **Organization Isolation**: All data is scoped to the user's organization
- **User Permissions**: Role-based access control for different user types
- **Data Privacy**: Customer and financial data isolation between organizations

### Authentication & Authorization
- **JWT Authentication**: Secure token-based authentication
- **Permission Checks**: Organization membership validation
- **API Security**: Protected endpoints with proper authentication

## Performance

### Database Optimization
- **Indexed Fields**: Optimized database indexes for common queries
- **Efficient Queries**: Optimized database queries with proper joins
- **Caching Strategy**: Strategic caching for frequently accessed data

### API Performance
- **Pagination**: Efficient pagination for large datasets
- **Filtering**: Advanced filtering capabilities with database optimization
- **Search**: Full-text search with optimized database queries

## Usage Examples

### Creating a Customer
```python
from apps.sales.models import Customer

customer = Customer.objects.create(
    organization=user.organization,
    name='Acme Corporation',
    customer_type='business',
    status='active',
    contact_person='John Smith',
    email='john@acme.com',
    phone='+1234567890',
    credit_limit=10000.00
)
```

### Creating a Sales Order
```python
from apps.sales.models import SalesOrder, SalesOrderItem

order = SalesOrder.objects.create(
    organization=user.organization,
    customer=customer,
    order_date=date.today(),
    expected_delivery_date=date.today() + timedelta(days=7),
    created_by=user
)

item = SalesOrderItem.objects.create(
    sales_order=order,
    product=product,
    quantity=5,
    unit_price=100.00
)
```

### Recording a Payment
```python
from apps.sales.models import SalesInvoice

invoice = SalesInvoice.objects.get(invoice_number='INV-000001')
invoice.record_payment(
    payment_amount=300.00,
    payment_method='Credit Card',
    reference_number='REF-001'
)
```

## Configuration

### Django Settings
```python
INSTALLED_APPS = [
    # ... other apps
    'apps.sales',
]

# Sales-specific settings
SALES_SETTINGS = {
    'DEFAULT_CURRENCY': 'USD',
    'AUTO_APPROVE_ORDERS': False,
    'LEAD_SCORING_ENABLED': True,
    'OVERDUE_NOTIFICATION_DAYS': 7,
}
```

### Environment Variables
```bash
# Sales module configuration
SALES_DEFAULT_CURRENCY=USD
SALES_AUTO_APPROVE_ORDERS=false
SALES_LEAD_SCORING_ENABLED=true
SALES_OVERDUE_NOTIFICATION_DAYS=7
```

## Testing

### Running Tests
```bash
# Run all sales tests
python manage.py test apps.sales

# Run specific test classes
python manage.py test apps.sales.tests.SalesModelsTestCase
python manage.py test apps.sales.tests.SalesAPITestCase

# Run with coverage
coverage run --source='apps.sales' manage.py test apps.sales
coverage report
```

### Test Coverage
The Sales module includes comprehensive test coverage for:
- **Model Tests**: All model creation, validation, and business logic
- **API Tests**: All API endpoints, CRUD operations, and business actions
- **Integration Tests**: End-to-end workflows and data relationships
- **Edge Cases**: Error handling, validation, and boundary conditions

## Future Enhancements

### Planned Features
- **Advanced Analytics**: Machine learning-based sales forecasting
- **Integration**: CRM system integration and data synchronization
- **Notifications**: Automated email and SMS notifications
- **Reporting**: Advanced reporting and business intelligence
- **Mobile App**: Mobile-optimized sales management interface

### Performance Improvements
- **Caching**: Redis-based caching for frequently accessed data
- **Async Processing**: Background task processing for heavy operations
- **Database Optimization**: Advanced database indexing and query optimization
- **API Optimization**: GraphQL implementation for flexible data queries

## Support

### Documentation
- **API Documentation**: Complete API reference with examples
- **User Guides**: Step-by-step user guides for common tasks
- **Developer Docs**: Technical documentation for developers
- **Video Tutorials**: Visual guides for complex workflows

### Community
- **Issue Tracking**: GitHub issues for bug reports and feature requests
- **Discussion Forum**: Community forum for questions and discussions
- **Contributions**: Guidelines for contributing to the module
- **Code Reviews**: Peer review process for all contributions

## License

This module is part of the TidyGen ERP platform and follows the same licensing terms as the main project.
