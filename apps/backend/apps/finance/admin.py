"""
Django admin configuration for finance models.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from apps.finance.models import (
    Account, Customer, Vendor, Invoice, InvoiceItem, Payment, Expense,
    Budget, BudgetItem, FinancialReport, TaxRate, RecurringInvoice, RecurringInvoiceItem
)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'account_type', 'parent', 'balance', 'is_active']
    list_filter = ['account_type', 'is_active', 'parent']
    search_fields = ['name', 'code', 'description']
    ordering = ['code']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'account_type', 'parent', 'description')
        }),
        ('Financial', {
            'fields': ('balance',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    fields = ['description', 'quantity', 'unit_price', 'total_price']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer', 'status', 'issue_date', 'due_date', 'total_amount', 'paid_amount', 'balance_due_display']
    list_filter = ['status', 'issue_date', 'due_date', 'created_by']
    search_fields = ['invoice_number', 'customer__name', 'notes']
    ordering = ['-issue_date']
    list_editable = ['status']
    inlines = [InvoiceItemInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('invoice_number', 'customer', 'status', 'created_by')
        }),
        ('Dates', {
            'fields': ('issue_date', 'due_date', 'sent_date', 'paid_date')
        }),
        ('Financial', {
            'fields': ('subtotal', 'tax_rate', 'tax_amount', 'discount_amount', 'total_amount', 'paid_amount')
        }),
        ('Additional Information', {
            'fields': ('notes', 'terms_conditions')
        }),
    )
    
    readonly_fields = ['subtotal', 'tax_amount', 'total_amount', 'paid_amount']
    
    def balance_due_display(self, obj):
        balance = obj.balance_due
        if balance > 0:
            return format_html('<span style="color: red;">${}</span>', balance)
        return format_html('<span style="color: green;">${}</span>', balance)
    balance_due_display.short_description = 'Balance Due'


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'city', 'credit_limit', 'is_active']
    list_filter = ['is_active', 'city', 'state', 'country']
    search_fields = ['name', 'email', 'phone', 'city', 'state']
    ordering = ['name']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Financial', {
            'fields': ('credit_limit', 'payment_terms', 'tax_id')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'email', 'phone', 'city', 'is_active']
    list_filter = ['is_active', 'city', 'state', 'country']
    search_fields = ['name', 'contact_person', 'email', 'phone', 'city']
    ordering = ['name']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'contact_person', 'email', 'phone')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Financial', {
            'fields': ('payment_terms', 'tax_id')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_number', 'customer', 'invoice_link', 'amount', 'payment_method', 'payment_date', 'received_by']
    list_filter = ['payment_method', 'payment_date', 'received_by']
    search_fields = ['payment_number', 'customer__name', 'reference_number', 'notes']
    ordering = ['-payment_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('payment_number', 'customer', 'invoice', 'received_by')
        }),
        ('Payment Details', {
            'fields': ('amount', 'payment_method', 'payment_date', 'reference_number')
        }),
        ('Bank Information', {
            'fields': ('bank_name', 'account_number')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
    )
    
    def invoice_link(self, obj):
        if obj.invoice:
            url = reverse('admin:finance_invoice_change', args=[obj.invoice.id])
            return format_html('<a href="{}">{}</a>', url, obj.invoice.invoice_number)
        return '-'
    invoice_link.short_description = 'Invoice'


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['description', 'vendor', 'category', 'status', 'amount', 'expense_date', 'submitted_by', 'approved_by']
    list_filter = ['category', 'status', 'expense_date', 'submitted_by', 'approved_by']
    search_fields = ['description', 'vendor__name', 'receipt_number']
    ordering = ['-expense_date']
    list_editable = ['status']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('vendor', 'category', 'status', 'submitted_by')
        }),
        ('Expense Details', {
            'fields': ('description', 'amount', 'tax_amount', 'total_amount', 'expense_date', 'receipt_number', 'receipt_image')
        }),
        ('Approval', {
            'fields': ('approved_by', 'approved_at', 'rejection_reason')
        }),
    )
    
    readonly_fields = ['total_amount', 'approved_at']


class BudgetItemInline(admin.TabularInline):
    model = BudgetItem
    extra = 0
    fields = ['category', 'description', 'budgeted_amount', 'spent_amount']


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'total_budget', 'spent_amount', 'remaining_budget_display', 'is_active']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['name', 'description']
    ordering = ['-start_date']
    list_editable = ['is_active']
    inlines = [BudgetItemInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Budget Period', {
            'fields': ('start_date', 'end_date')
        }),
        ('Financial', {
            'fields': ('total_budget', 'spent_amount')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ['spent_amount']
    
    def remaining_budget_display(self, obj):
        remaining = obj.remaining_budget
        if remaining < 0:
            return format_html('<span style="color: red;">${}</span>', remaining)
        return format_html('<span style="color: green;">${}</span>', remaining)
    remaining_budget_display.short_description = 'Remaining Budget'


@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'start_date', 'end_date', 'generated_by', 'generated_at']
    list_filter = ['report_type', 'start_date', 'end_date', 'generated_by']
    search_fields = ['name']
    ordering = ['-generated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'report_type', 'generated_by')
        }),
        ('Report Period', {
            'fields': ('start_date', 'end_date')
        }),
        ('Report Data', {
            'fields': ('report_data',)
        }),
    )
    
    readonly_fields = ['generated_at']


@admin.register(TaxRate)
class TaxRateAdmin(admin.ModelAdmin):
    list_display = ['name', 'rate', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    ordering = ['name']
    list_editable = ['is_active']


class RecurringInvoiceItemInline(admin.TabularInline):
    model = RecurringInvoiceItem
    extra = 0
    fields = ['description', 'quantity', 'unit_price', 'total_price']


@admin.register(RecurringInvoice)
class RecurringInvoiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'customer', 'frequency', 'total_amount', 'is_active', 'last_generated', 'next_generation']
    list_filter = ['frequency', 'is_active', 'start_date', 'end_date']
    search_fields = ['name', 'customer__name', 'description']
    ordering = ['name']
    list_editable = ['is_active']
    inlines = [RecurringInvoiceItemInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'customer', 'description')
        }),
        ('Recurring Settings', {
            'fields': ('frequency', 'interval', 'start_date', 'end_date')
        }),
        ('Invoice Template', {
            'fields': ('subtotal', 'tax_rate', 'total_amount')
        }),
        ('Status', {
            'fields': ('is_active', 'last_generated', 'next_generation')
        }),
    )
    
    readonly_fields = ['last_generated', 'next_generation']


# Customize admin site
admin.site.site_header = "TidyGen ERP Finance Management"
admin.site.site_title = "TidyGen Finance Admin"
admin.site.index_title = "Finance Administration"
