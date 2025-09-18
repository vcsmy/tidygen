"""
Comprehensive payroll management models.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta

from apps.core.models import BaseModel
from apps.hr.models import Employee, PayrollPeriod, Payroll

User = get_user_model()


# ==================== PAYROLL CONFIGURATION MODELS ====================

class PayrollConfiguration(BaseModel):
    """Payroll configuration for organization."""
    
    # Basic settings
    currency = models.CharField(max_length=3, default='USD')
    pay_frequency = models.CharField(
        max_length=20,
        choices=[
            ('weekly', 'Weekly'),
            ('bi_weekly', 'Bi-weekly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
        ],
        default='monthly'
    )
    
    # Tax settings
    tax_year = models.IntegerField(default=2024)
    federal_tax_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.22)  # 22%
    state_tax_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.05)    # 5%
    local_tax_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.02)    # 2%
    
    # Social Security settings
    social_security_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.062)  # 6.2%
    social_security_wage_base = models.DecimalField(max_digits=10, decimal_places=2, default=160200.00)
    
    # Medicare settings
    medicare_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.0145)  # 1.45%
    medicare_additional_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.009)  # 0.9%
    medicare_additional_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=200000.00)
    
    # Overtime settings
    overtime_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.50)  # 1.5x
    double_time_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=2.00)  # 2.0x
    overtime_threshold = models.DecimalField(max_digits=5, decimal_places=2, default=40.00)  # 40 hours
    
    # Holiday and vacation settings
    holiday_pay_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.00)  # 1.0x
    vacation_accrual_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.0385)  # ~2 weeks/year
    sick_leave_accrual_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.0192)  # ~1 week/year
    
    # Processing settings
    auto_process_payroll = models.BooleanField(default=False)
    require_approval = models.BooleanField(default=True)
    allow_manual_adjustments = models.BooleanField(default=True)
    
    # Notification settings
    notify_employees = models.BooleanField(default=True)
    notify_managers = models.BooleanField(default=True)
    notify_hr = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Payroll Configuration'
        verbose_name_plural = 'Payroll Configurations'
    
    def __str__(self):
        return f"Payroll Config - {self.organization.name}"


class PayrollComponent(BaseModel):
    """Payroll components (allowances, deductions, etc.)."""
    
    name = models.CharField(max_length=100)
    component_type = models.CharField(
        max_length=20,
        choices=[
            ('allowance', 'Allowance'),
            ('deduction', 'Deduction'),
            ('benefit', 'Benefit'),
            ('tax', 'Tax'),
            ('overtime', 'Overtime'),
            ('bonus', 'Bonus'),
            ('commission', 'Commission'),
        ]
    )
    
    # Calculation settings
    calculation_type = models.CharField(
        max_length=20,
        choices=[
            ('fixed', 'Fixed Amount'),
            ('percentage', 'Percentage of Gross'),
            ('hourly', 'Per Hour'),
            ('daily', 'Per Day'),
            ('monthly', 'Per Month'),
            ('annual', 'Per Year'),
        ],
        default='fixed'
    )
    
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    
    # Tax settings
    is_taxable = models.BooleanField(default=True)
    is_pretax = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_mandatory = models.BooleanField(default=False)
    
    # Additional settings
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, blank=True)
    sort_order = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Payroll Component'
        verbose_name_plural = 'Payroll Components'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.component_type})"


class EmployeePayrollProfile(BaseModel):
    """Employee-specific payroll profile."""
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='payroll_profile')
    
    # Basic pay settings
    pay_type = models.CharField(
        max_length=20,
        choices=[
            ('salary', 'Salary'),
            ('hourly', 'Hourly'),
            ('commission', 'Commission'),
            ('contract', 'Contract'),
        ],
        default='salary'
    )
    
    # Pay rates
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    
    # Tax settings
    federal_exemptions = models.IntegerField(default=0)
    state_exemptions = models.IntegerField(default=0)
    additional_federal_withholding = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    additional_state_withholding = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Direct deposit
    bank_name = models.CharField(max_length=100, blank=True)
    bank_routing_number = models.CharField(max_length=20, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    account_type = models.CharField(
        max_length=20,
        choices=[
            ('checking', 'Checking'),
            ('savings', 'Savings'),
        ],
        default='checking'
    )
    
    # Benefits
    health_insurance_deduction = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    dental_insurance_deduction = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    vision_insurance_deduction = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    retirement_contribution = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    retirement_match = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    
    # Custom components
    custom_allowances = models.JSONField(default=dict, blank=True)
    custom_deductions = models.JSONField(default=dict, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    effective_date = models.DateField(default=date.today)
    
    class Meta:
        verbose_name = 'Employee Payroll Profile'
        verbose_name_plural = 'Employee Payroll Profiles'
    
    def __str__(self):
        return f"Payroll Profile - {self.employee.full_name}"


# ==================== ENHANCED PAYROLL MODELS ====================

class PayrollRun(BaseModel):
    """Payroll run for processing multiple employees."""
    payroll_period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE, related_name='payroll_runs')
    
    # Run details
    run_name = models.CharField(max_length=100)
    run_type = models.CharField(
        max_length=20,
        choices=[
            ('regular', 'Regular Payroll'),
            ('bonus', 'Bonus Payroll'),
            ('adjustment', 'Adjustment Payroll'),
            ('termination', 'Termination Payroll'),
            ('supplemental', 'Supplemental Payroll'),
        ],
        default='regular'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('processing', 'Processing'),
            ('review', 'Under Review'),
            ('approved', 'Approved'),
            ('paid', 'Paid'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft'
    )
    
    # Processing details
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_payroll_runs')
    processed_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_payroll_runs')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Totals
    total_employees = models.IntegerField(default=0)
    total_gross_pay = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_net_pay = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_taxes = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Additional information
    notes = models.TextField(blank=True)
    error_log = models.JSONField(default=list, blank=True)
    
    class Meta:
        verbose_name = 'Payroll Run'
        verbose_name_plural = 'Payroll Runs'
        ordering = ['-created']
    
    def __str__(self):
        return f"{self.run_name} - {self.payroll_period.name}"


class PayrollItem(BaseModel):
    """Individual payroll items for detailed tracking."""
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE, related_name='items')
    payroll_run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name='items')
    
    # Item details
    component = models.ForeignKey(PayrollComponent, on_delete=models.CASCADE, related_name='payroll_items')
    item_type = models.CharField(
        max_length=20,
        choices=[
            ('earnings', 'Earnings'),
            ('deduction', 'Deduction'),
            ('tax', 'Tax'),
            ('benefit', 'Benefit'),
        ]
    )
    
    # Amounts
    quantity = models.DecimalField(max_digits=10, decimal_places=4, default=1)
    rate = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Tax settings
    is_taxable = models.BooleanField(default=True)
    is_pretax = models.BooleanField(default=False)
    
    # Additional information
    description = models.TextField(blank=True)
    reference = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'Payroll Item'
        verbose_name_plural = 'Payroll Items'
        ordering = ['component__sort_order', 'component__name']
    
    def __str__(self):
        return f"{self.payroll.employee.full_name} - {self.component.name}"


class PayrollAdjustment(BaseModel):
    """Payroll adjustments for corrections."""
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE, related_name='adjustments')
    payroll_run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name='adjustments')
    
    # Adjustment details
    adjustment_type = models.CharField(
        max_length=20,
        choices=[
            ('correction', 'Correction'),
            ('bonus', 'Bonus'),
            ('penalty', 'Penalty'),
            ('advance', 'Advance'),
            ('reimbursement', 'Reimbursement'),
            ('other', 'Other'),
        ]
    )
    
    # Amounts
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_positive = models.BooleanField(default=True)  # True for additions, False for deductions
    
    # Tax settings
    is_taxable = models.BooleanField(default=True)
    is_pretax = models.BooleanField(default=False)
    
    # Approval
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_adjustments')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Additional information
    reason = models.TextField()
    reference_document = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'Payroll Adjustment'
        verbose_name_plural = 'Payroll Adjustments'
        ordering = ['-created']
    
    def __str__(self):
        return f"{self.payroll.employee.full_name} - {self.adjustment_type}"


# ==================== TAX AND COMPLIANCE MODELS ====================

class TaxYear(BaseModel):
    """Tax year configuration."""
    year = models.IntegerField(unique=True)
    
    # Tax rates
    federal_tax_rate = models.DecimalField(max_digits=5, decimal_places=4)
    state_tax_rate = models.DecimalField(max_digits=5, decimal_places=4)
    local_tax_rate = models.DecimalField(max_digits=5, decimal_places=4)
    
    # Social Security
    social_security_rate = models.DecimalField(max_digits=5, decimal_places=4)
    social_security_wage_base = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Medicare
    medicare_rate = models.DecimalField(max_digits=5, decimal_places=4)
    medicare_additional_rate = models.DecimalField(max_digits=5, decimal_places=4)
    medicare_additional_threshold = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Standard deductions
    standard_deduction_single = models.DecimalField(max_digits=10, decimal_places=2)
    standard_deduction_married = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Tax Year'
        verbose_name_plural = 'Tax Years'
        ordering = ['-year']
    
    def __str__(self):
        return f"Tax Year {self.year}"


class EmployeeTaxInfo(BaseModel):
    """Employee tax information."""
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='tax_info')
    tax_year = models.ForeignKey(TaxYear, on_delete=models.CASCADE, related_name='employee_tax_info')
    
    # Filing status
    filing_status = models.CharField(
        max_length=20,
        choices=[
            ('single', 'Single'),
            ('married_joint', 'Married Filing Jointly'),
            ('married_separate', 'Married Filing Separately'),
            ('head_of_household', 'Head of Household'),
            ('widow', 'Qualifying Widow(er)'),
        ],
        default='single'
    )
    
    # Exemptions
    federal_exemptions = models.IntegerField(default=0)
    state_exemptions = models.IntegerField(default=0)
    
    # Additional withholding
    additional_federal_withholding = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    additional_state_withholding = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Tax forms
    w4_form_date = models.DateField(null=True, blank=True)
    state_tax_form_date = models.DateField(null=True, blank=True)
    
    # YTD totals
    ytd_gross_wages = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ytd_federal_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ytd_state_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ytd_social_security = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ytd_medicare = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'Employee Tax Information'
        verbose_name_plural = 'Employee Tax Information'
        unique_together = ['employee', 'tax_year']
    
    def __str__(self):
        return f"{self.employee.full_name} - Tax Year {self.tax_year.year}"


# ==================== PAYROLL REPORTS AND ANALYTICS ====================

class PayrollReport(BaseModel):
    """Payroll reports and analytics."""
    
    # Report details
    report_name = models.CharField(max_length=100)
    report_type = models.CharField(
        max_length=30,
        choices=[
            ('summary', 'Payroll Summary'),
            ('detailed', 'Detailed Payroll'),
            ('tax_summary', 'Tax Summary'),
            ('benefits_summary', 'Benefits Summary'),
            ('overtime_report', 'Overtime Report'),
            ('attendance_report', 'Attendance Report'),
            ('custom', 'Custom Report'),
        ]
    )
    
    # Date range
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Filters
    departments = models.JSONField(default=list, blank=True)
    employees = models.JSONField(default=list, blank=True)
    payroll_periods = models.JSONField(default=list, blank=True)
    
    # Report data
    report_data = models.JSONField(default=dict, blank=True)
    totals = models.JSONField(default=dict, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('generating', 'Generating'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='generating'
    )
    
    # Generated by
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_payroll_reports')
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Payroll Report'
        verbose_name_plural = 'Payroll Reports'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.report_name} - {self.start_date} to {self.end_date}"


class PayrollAnalytics(BaseModel):
    """Payroll analytics and metrics."""
    
    # Time period
    period_start = models.DateField()
    period_end = models.DateField()
    period_type = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('yearly', 'Yearly'),
        ]
    )
    
    # Metrics
    total_employees = models.IntegerField(default=0)
    total_gross_pay = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_net_pay = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_taxes = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_benefits = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_overtime = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Averages
    average_gross_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_net_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_hours_worked = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Trends
    gross_pay_trend = models.DecimalField(max_digits=8, decimal_places=4, default=0)  # Percentage change
    employee_count_trend = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    
    # Additional metrics
    metrics = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = 'Payroll Analytics'
        verbose_name_plural = 'Payroll Analytics'
        ordering = ['-period_start']
        unique_together = ['period_start', 'period_end', 'period_type']
    
    def __str__(self):
        return f"Payroll Analytics - {self.period_start} to {self.period_end}"


# ==================== PAYROLL INTEGRATION MODELS ====================

class PayrollIntegration(BaseModel):
    """Payroll system integrations."""
    
    # Integration details
    integration_name = models.CharField(max_length=100)
    integration_type = models.CharField(
        max_length=30,
        choices=[
            ('banking', 'Banking Integration'),
            ('tax_service', 'Tax Service Integration'),
            ('benefits_provider', 'Benefits Provider Integration'),
            ('time_tracking', 'Time Tracking Integration'),
            ('accounting', 'Accounting System Integration'),
            ('hr_system', 'HR System Integration'),
        ]
    )
    
    # Provider information
    provider_name = models.CharField(max_length=100)
    provider_url = models.URLField(blank=True)
    
    # Configuration
    is_active = models.BooleanField(default=True)
    configuration = models.JSONField(default=dict, blank=True)
    
    # Authentication
    api_key = models.CharField(max_length=255, blank=True)
    api_secret = models.CharField(max_length=255, blank=True)
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    last_sync = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Success'),
            ('error', 'Error'),
            ('pending', 'Pending'),
        ],
        default='pending'
    )
    error_message = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Payroll Integration'
        verbose_name_plural = 'Payroll Integrations'
        ordering = ['integration_name']
    
    def __str__(self):
        return f"{self.integration_name} - {self.provider_name}"


class PayrollWebhook(BaseModel):
    """Payroll webhooks for external integrations."""
    integration = models.ForeignKey(PayrollIntegration, on_delete=models.CASCADE, related_name='webhooks')
    
    # Webhook details
    event_type = models.CharField(max_length=50)
    webhook_url = models.URLField()
    
    # Security
    secret_key = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Statistics
    total_calls = models.IntegerField(default=0)
    successful_calls = models.IntegerField(default=0)
    failed_calls = models.IntegerField(default=0)
    last_called = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Payroll Webhook'
        verbose_name_plural = 'Payroll Webhooks'
        ordering = ['event_type']
    
    def __str__(self):
        return f"{self.event_type} - {self.webhook_url}"


# ==================== PAYROLL NOTIFICATIONS ====================

class PayrollNotification(BaseModel):
    """Payroll notifications and alerts."""
    
    # Notification details
    notification_type = models.CharField(
        max_length=30,
        choices=[
            ('payroll_processed', 'Payroll Processed'),
            ('payroll_approved', 'Payroll Approved'),
            ('payroll_paid', 'Payroll Paid'),
            ('tax_deadline', 'Tax Deadline'),
            ('benefits_deadline', 'Benefits Deadline'),
            ('error_alert', 'Error Alert'),
            ('reminder', 'Reminder'),
        ]
    )
    
    # Recipients
    recipients = models.JSONField(default=list, blank=True)  # List of user IDs or email addresses
    
    # Message
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    # Delivery
    delivery_method = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('sms', 'SMS'),
            ('push', 'Push Notification'),
            ('in_app', 'In-App Notification'),
        ],
        default='email'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('sent', 'Sent'),
            ('delivered', 'Delivered'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    
    # Scheduling
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Related objects
    related_payroll = models.ForeignKey(Payroll, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    related_payroll_run = models.ForeignKey(PayrollRun, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    
    class Meta:
        verbose_name = 'Payroll Notification'
        verbose_name_plural = 'Payroll Notifications'
        ordering = ['-created']
    
    def __str__(self):
        return f"{self.notification_type} - {self.subject}"
