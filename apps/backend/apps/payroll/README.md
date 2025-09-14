# Payroll Management System

A comprehensive payroll management system for the TidyGen ERP platform, providing complete payroll processing, tax management, reporting, and analytics capabilities.

## Features

### Core Payroll Management
- **Payroll Configuration**: Flexible payroll settings per organization
- **Payroll Components**: Configurable earnings, deductions, and taxes
- **Employee Payroll Profiles**: Individual payroll settings and direct deposit
- **Payroll Runs**: Batch processing of payroll for multiple employees
- **Payroll Items**: Detailed line items for each payroll calculation
- **Payroll Adjustments**: Manual adjustments with approval workflow

### Tax Management
- **Tax Year Configuration**: Annual tax settings and rates
- **Employee Tax Information**: W-4 forms and tax exemptions
- **Tax Calculations**: Automated federal, state, and local tax calculations
- **Tax Reporting**: Year-end tax forms and reporting

### Reporting & Analytics
- **Payroll Reports**: Comprehensive reporting capabilities
- **Payroll Analytics**: Trend analysis and insights
- **Custom Reports**: Flexible report generation
- **Export Capabilities**: Multiple export formats

### Integrations
- **Third-party Integrations**: Connect with accounting and HR systems
- **Webhook Support**: Real-time notifications and data sync
- **API Access**: RESTful API for external integrations

### Notifications
- **Multi-channel Notifications**: Email, SMS, and push notifications
- **Automated Alerts**: Payroll processing and error notifications
- **Customizable Templates**: Flexible notification templates

## Models

### PayrollConfiguration
Central configuration for payroll processing per organization.

**Key Fields:**
- `organization`: Organization reference
- `currency`: Payroll currency (USD, EUR, etc.)
- `pay_frequency`: Pay frequency (weekly, biweekly, monthly, etc.)
- `tax_year`: Current tax year
- `federal_tax_rate`: Federal tax rate
- `state_tax_rate`: State tax rate
- `social_security_rate`: Social Security tax rate
- `medicare_rate`: Medicare tax rate
- `overtime_multiplier`: Overtime pay multiplier
- `auto_process_payroll`: Automatic payroll processing
- `require_approval`: Require approval for payroll runs

### PayrollComponent
Configurable payroll components for earnings, deductions, and taxes.

**Key Fields:**
- `organization`: Organization reference
- `name`: Component name
- `component_type`: Type (earning, deduction, tax)
- `calculation_type`: Calculation method (fixed, percentage, hours)
- `amount`: Fixed amount or base amount
- `percentage`: Percentage rate
- `is_taxable`: Whether component is taxable
- `is_pretax`: Whether component is pre-tax
- `is_mandatory`: Whether component is mandatory
- `sort_order`: Display order

### EmployeePayrollProfile
Individual payroll settings for each employee.

**Key Fields:**
- `employee`: Employee reference
- `pay_type`: Pay type (hourly, salary, commission)
- `base_salary`: Base salary amount
- `hourly_rate`: Hourly rate
- `commission_rate`: Commission rate
- `federal_exemptions`: Federal tax exemptions
- `state_exemptions`: State tax exemptions
- `bank_name`: Bank name for direct deposit
- `bank_routing_number`: Bank routing number
- `bank_account_number`: Bank account number
- `account_type`: Account type (checking, savings)

### PayrollRun
Batch payroll processing for a specific period.

**Key Fields:**
- `organization`: Organization reference
- `payroll_period`: Payroll period reference
- `run_name`: Run name/description
- `run_type`: Run type (regular, bonus, adjustment)
- `status`: Run status (draft, processing, approved, paid)
- `processed_by`: User who processed the run
- `processed_at`: Processing timestamp
- `approved_by`: User who approved the run
- `approved_at`: Approval timestamp
- `total_employees`: Total number of employees
- `total_gross_pay`: Total gross pay
- `total_deductions`: Total deductions
- `total_net_pay`: Total net pay
- `total_taxes`: Total taxes

### PayrollItem
Individual payroll line items for each employee.

**Key Fields:**
- `payroll_run`: Payroll run reference
- `component`: Payroll component reference
- `item_type`: Item type (earning, deduction, tax)
- `quantity`: Quantity (hours, units, etc.)
- `rate`: Rate per unit
- `amount`: Total amount
- `is_taxable`: Whether item is taxable
- `is_pretax`: Whether item is pre-tax
- `description`: Item description
- `reference`: Reference information

### PayrollAdjustment
Manual adjustments to payroll with approval workflow.

**Key Fields:**
- `payroll_run`: Payroll run reference
- `adjustment_type`: Type of adjustment
- `amount`: Adjustment amount
- `is_positive`: Whether adjustment is positive
- `is_taxable`: Whether adjustment is taxable
- `is_pretax`: Whether adjustment is pre-tax
- `reason`: Reason for adjustment
- `reference_document`: Reference document
- `approved_by`: User who approved
- `approved_at`: Approval timestamp

### TaxYear
Annual tax configuration and rates.

**Key Fields:**
- `organization`: Organization reference
- `year`: Tax year
- `federal_tax_rate`: Federal tax rate
- `state_tax_rate`: State tax rate
- `local_tax_rate`: Local tax rate
- `social_security_rate`: Social Security rate
- `social_security_wage_base`: Social Security wage base
- `medicare_rate`: Medicare rate
- `medicare_additional_rate`: Additional Medicare rate
- `medicare_additional_threshold`: Additional Medicare threshold
- `standard_deduction_single`: Standard deduction for single filers
- `standard_deduction_married`: Standard deduction for married filers
- `is_active`: Whether tax year is active

### EmployeeTaxInfo
Employee tax information and W-4 data.

**Key Fields:**
- `employee`: Employee reference
- `tax_year`: Tax year
- `filing_status`: Filing status
- `federal_exemptions`: Federal exemptions
- `state_exemptions`: State exemptions
- `additional_federal_withholding`: Additional federal withholding
- `additional_state_withholding`: Additional state withholding
- `w4_form_date`: W-4 form date
- `state_tax_form_date`: State tax form date
- `ytd_gross_wages`: Year-to-date gross wages
- `ytd_federal_tax`: Year-to-date federal tax
- `ytd_state_tax`: Year-to-date state tax
- `ytd_social_security`: Year-to-date Social Security
- `ytd_medicare`: Year-to-date Medicare

### PayrollReport
Generated payroll reports with flexible filtering.

**Key Fields:**
- `organization`: Organization reference
- `report_name`: Report name
- `report_type`: Report type
- `start_date`: Report start date
- `end_date`: Report end date
- `departments`: Filter by departments
- `employees`: Filter by employees
- `payroll_periods`: Filter by payroll periods
- `report_data`: Report data (JSON)
- `totals`: Report totals (JSON)
- `status`: Report status
- `generated_by`: User who generated report
- `generated_at`: Generation timestamp

### PayrollAnalytics
Payroll analytics and trend data.

**Key Fields:**
- `organization`: Organization reference
- `period_start`: Period start date
- `period_end`: Period end date
- `period_type`: Period type (daily, weekly, monthly, yearly)
- `total_employees`: Total employees
- `total_gross_pay`: Total gross pay
- `total_net_pay`: Total net pay
- `total_taxes`: Total taxes
- `total_benefits`: Total benefits
- `total_overtime`: Total overtime
- `average_gross_pay`: Average gross pay
- `average_net_pay`: Average net pay
- `average_hours_worked`: Average hours worked
- `gross_pay_trend`: Gross pay trend data
- `employee_count_trend`: Employee count trend data
- `metrics`: Additional metrics (JSON)

### PayrollIntegration
Third-party payroll system integrations.

**Key Fields:**
- `organization`: Organization reference
- `integration_name`: Integration name
- `integration_type`: Integration type
- `provider_name`: Provider name
- `provider_url`: Provider URL
- `is_active`: Whether integration is active
- `configuration`: Integration configuration (JSON)
- `api_key`: API key
- `api_secret`: API secret
- `access_token`: Access token
- `refresh_token`: Refresh token
- `token_expires_at`: Token expiration
- `sync_status`: Sync status
- `last_sync`: Last sync timestamp
- `error_message`: Error message

### PayrollWebhook
Webhook configuration for real-time notifications.

**Key Fields:**
- `organization`: Organization reference
- `integration`: Integration reference
- `event_type`: Event type
- `webhook_url`: Webhook URL
- `secret_key`: Secret key for verification
- `is_active`: Whether webhook is active
- `total_calls`: Total webhook calls
- `successful_calls`: Successful webhook calls
- `failed_calls`: Failed webhook calls
- `last_called`: Last call timestamp

### PayrollNotification
Payroll-related notifications and alerts.

**Key Fields:**
- `organization`: Organization reference
- `notification_type`: Notification type
- `subject`: Notification subject
- `message`: Notification message
- `recipients`: Notification recipients
- `delivery_method`: Delivery method (email, SMS, push)
- `status`: Notification status
- `scheduled_at`: Scheduled delivery time
- `sent_at`: Sent timestamp
- `related_payroll`: Related payroll record
- `related_payroll_run`: Related payroll run

## API Endpoints

### Payroll Configuration
- `GET /api/payroll/configuration/` - List payroll configurations
- `POST /api/payroll/configuration/` - Create payroll configuration
- `GET /api/payroll/configuration/{id}/` - Get payroll configuration
- `PUT /api/payroll/configuration/{id}/` - Update payroll configuration
- `DELETE /api/payroll/configuration/{id}/` - Delete payroll configuration

### Payroll Components
- `GET /api/payroll/components/` - List payroll components
- `POST /api/payroll/components/` - Create payroll component
- `GET /api/payroll/components/{id}/` - Get payroll component
- `PUT /api/payroll/components/{id}/` - Update payroll component
- `DELETE /api/payroll/components/{id}/` - Delete payroll component

### Employee Payroll Profiles
- `GET /api/payroll/profiles/` - List employee payroll profiles
- `POST /api/payroll/profiles/` - Create employee payroll profile
- `GET /api/payroll/profiles/{id}/` - Get employee payroll profile
- `PUT /api/payroll/profiles/{id}/` - Update employee payroll profile
- `DELETE /api/payroll/profiles/{id}/` - Delete employee payroll profile

### Payroll Runs
- `GET /api/payroll/runs/` - List payroll runs
- `POST /api/payroll/runs/` - Create payroll run
- `GET /api/payroll/runs/{id}/` - Get payroll run
- `PUT /api/payroll/runs/{id}/` - Update payroll run
- `DELETE /api/payroll/runs/{id}/` - Delete payroll run
- `POST /api/payroll/runs/{id}/process/` - Process payroll run
- `POST /api/payroll/runs/{id}/approve/` - Approve payroll run
- `POST /api/payroll/runs/{id}/pay/` - Mark payroll run as paid

### Payroll Items
- `GET /api/payroll/items/` - List payroll items
- `POST /api/payroll/items/` - Create payroll item
- `GET /api/payroll/items/{id}/` - Get payroll item
- `PUT /api/payroll/items/{id}/` - Update payroll item
- `DELETE /api/payroll/items/{id}/` - Delete payroll item

### Payroll Adjustments
- `GET /api/payroll/adjustments/` - List payroll adjustments
- `POST /api/payroll/adjustments/` - Create payroll adjustment
- `GET /api/payroll/adjustments/{id}/` - Get payroll adjustment
- `PUT /api/payroll/adjustments/{id}/` - Update payroll adjustment
- `DELETE /api/payroll/adjustments/{id}/` - Delete payroll adjustment
- `POST /api/payroll/adjustments/{id}/approve/` - Approve payroll adjustment

### Tax Management
- `GET /api/payroll/tax-years/` - List tax years
- `POST /api/payroll/tax-years/` - Create tax year
- `GET /api/payroll/tax-years/{id}/` - Get tax year
- `PUT /api/payroll/tax-years/{id}/` - Update tax year
- `DELETE /api/payroll/tax-years/{id}/` - Delete tax year

- `GET /api/payroll/tax-info/` - List employee tax info
- `POST /api/payroll/tax-info/` - Create employee tax info
- `GET /api/payroll/tax-info/{id}/` - Get employee tax info
- `PUT /api/payroll/tax-info/{id}/` - Update employee tax info
- `DELETE /api/payroll/tax-info/{id}/` - Delete employee tax info

### Reports & Analytics
- `GET /api/payroll/reports/` - List payroll reports
- `POST /api/payroll/reports/` - Create payroll report
- `GET /api/payroll/reports/{id}/` - Get payroll report
- `PUT /api/payroll/reports/{id}/` - Update payroll report
- `DELETE /api/payroll/reports/{id}/` - Delete payroll report
- `POST /api/payroll/reports/{id}/generate/` - Generate report data

- `GET /api/payroll/analytics/` - List payroll analytics
- `POST /api/payroll/analytics/` - Create payroll analytics
- `GET /api/payroll/analytics/{id}/` - Get payroll analytics
- `PUT /api/payroll/analytics/{id}/` - Update payroll analytics
- `DELETE /api/payroll/analytics/{id}/` - Delete payroll analytics

### Integrations
- `GET /api/payroll/integrations/` - List payroll integrations
- `POST /api/payroll/integrations/` - Create payroll integration
- `GET /api/payroll/integrations/{id}/` - Get payroll integration
- `PUT /api/payroll/integrations/{id}/` - Update payroll integration
- `DELETE /api/payroll/integrations/{id}/` - Delete payroll integration
- `POST /api/payroll/integrations/{id}/test/` - Test integration connection
- `POST /api/payroll/integrations/{id}/sync/` - Sync integration data

### Webhooks
- `GET /api/payroll/webhooks/` - List payroll webhooks
- `POST /api/payroll/webhooks/` - Create payroll webhook
- `GET /api/payroll/webhooks/{id}/` - Get payroll webhook
- `PUT /api/payroll/webhooks/{id}/` - Update payroll webhook
- `DELETE /api/payroll/webhooks/{id}/` - Delete payroll webhook
- `POST /api/payroll/webhooks/{id}/test/` - Test webhook endpoint

### Notifications
- `GET /api/payroll/notifications/` - List payroll notifications
- `POST /api/payroll/notifications/` - Create payroll notification
- `GET /api/payroll/notifications/{id}/` - Get payroll notification
- `PUT /api/payroll/notifications/{id}/` - Update payroll notification
- `DELETE /api/payroll/notifications/{id}/` - Delete payroll notification
- `POST /api/payroll/notifications/{id}/send/` - Send notification

## Usage Examples

### Creating a Payroll Configuration

```python
from apps.payroll.models import PayrollConfiguration
from apps.organizations.models import Organization

organization = Organization.objects.get(name="My Company")
config = PayrollConfiguration.objects.create(
    organization=organization,
    currency="USD",
    pay_frequency="biweekly",
    tax_year=2024,
    federal_tax_rate=Decimal('0.22'),
    state_tax_rate=Decimal('0.05'),
    social_security_rate=Decimal('0.062'),
    medicare_rate=Decimal('0.0145'),
    overtime_multiplier=Decimal('1.5'),
    auto_process_payroll=True,
    require_approval=True
)
```

### Creating Payroll Components

```python
from apps.payroll.models import PayrollComponent

# Regular hours component
regular_hours = PayrollComponent.objects.create(
    organization=organization,
    name="Regular Hours",
    component_type="earning",
    calculation_type="hours",
    amount=Decimal('25.00'),
    is_taxable=True,
    is_mandatory=True,
    sort_order=1
)

# Federal tax component
federal_tax = PayrollComponent.objects.create(
    organization=organization,
    name="Federal Tax",
    component_type="deduction",
    calculation_type="percentage",
    percentage=Decimal('0.22'),
    is_taxable=False,
    is_mandatory=True,
    sort_order=10
)
```

### Processing a Payroll Run

```python
from apps.payroll.models import PayrollRun, PayrollItem
from apps.hr.models import PayrollPeriod

# Create payroll period
period = PayrollPeriod.objects.create(
    organization=organization,
    name="Biweekly Period 1",
    start_date=date(2024, 1, 1),
    end_date=date(2024, 1, 14)
)

# Create payroll run
run = PayrollRun.objects.create(
    organization=organization,
    payroll_period=period,
    run_name="Biweekly Payroll - Period 1",
    run_type="regular",
    status="draft"
)

# Add payroll items for employees
for employee in Employee.objects.filter(organization=organization, is_active=True):
    # Regular hours
    PayrollItem.objects.create(
        payroll_run=run,
        component=regular_hours,
        item_type="earning",
        quantity=80,  # 80 hours for biweekly
        rate=employee.payroll_profile.hourly_rate,
        amount=80 * employee.payroll_profile.hourly_rate,
        is_taxable=True
    )
    
    # Federal tax
    gross_pay = 80 * employee.payroll_profile.hourly_rate
    federal_tax_amount = gross_pay * Decimal('0.22')
    PayrollItem.objects.create(
        payroll_run=run,
        component=federal_tax,
        item_type="deduction",
        quantity=1,
        rate=federal_tax_amount,
        amount=federal_tax_amount,
        is_taxable=False
    )

# Process the payroll run
run.status = "processing"
run.processed_by = request.user
run.processed_at = timezone.now()
run.save()
```

### Creating Payroll Adjustments

```python
from apps.payroll.models import PayrollAdjustment

# Create a bonus adjustment
adjustment = PayrollAdjustment.objects.create(
    payroll_run=run,
    adjustment_type="bonus",
    amount=Decimal('1000.00'),
    is_positive=True,
    is_taxable=True,
    reason="Q1 Performance Bonus"
)

# Approve the adjustment
adjustment.approved_by = request.user
adjustment.approved_at = timezone.now()
adjustment.save()
```

### Generating Payroll Reports

```python
from apps.payroll.models import PayrollReport

# Create a summary report
report = PayrollReport.objects.create(
    organization=organization,
    report_name="Q1 2024 Payroll Summary",
    report_type="summary",
    start_date=date(2024, 1, 1),
    end_date=date(2024, 3, 31),
    status="draft"
)

# Generate report data
report.generate_data()
report.status = "completed"
report.save()
```

## Signals

The payroll system includes comprehensive signals for automated operations:

### PayrollConfiguration Signals
- `post_save`: Creates default payroll components and tax year
- `pre_save`: Validates configuration settings

### EmployeePayrollProfile Signals
- `post_save`: Creates employee tax info for current year
- `pre_save`: Validates bank account information

### PayrollRun Signals
- `post_save`: Generates payroll items for active employees
- `pre_save`: Calculates payroll totals

### PayrollItem Signals
- `post_save`: Updates payroll totals
- `post_delete`: Updates payroll totals

### PayrollAdjustment Signals
- `post_save`: Updates payroll totals and sends approval notifications
- `pre_save`: Sets approval timestamp

### TaxYear Signals
- `post_save`: Creates tax info for all active employees

### EmployeeTaxInfo Signals
- `post_save`: Recalculates current payroll based on updated tax info

## Admin Interface

The payroll system includes a comprehensive Django admin interface with:

- **List Views**: Optimized list displays with filtering and search
- **Detail Views**: Organized field sets for easy editing
- **Inline Editing**: Related objects can be edited inline
- **Custom Actions**: Bulk operations for common tasks
- **Read-only Fields**: Automatic timestamp and calculated fields
- **Validation**: Form validation and error handling

## Testing

The payroll system includes comprehensive tests covering:

- **Model Tests**: All model creation, validation, and relationships
- **Integration Tests**: Complete payroll workflows
- **Calculation Tests**: Payroll calculations and totals
- **Signal Tests**: Automated signal operations
- **API Tests**: REST API endpoints and responses

## Security

The payroll system implements several security measures:

- **Data Encryption**: Sensitive data like bank account numbers
- **Access Control**: Role-based permissions for payroll operations
- **Audit Logging**: Complete audit trail for all payroll changes
- **Approval Workflows**: Multi-level approval for sensitive operations
- **Data Validation**: Comprehensive input validation and sanitization

## Performance

The payroll system is optimized for performance with:

- **Database Indexing**: Strategic indexes on frequently queried fields
- **Query Optimization**: Efficient queries with select_related and prefetch_related
- **Caching**: Strategic caching of frequently accessed data
- **Background Processing**: Asynchronous processing for large operations
- **Pagination**: Efficient pagination for large datasets

## Maintenance

Regular maintenance tasks include:

- **Data Cleanup**: Archiving old payroll data
- **Tax Updates**: Updating tax rates and calculations
- **Integration Monitoring**: Monitoring third-party integrations
- **Performance Monitoring**: Tracking system performance
- **Backup Verification**: Ensuring data backup integrity

## Support

For support and questions:

- **Documentation**: Comprehensive API and user documentation
- **Logging**: Detailed logging for troubleshooting
- **Error Handling**: Graceful error handling and recovery
- **Monitoring**: System health monitoring and alerts
- **Updates**: Regular updates and bug fixes
