"""
Finance management models for TidyGen ERP platform.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from apps.core.models import BaseModel

User = get_user_model()


class Account(BaseModel):
    """Chart of accounts for financial tracking."""
    ACCOUNT_TYPES = [
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('revenue', 'Revenue'),
        ('expense', 'Expense'),
    ]
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        unique_together = ['code']
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Customer(BaseModel):
    """Customer model for invoicing and payments."""
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Address
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Financial details
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_terms = models.IntegerField(default=30)  # days
    tax_id = models.CharField(max_length=50, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Vendor(BaseModel):
    """Vendor model for expenses and payments."""
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Address
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Financial details
    payment_terms = models.IntegerField(default=30)  # days
    tax_id = models.CharField(max_length=50, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Invoice(BaseModel):
    """Invoice model for customer billing."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('viewed', 'Viewed'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Dates
    issue_date = models.DateField()
    due_date = models.DateField()
    sent_date = models.DateField(null=True, blank=True)
    paid_date = models.DateField(null=True, blank=True)
    
    # Financial details
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Additional information
    notes = models.TextField(blank=True)
    terms_conditions = models.TextField(blank=True)
    
    # Tracking
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_invoices')
    
    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"INV-{self.invoice_number}"
    
    @property
    def balance_due(self):
        return self.total_amount - self.paid_amount
    
    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.due_date < timezone.now().date() and self.status not in ['paid', 'cancelled']


class InvoiceItem(BaseModel):
    """Invoice line items."""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        verbose_name = 'Invoice Item'
        verbose_name_plural = 'Invoice Items'
    
    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.description}"


class Payment(BaseModel):
    """Payment model for tracking payments received."""
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('other', 'Other'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='payments')
    
    payment_number = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_date = models.DateField()
    
    # Reference information
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    # Bank details (for bank transfers)
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    
    # Tracking
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='received_payments')
    
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"PAY-{self.payment_number}"


class Expense(BaseModel):
    """Expense model for tracking business expenses."""
    CATEGORIES = [
        ('office_supplies', 'Office Supplies'),
        ('travel', 'Travel'),
        ('meals', 'Meals & Entertainment'),
        ('utilities', 'Utilities'),
        ('rent', 'Rent'),
        ('marketing', 'Marketing'),
        ('professional_services', 'Professional Services'),
        ('equipment', 'Equipment'),
        ('software', 'Software'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
    ]
    
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    category = models.CharField(max_length=30, choices=CATEGORIES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Financial details
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Details
    description = models.CharField(max_length=500)
    expense_date = models.DateField()
    receipt_number = models.CharField(max_length=100, blank=True)
    receipt_image = models.ImageField(upload_to='expense_receipts/', blank=True, null=True)
    
    # Approval workflow
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_expenses')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_expenses')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'
        ordering = ['-expense_date']
    
    def __str__(self):
        return f"{self.description} - ${self.total_amount}"


class Budget(BaseModel):
    """Budget model for financial planning."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Budget period
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Budget amounts
    total_budget = models.DecimalField(max_digits=15, decimal_places=2)
    spent_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Budget'
        verbose_name_plural = 'Budgets'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"
    
    @property
    def remaining_budget(self):
        return self.total_budget - self.spent_amount
    
    @property
    def spent_percentage(self):
        if self.total_budget > 0:
            return (self.spent_amount / self.total_budget) * 100
        return 0


class BudgetItem(BaseModel):
    """Budget line items."""
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='items')
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    budgeted_amount = models.DecimalField(max_digits=12, decimal_places=2)
    spent_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'Budget Item'
        verbose_name_plural = 'Budget Items'
    
    def __str__(self):
        return f"{self.budget.name} - {self.category}"


class FinancialReport(BaseModel):
    """Financial report model for storing generated reports."""
    REPORT_TYPES = [
        ('profit_loss', 'Profit & Loss'),
        ('balance_sheet', 'Balance Sheet'),
        ('cash_flow', 'Cash Flow'),
        ('aged_receivables', 'Aged Receivables'),
        ('aged_payables', 'Aged Payables'),
        ('custom', 'Custom Report'),
    ]
    
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    name = models.CharField(max_length=200)
    
    # Report period
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Report data
    report_data = models.JSONField(default=dict)
    
    # Generation details
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='generated_financial_reports')
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Financial Report'
        verbose_name_plural = 'Financial Reports'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"


class TaxRate(BaseModel):
    """Tax rate model for different tax jurisdictions."""
    name = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Tax Rate'
        verbose_name_plural = 'Tax Rates'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.rate}%)"


class RecurringInvoice(BaseModel):
    """Recurring invoice template."""
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='recurring_invoices')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Recurring settings
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    interval = models.IntegerField(default=1)  # Every X days/weeks/months
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    # Invoice template
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_generated = models.DateField(null=True, blank=True)
    next_generation = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Recurring Invoice'
        verbose_name_plural = 'Recurring Invoices'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.customer.name}"


class RecurringInvoiceItem(BaseModel):
    """Recurring invoice line items."""
    recurring_invoice = models.ForeignKey(RecurringInvoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        verbose_name = 'Recurring Invoice Item'
        verbose_name_plural = 'Recurring Invoice Items'
    
    def __str__(self):
        return f"{self.recurring_invoice.name} - {self.description}"
