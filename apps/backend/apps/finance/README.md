# Finance Management Module

A comprehensive finance management system for the iNEAT ERP platform that handles invoicing, payments, expenses, budgeting, and financial reporting.

## Features

### 📊 Core Financial Management
- **Chart of Accounts**: Complete accounting structure with asset, liability, equity, revenue, and expense accounts
- **Customer Management**: Track customer information, credit limits, and payment terms
- **Vendor Management**: Manage vendor relationships and payment terms
- **Invoice Management**: Create, send, and track invoices with automatic numbering
- **Payment Processing**: Record and track payments with multiple payment methods
- **Expense Tracking**: Submit, approve, and track business expenses
- **Budget Management**: Create and monitor budgets with category breakdowns
- **Tax Rate Management**: Configure and manage tax rates for different jurisdictions

### 🔄 Automated Operations
- **Recurring Invoices**: Set up automatic invoice generation on schedules
- **Payment Tracking**: Automatic invoice status updates based on payments
- **Budget Monitoring**: Real-time budget tracking against actual expenses
- **Financial Calculations**: Automatic tax calculations and totals
- **Status Workflows**: Automated status transitions for invoices and expenses

### 📈 Analytics & Reporting
- **Financial Dashboard**: Real-time overview of financial health
- **Invoice Analytics**: Payment trends, overdue tracking, and revenue analysis
- **Expense Analytics**: Category breakdowns and spending trends
- **Financial Reports**: Generate comprehensive financial reports
- **KPI Tracking**: Monitor key financial performance indicators

## Models

### Core Models

#### Account
- Chart of accounts for financial tracking
- Supports hierarchical account structure
- Tracks account balances and types

#### Customer
- Customer information and contact details
- Credit limits and payment terms
- Address and tax information

#### Vendor
- Vendor information and contact details
- Payment terms and tax information
- Address and contact person details

#### Invoice
- Customer billing with automatic numbering
- Tax calculations and discount support
- Status tracking (draft, sent, viewed, paid, overdue, cancelled)
- Due date management

#### InvoiceItem
- Line items for invoices
- Quantity, unit price, and total calculations
- Description and product details

#### Payment
- Payment recording with multiple methods
- Reference tracking and bank details
- Automatic invoice status updates

#### Expense
- Business expense tracking
- Category-based organization
- Approval workflow support
- Receipt image storage

#### Budget
- Financial planning and monitoring
- Period-based budgeting
- Real-time spending tracking

#### BudgetItem
- Category-specific budget allocations
- Spending vs. budgeted amount tracking

#### TaxRate
- Configurable tax rates
- Support for different jurisdictions
- Active/inactive status management

#### RecurringInvoice
- Automated invoice generation
- Flexible scheduling (daily, weekly, monthly, quarterly, yearly)
- Template-based invoice creation

#### FinancialReport
- Generated financial reports
- JSON-based report data storage
- Historical report tracking

## API Endpoints

### Accounts
- `GET /api/v1/finance/accounts/` - List accounts
- `POST /api/v1/finance/accounts/` - Create account
- `GET /api/v1/finance/accounts/{id}/` - Get account details
- `PUT /api/v1/finance/accounts/{id}/` - Update account
- `DELETE /api/v1/finance/accounts/{id}/` - Delete account

### Customers
- `GET /api/v1/finance/customers/` - List customers
- `POST /api/v1/finance/customers/` - Create customer
- `GET /api/v1/finance/customers/{id}/` - Get customer details
- `PUT /api/v1/finance/customers/{id}/` - Update customer
- `DELETE /api/v1/finance/customers/{id}/` - Delete customer
- `GET /api/v1/finance/customers/{id}/invoices/` - Get customer invoices
- `GET /api/v1/finance/customers/{id}/payments/` - Get customer payments

### Vendors
- `GET /api/v1/finance/vendors/` - List vendors
- `POST /api/v1/finance/vendors/` - Create vendor
- `GET /api/v1/finance/vendors/{id}/` - Get vendor details
- `PUT /api/v1/finance/vendors/{id}/` - Update vendor
- `DELETE /api/v1/finance/vendors/{id}/` - Delete vendor
- `GET /api/v1/finance/vendors/{id}/expenses/` - Get vendor expenses

### Invoices
- `GET /api/v1/finance/invoices/` - List invoices
- `POST /api/v1/finance/invoices/` - Create invoice
- `GET /api/v1/finance/invoices/{id}/` - Get invoice details
- `PUT /api/v1/finance/invoices/{id}/` - Update invoice
- `DELETE /api/v1/finance/invoices/{id}/` - Delete invoice
- `POST /api/v1/finance/invoices/{id}/send_invoice/` - Send invoice
- `POST /api/v1/finance/invoices/{id}/mark_paid/` - Mark as paid
- `POST /api/v1/finance/invoices/{id}/cancel_invoice/` - Cancel invoice
- `GET /api/v1/finance/invoices/overdue/` - Get overdue invoices
- `GET /api/v1/finance/invoices/analytics/` - Get invoice analytics

### Payments
- `GET /api/v1/finance/payments/` - List payments
- `POST /api/v1/finance/payments/` - Create payment
- `GET /api/v1/finance/payments/{id}/` - Get payment details
- `PUT /api/v1/finance/payments/{id}/` - Update payment
- `DELETE /api/v1/finance/payments/{id}/` - Delete payment

### Expenses
- `GET /api/v1/finance/expenses/` - List expenses
- `POST /api/v1/finance/expenses/` - Create expense
- `GET /api/v1/finance/expenses/{id}/` - Get expense details
- `PUT /api/v1/finance/expenses/{id}/` - Update expense
- `DELETE /api/v1/finance/expenses/{id}/` - Delete expense
- `POST /api/v1/finance/expenses/{id}/approve/` - Approve expense
- `POST /api/v1/finance/expenses/{id}/reject/` - Reject expense
- `POST /api/v1/finance/expenses/{id}/mark_paid/` - Mark as paid
- `GET /api/v1/finance/expenses/analytics/` - Get expense analytics

### Budgets
- `GET /api/v1/finance/budgets/` - List budgets
- `POST /api/v1/finance/budgets/` - Create budget
- `GET /api/v1/finance/budgets/{id}/` - Get budget details
- `PUT /api/v1/finance/budgets/{id}/` - Update budget
- `DELETE /api/v1/finance/budgets/{id}/` - Delete budget

### Tax Rates
- `GET /api/v1/finance/tax-rates/` - List tax rates
- `POST /api/v1/finance/tax-rates/` - Create tax rate
- `GET /api/v1/finance/tax-rates/{id}/` - Get tax rate details
- `PUT /api/v1/finance/tax-rates/{id}/` - Update tax rate
- `DELETE /api/v1/finance/tax-rates/{id}/` - Delete tax rate

### Recurring Invoices
- `GET /api/v1/finance/recurring-invoices/` - List recurring invoices
- `POST /api/v1/finance/recurring-invoices/` - Create recurring invoice
- `GET /api/v1/finance/recurring-invoices/{id}/` - Get recurring invoice details
- `PUT /api/v1/finance/recurring-invoices/{id}/` - Update recurring invoice
- `DELETE /api/v1/finance/recurring-invoices/{id}/` - Delete recurring invoice
- `POST /api/v1/finance/recurring-invoices/{id}/generate_invoice/` - Generate invoice

### Financial Reports
- `GET /api/v1/finance/financial-reports/` - List financial reports
- `POST /api/v1/finance/financial-reports/` - Create financial report
- `GET /api/v1/finance/financial-reports/{id}/` - Get financial report details
- `PUT /api/v1/finance/financial-reports/{id}/` - Update financial report
- `DELETE /api/v1/finance/financial-reports/{id}/` - Delete financial report

### Dashboard
- `GET /api/v1/finance/dashboard/overview/` - Get finance dashboard overview

## Filters

The finance module includes comprehensive filtering capabilities:

### Customer Filters
- Name, email, phone, city, state, country
- Active status
- Date range filters

### Invoice Filters
- Invoice number, customer, status
- Date ranges (issue date, due date)
- Amount ranges
- Overdue status
- Created by user

### Payment Filters
- Payment number, customer, invoice
- Payment method, received by user
- Date ranges, amount ranges

### Expense Filters
- Description, vendor, category, status
- Date ranges, amount ranges
- Submitted by, approved by users
- Receipt number

### Budget Filters
- Name, active status
- Date ranges, amount ranges
- Current budget filter

### Advanced Analytics Filters
- Date range presets (today, this week, this month, etc.)
- Custom date ranges
- Category and status filters

## Signals

The finance module includes automated signals for:

### Invoice Management
- Automatic total calculations when items are added/removed
- Payment amount updates when payments are recorded
- Status updates based on payment amounts

### Expense Management
- Total amount calculations
- Budget spending updates when expenses are approved/paid

### Budget Management
- Spent amount calculations from approved expenses
- Real-time budget monitoring

### Recurring Invoices
- Next generation date calculations
- Total amount calculations from items

## Permissions

The finance module uses the following permission system:

- **IsAuthenticated**: User must be logged in
- **IsOrganizationMember**: User must be a member of the organization
- **Organization-specific data**: All data is filtered by organization

## Testing

Comprehensive test coverage includes:

- **Model Tests**: Test model creation, validation, and relationships
- **API Tests**: Test all CRUD operations and custom endpoints
- **Signal Tests**: Test automated calculations and updates
- **Filter Tests**: Test filtering functionality
- **Permission Tests**: Test access control

Run tests with:
```bash
python manage.py test apps.finance
```

## Usage Examples

### Creating an Invoice
```python
# Create customer
customer = Customer.objects.create(
    organization=organization,
    name="Acme Corp",
    email="billing@acme.com"
)

# Create invoice
invoice = Invoice.objects.create(
    organization=organization,
    customer=customer,
    issue_date=date.today(),
    due_date=date.today() + timedelta(days=30),
    tax_rate=Decimal('10.00'),
    created_by=user
)

# Add invoice items
InvoiceItem.objects.create(
    invoice=invoice,
    description="Web Development Services",
    quantity=Decimal('40.00'),
    unit_price=Decimal('100.00'),
    total_price=Decimal('4000.00')
)
```

### Recording a Payment
```python
payment = Payment.objects.create(
    organization=organization,
    invoice=invoice,
    customer=customer,
    amount=Decimal('4400.00'),
    payment_method="bank_transfer",
    payment_date=date.today(),
    received_by=user
)
```

### Creating a Budget
```python
budget = Budget.objects.create(
    organization=organization,
    name="2024 Marketing Budget",
    start_date=date(2024, 1, 1),
    end_date=date(2024, 12, 31),
    total_budget=Decimal('50000.00')
)

# Add budget items
BudgetItem.objects.create(
    budget=budget,
    category="marketing",
    description="Digital Marketing",
    budgeted_amount=Decimal('30000.00')
)
```

## Integration

The finance module integrates with:

- **Organizations**: Self-hosted support
- **Users**: User authentication and permissions
- **Core**: Base models and permissions
- **Inventory**: Product information for invoicing
- **Sales**: Customer relationship management

## Future Enhancements

Planned features include:

- **Multi-currency Support**: Handle multiple currencies
- **Advanced Reporting**: More detailed financial reports
- **Payment Gateway Integration**: Direct payment processing
- **Automated Reminders**: Email reminders for overdue invoices
- **Financial Forecasting**: Predictive analytics
- **Audit Trail**: Detailed change tracking
- **Export/Import**: Data migration tools
- **API Webhooks**: Real-time notifications
