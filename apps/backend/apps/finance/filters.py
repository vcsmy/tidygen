"""
Finance management filters for TidyGen ERP platform.
"""
import django_filters
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from apps.finance.models import (
    Account, Customer, Vendor, Invoice, Payment, Expense,
    Budget, FinancialReport, TaxRate, RecurringInvoice
)


class AccountFilter(django_filters.FilterSet):
    """Filter for Account model."""
    name = django_filters.CharFilter(lookup_expr='icontains')
    code = django_filters.CharFilter(lookup_expr='icontains')
    account_type = django_filters.ChoiceFilter(choices=Account.ACCOUNT_TYPES)
    is_active = django_filters.BooleanFilter()
    parent = django_filters.ModelChoiceFilter(queryset=Account.objects.all())
    
    class Meta:
        model = Account
        fields = ['name', 'code', 'account_type', 'is_active', 'parent']


class CustomerFilter(django_filters.FilterSet):
    """Filter for Customer model."""
    name = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    city = django_filters.CharFilter(lookup_expr='icontains')
    state = django_filters.CharFilter(lookup_expr='icontains')
    country = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    
    # Date range filters
    created_after = django_filters.DateFilter(field_name='created', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created', lookup_expr='lte')
    
    class Meta:
        model = Customer
        fields = ['name', 'email', 'city', 'state', 'country', 'is_active']


class VendorFilter(django_filters.FilterSet):
    """Filter for Vendor model."""
    name = django_filters.CharFilter(lookup_expr='icontains')
    contact_person = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    city = django_filters.CharFilter(lookup_expr='icontains')
    state = django_filters.CharFilter(lookup_expr='icontains')
    country = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    
    # Date range filters
    created_after = django_filters.DateFilter(field_name='created', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created', lookup_expr='lte')
    
    class Meta:
        model = Vendor
        fields = ['name', 'contact_person', 'email', 'city', 'state', 'country', 'is_active']


class InvoiceFilter(django_filters.FilterSet):
    """Filter for Invoice model."""
    invoice_number = django_filters.CharFilter(lookup_expr='icontains')
    customer = django_filters.ModelChoiceFilter(queryset=Customer.objects.all())
    status = django_filters.ChoiceFilter(choices=Invoice.STATUS_CHOICES)
    created_by = django_filters.ModelChoiceFilter(queryset=Invoice._meta.get_field('created_by').related_model.objects.all())
    
    # Date range filters
    issue_date_after = django_filters.DateFilter(field_name='issue_date', lookup_expr='gte')
    issue_date_before = django_filters.DateFilter(field_name='issue_date', lookup_expr='lte')
    due_date_after = django_filters.DateFilter(field_name='due_date', lookup_expr='gte')
    due_date_before = django_filters.DateFilter(field_name='due_date', lookup_expr='lte')
    
    # Amount filters
    total_amount_min = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    total_amount_max = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte')
    
    # Overdue filter
    is_overdue = django_filters.BooleanFilter(method='filter_overdue')
    
    def filter_overdue(self, queryset, name, value):
        if value:
            today = timezone.now().date()
            return queryset.filter(
                due_date__lt=today,
                status__in=['sent', 'viewed']
            )
        return queryset
    
    class Meta:
        model = Invoice
        fields = ['invoice_number', 'customer', 'status', 'created_by']


class PaymentFilter(django_filters.FilterSet):
    """Filter for Payment model."""
    payment_number = django_filters.CharFilter(lookup_expr='icontains')
    customer = django_filters.ModelChoiceFilter(queryset=Customer.objects.all())
    invoice = django_filters.ModelChoiceFilter(queryset=Invoice.objects.all())
    payment_method = django_filters.ChoiceFilter(choices=Payment.PAYMENT_METHODS)
    received_by = django_filters.ModelChoiceFilter(queryset=Payment._meta.get_field('received_by').related_model.objects.all())
    
    # Date range filters
    payment_date_after = django_filters.DateFilter(field_name='payment_date', lookup_expr='gte')
    payment_date_before = django_filters.DateFilter(field_name='payment_date', lookup_expr='lte')
    
    # Amount filters
    amount_min = django_filters.NumberFilter(field_name='amount', lookup_expr='gte')
    amount_max = django_filters.NumberFilter(field_name='amount', lookup_expr='lte')
    
    class Meta:
        model = Payment
        fields = ['payment_number', 'customer', 'invoice', 'payment_method', 'received_by']


class ExpenseFilter(django_filters.FilterSet):
    """Filter for Expense model."""
    description = django_filters.CharFilter(lookup_expr='icontains')
    vendor = django_filters.ModelChoiceFilter(queryset=Vendor.objects.all())
    category = django_filters.ChoiceFilter(choices=Expense.CATEGORIES)
    status = django_filters.ChoiceFilter(choices=Expense.STATUS_CHOICES)
    submitted_by = django_filters.ModelChoiceFilter(queryset=Expense._meta.get_field('submitted_by').related_model.objects.all())
    approved_by = django_filters.ModelChoiceFilter(queryset=Expense._meta.get_field('approved_by').related_model.objects.all())
    
    # Date range filters
    expense_date_after = django_filters.DateFilter(field_name='expense_date', lookup_expr='gte')
    expense_date_before = django_filters.DateFilter(field_name='expense_date', lookup_expr='lte')
    
    # Amount filters
    amount_min = django_filters.NumberFilter(field_name='amount', lookup_expr='gte')
    amount_max = django_filters.NumberFilter(field_name='amount', lookup_expr='lte')
    
    # Receipt number filter
    receipt_number = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Expense
        fields = ['description', 'vendor', 'category', 'status', 'submitted_by', 'approved_by', 'receipt_number']


class BudgetFilter(django_filters.FilterSet):
    """Filter for Budget model."""
    name = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    
    # Date range filters
    start_date_after = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_before = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')
    end_date_after = django_filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_date_before = django_filters.DateFilter(field_name='end_date', lookup_expr='lte')
    
    # Amount filters
    total_budget_min = django_filters.NumberFilter(field_name='total_budget', lookup_expr='gte')
    total_budget_max = django_filters.NumberFilter(field_name='total_budget', lookup_expr='lte')
    
    # Current budget filter
    is_current = django_filters.BooleanFilter(method='filter_current')
    
    def filter_current(self, queryset, name, value):
        if value:
            today = timezone.now().date()
            return queryset.filter(
                start_date__lte=today,
                end_date__gte=today,
                is_active=True
            )
        return queryset
    
    class Meta:
        model = Budget
        fields = ['name', 'is_active']


class FinancialReportFilter(django_filters.FilterSet):
    """Filter for FinancialReport model."""
    name = django_filters.CharFilter(lookup_expr='icontains')
    report_type = django_filters.ChoiceFilter(choices=FinancialReport.REPORT_TYPES)
    generated_by = django_filters.ModelChoiceFilter(queryset=FinancialReport._meta.get_field('generated_by').related_model.objects.all())
    
    # Date range filters
    start_date_after = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_before = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')
    end_date_after = django_filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_date_before = django_filters.DateFilter(field_name='end_date', lookup_expr='lte')
    
    # Generated date filters
    generated_after = django_filters.DateTimeFilter(field_name='generated_at', lookup_expr='gte')
    generated_before = django_filters.DateTimeFilter(field_name='generated_at', lookup_expr='lte')
    
    class Meta:
        model = FinancialReport
        fields = ['name', 'report_type', 'generated_by']


class TaxRateFilter(django_filters.FilterSet):
    """Filter for TaxRate model."""
    name = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    
    # Rate filters
    rate_min = django_filters.NumberFilter(field_name='rate', lookup_expr='gte')
    rate_max = django_filters.NumberFilter(field_name='rate', lookup_expr='lte')
    
    class Meta:
        model = TaxRate
        fields = ['name', 'is_active']


class RecurringInvoiceFilter(django_filters.FilterSet):
    """Filter for RecurringInvoice model."""
    name = django_filters.CharFilter(lookup_expr='icontains')
    customer = django_filters.ModelChoiceFilter(queryset=Customer.objects.all())
    frequency = django_filters.ChoiceFilter(choices=RecurringInvoice.FREQUENCY_CHOICES)
    is_active = django_filters.BooleanFilter()
    
    # Date range filters
    start_date_after = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_before = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')
    end_date_after = django_filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_date_before = django_filters.DateFilter(field_name='end_date', lookup_expr='lte')
    
    # Amount filters
    total_amount_min = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    total_amount_max = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte')
    
    # Due for generation filter
    due_for_generation = django_filters.BooleanFilter(method='filter_due_for_generation')
    
    def filter_due_for_generation(self, queryset, name, value):
        if value:
            today = timezone.now().date()
            return queryset.filter(
                is_active=True,
                next_generation__lte=today
            )
        return queryset
    
    class Meta:
        model = RecurringInvoice
        fields = ['name', 'customer', 'frequency', 'is_active']


# Advanced filters for analytics and reporting
class InvoiceAnalyticsFilter(django_filters.FilterSet):
    """Advanced filter for invoice analytics."""
    date_range = django_filters.ChoiceFilter(
        choices=[
            ('today', 'Today'),
            ('yesterday', 'Yesterday'),
            ('this_week', 'This Week'),
            ('last_week', 'Last Week'),
            ('this_month', 'This Month'),
            ('last_month', 'Last Month'),
            ('this_quarter', 'This Quarter'),
            ('last_quarter', 'Last Quarter'),
            ('this_year', 'This Year'),
            ('last_year', 'Last Year'),
            ('custom', 'Custom Range'),
        ],
        method='filter_date_range'
    )
    
    start_date = django_filters.DateFilter(field_name='issue_date', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='issue_date', lookup_expr='lte')
    
    def filter_date_range(self, queryset, name, value):
        today = timezone.now().date()
        
        if value == 'today':
            return queryset.filter(issue_date=today)
        elif value == 'yesterday':
            yesterday = today - timedelta(days=1)
            return queryset.filter(issue_date=yesterday)
        elif value == 'this_week':
            start_of_week = today - timedelta(days=today.weekday())
            return queryset.filter(issue_date__gte=start_of_week)
        elif value == 'last_week':
            start_of_last_week = today - timedelta(days=today.weekday() + 7)
            end_of_last_week = start_of_last_week + timedelta(days=6)
            return queryset.filter(issue_date__gte=start_of_last_week, issue_date__lte=end_of_last_week)
        elif value == 'this_month':
            start_of_month = today.replace(day=1)
            return queryset.filter(issue_date__gte=start_of_month)
        elif value == 'last_month':
            if today.month == 1:
                start_of_last_month = today.replace(year=today.year - 1, month=12, day=1)
            else:
                start_of_last_month = today.replace(month=today.month - 1, day=1)
            end_of_last_month = today.replace(day=1) - timedelta(days=1)
            return queryset.filter(issue_date__gte=start_of_last_month, issue_date__lte=end_of_last_month)
        elif value == 'this_quarter':
            quarter = (today.month - 1) // 3 + 1
            start_of_quarter = today.replace(month=(quarter - 1) * 3 + 1, day=1)
            return queryset.filter(issue_date__gte=start_of_quarter)
        elif value == 'last_quarter':
            quarter = (today.month - 1) // 3 + 1
            if quarter == 1:
                start_of_last_quarter = today.replace(year=today.year - 1, month=10, day=1)
            else:
                start_of_last_quarter = today.replace(month=(quarter - 2) * 3 + 1, day=1)
            end_of_last_quarter = today.replace(month=(quarter - 1) * 3 + 1, day=1) - timedelta(days=1)
            return queryset.filter(issue_date__gte=start_of_last_quarter, issue_date__lte=end_of_last_quarter)
        elif value == 'this_year':
            start_of_year = today.replace(month=1, day=1)
            return queryset.filter(issue_date__gte=start_of_year)
        elif value == 'last_year':
            start_of_last_year = today.replace(year=today.year - 1, month=1, day=1)
            end_of_last_year = today.replace(year=today.year - 1, month=12, day=31)
            return queryset.filter(issue_date__gte=start_of_last_year, issue_date__lte=end_of_last_year)
        
        return queryset
    
    class Meta:
        model = Invoice
        fields = ['date_range', 'start_date', 'end_date']


class ExpenseAnalyticsFilter(django_filters.FilterSet):
    """Advanced filter for expense analytics."""
    date_range = django_filters.ChoiceFilter(
        choices=[
            ('today', 'Today'),
            ('yesterday', 'Yesterday'),
            ('this_week', 'This Week'),
            ('last_week', 'Last Week'),
            ('this_month', 'This Month'),
            ('last_month', 'Last Month'),
            ('this_quarter', 'This Quarter'),
            ('last_quarter', 'Last Quarter'),
            ('this_year', 'This Year'),
            ('last_year', 'Last Year'),
            ('custom', 'Custom Range'),
        ],
        method='filter_date_range'
    )
    
    start_date = django_filters.DateFilter(field_name='expense_date', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='expense_date', lookup_expr='lte')
    
    def filter_date_range(self, queryset, name, value):
        today = timezone.now().date()
        
        if value == 'today':
            return queryset.filter(expense_date=today)
        elif value == 'yesterday':
            yesterday = today - timedelta(days=1)
            return queryset.filter(expense_date=yesterday)
        elif value == 'this_week':
            start_of_week = today - timedelta(days=today.weekday())
            return queryset.filter(expense_date__gte=start_of_week)
        elif value == 'last_week':
            start_of_last_week = today - timedelta(days=today.weekday() + 7)
            end_of_last_week = start_of_last_week + timedelta(days=6)
            return queryset.filter(expense_date__gte=start_of_last_week, expense_date__lte=end_of_last_week)
        elif value == 'this_month':
            start_of_month = today.replace(day=1)
            return queryset.filter(expense_date__gte=start_of_month)
        elif value == 'last_month':
            if today.month == 1:
                start_of_last_month = today.replace(year=today.year - 1, month=12, day=1)
            else:
                start_of_last_month = today.replace(month=today.month - 1, day=1)
            end_of_last_month = today.replace(day=1) - timedelta(days=1)
            return queryset.filter(expense_date__gte=start_of_last_month, expense_date__lte=end_of_last_month)
        elif value == 'this_quarter':
            quarter = (today.month - 1) // 3 + 1
            start_of_quarter = today.replace(month=(quarter - 1) * 3 + 1, day=1)
            return queryset.filter(expense_date__gte=start_of_quarter)
        elif value == 'last_quarter':
            quarter = (today.month - 1) // 3 + 1
            if quarter == 1:
                start_of_last_quarter = today.replace(year=today.year - 1, month=10, day=1)
            else:
                start_of_last_quarter = today.replace(month=(quarter - 2) * 3 + 1, day=1)
            end_of_last_quarter = today.replace(month=(quarter - 1) * 3 + 1, day=1) - timedelta(days=1)
            return queryset.filter(expense_date__gte=start_of_last_quarter, expense_date__lte=end_of_last_quarter)
        elif value == 'this_year':
            start_of_year = today.replace(month=1, day=1)
            return queryset.filter(expense_date__gte=start_of_year)
        elif value == 'last_year':
            start_of_last_year = today.replace(year=today.year - 1, month=1, day=1)
            end_of_last_year = today.replace(year=today.year - 1, month=12, day=31)
            return queryset.filter(expense_date__gte=start_of_last_year, expense_date__lte=end_of_last_year)
        
        return queryset
    
    class Meta:
        model = Expense
        fields = ['date_range', 'start_date', 'end_date']
