"""
Comprehensive payroll management admin configuration.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Sum, Count, Avg
from decimal import Decimal

from .models import (
    PayrollConfiguration, PayrollComponent, EmployeePayrollProfile,
    PayrollRun, PayrollItem, PayrollAdjustment, TaxYear, EmployeeTaxInfo,
    PayrollReport, PayrollAnalytics, PayrollIntegration, PayrollWebhook,
    PayrollNotification
)


# ==================== PAYROLL CONFIGURATION ADMIN ====================

@admin.register(PayrollConfiguration)
class PayrollConfigurationAdmin(admin.ModelAdmin):
    """Admin for PayrollConfiguration."""
    list_display = [
        'organization', 'currency', 'pay_frequency', 'tax_year',
        'federal_tax_rate', 'state_tax_rate', 'social_security_rate',
        'auto_process_payroll', 'require_approval'
    ]
    list_filter = [
        'currency', 'pay_frequency', 'tax_year', 'auto_process_payroll',
        'require_approval', 'allow_manual_adjustments'
    ]
    search_fields = ['organization__name']
    readonly_fields = ['created_at', 'modified_at']
    
    fieldsets = (
        ('Basic Settings', {
            'fields': ('organization', 'currency', 'pay_frequency', 'tax_year')
        }),
        ('Tax Rates', {
            'fields': (
                'federal_tax_rate', 'state_tax_rate', 'local_tax_rate',
                'social_security_rate', 'social_security_wage_base',
                'medicare_rate', 'medicare_additional_rate', 'medicare_additional_threshold'
            )
        }),
        ('Overtime Settings', {
            'fields': (
                'overtime_multiplier', 'double_time_multiplier', 'overtime_threshold'
            )
        }),
        ('Benefits Settings', {
            'fields': (
                'holiday_pay_multiplier', 'vacation_accrual_rate', 'sick_leave_accrual_rate'
            )
        }),
        ('Processing Settings', {
            'fields': (
                'auto_process_payroll', 'require_approval', 'allow_manual_adjustments'
            )
        }),
        ('Notification Settings', {
            'fields': (
                'notify_employees', 'notify_managers', 'notify_hr'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(PayrollComponent)
class PayrollComponentAdmin(admin.ModelAdmin):
    """Admin for PayrollComponent."""
    list_display = [
        'name', 'organization', 'component_type', 'calculation_type',
        'amount', 'percentage', 'is_taxable', 'is_active', 'is_mandatory', 'sort_order'
    ]
    list_filter = [
        'component_type', 'calculation_type', 'is_taxable', 'is_pretax',
        'is_active', 'is_mandatory', 'category'
    ]
    search_fields = ['name', 'description', 'category', 'organization__name']
    list_editable = ['sort_order', 'is_active', 'is_mandatory']
    readonly_fields = ['created_at', 'modified_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'name', 'component_type', 'description', 'category')
        }),
        ('Calculation Settings', {
            'fields': ('calculation_type', 'amount', 'percentage')
        }),
        ('Tax Settings', {
            'fields': ('is_taxable', 'is_pretax')
        }),
        ('Status Settings', {
            'fields': ('is_active', 'is_mandatory', 'sort_order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(EmployeePayrollProfile)
class EmployeePayrollProfileAdmin(admin.ModelAdmin):
    """Admin for EmployeePayrollProfile."""
    list_display = [
        'employee', 'pay_type', 'base_salary', 'hourly_rate',
        'federal_exemptions', 'state_exemptions', 'is_active', 'effective_date'
    ]
    list_filter = [
        'pay_type', 'is_active', 'account_type', 'effective_date'
    ]
    search_fields = [
        'employee__user__first_name', 'employee__user__last_name',
        'employee__employee_id', 'employee__organization__name'
    ]
    readonly_fields = ['created_at', 'modified_at']
    
    fieldsets = (
        ('Employee Information', {
            'fields': ('employee', 'pay_type', 'effective_date', 'is_active')
        }),
        ('Pay Rates', {
            'fields': ('base_salary', 'hourly_rate', 'commission_rate')
        }),
        ('Tax Settings', {
            'fields': (
                'federal_exemptions', 'state_exemptions',
                'additional_federal_withholding', 'additional_state_withholding'
            )
        }),
        ('Direct Deposit', {
            'fields': (
                'bank_name', 'bank_routing_number', 'bank_account_number', 'account_type'
            )
        }),
        ('Benefits', {
            'fields': (
                'health_insurance_deduction', 'dental_insurance_deduction',
                'vision_insurance_deduction', 'retirement_contribution', 'retirement_match'
            )
        }),
        ('Custom Components', {
            'fields': ('custom_allowances', 'custom_deductions'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        })
    )


# ==================== ENHANCED PAYROLL ADMIN ====================

class PayrollItemInline(admin.TabularInline):
    """Inline admin for PayrollItem."""
    model = PayrollItem
    extra = 0
    readonly_fields = ['created_at', 'modified_at']
    fields = [
        'component', 'item_type', 'quantity', 'rate', 'amount',
        'is_taxable', 'is_pretax', 'description', 'reference'
    ]


class PayrollAdjustmentInline(admin.TabularInline):
    """Inline admin for PayrollAdjustment."""
    model = PayrollAdjustment
    extra = 0
    readonly_fields = ['created_at', 'modified_at', 'approved_at']
    fields = [
        'adjustment_type', 'amount', 'is_positive', 'is_taxable',
        'reason', 'reference_document', 'approved_by', 'approved_at'
    ]


@admin.register(PayrollRun)
class PayrollRunAdmin(admin.ModelAdmin):
    """Admin for PayrollRun."""
    list_display = [
        'run_name', 'organization', 'payroll_period', 'run_type', 'status',
        'total_employees', 'total_gross_pay', 'total_net_pay', 'processed_at'
    ]
    list_filter = [
        'run_type', 'status', 'organization', 'processed_at', 'approved_at'
    ]
    search_fields = [
        'run_name', 'notes', 'organization__name', 'payroll_period__name'
    ]
    readonly_fields = [
        'created_at', 'modified_at', 'processed_at', 'approved_at',
        'total_employees', 'total_gross_pay', 'total_deductions', 'total_net_pay', 'total_taxes'
    ]
    inlines = [PayrollItemInline, PayrollAdjustmentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'payroll_period', 'run_name', 'run_type', 'status')
        }),
        ('Processing Information', {
            'fields': (
                'processed_by', 'processed_at', 'approved_by', 'approved_at'
            )
        }),
        ('Totals', {
            'fields': (
                'total_employees', 'total_gross_pay', 'total_deductions',
                'total_net_pay', 'total_taxes'
            )
        }),
        ('Additional Information', {
            'fields': ('notes', 'error_log'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'organization', 'payroll_period', 'processed_by', 'approved_by'
        )


@admin.register(PayrollItem)
class PayrollItemAdmin(admin.ModelAdmin):
    """Admin for PayrollItem."""
    list_display = [
        'payroll_employee', 'component', 'item_type', 'quantity',
        'rate', 'amount', 'is_taxable', 'is_pretax'
    ]
    list_filter = [
        'item_type', 'is_taxable', 'is_pretax', 'component__component_type'
    ]
    search_fields = [
        'payroll__employee__user__first_name', 'payroll__employee__user__last_name',
        'component__name', 'description', 'reference'
    ]
    readonly_fields = ['created_at', 'modified_at']
    
    def payroll_employee(self, obj):
        """Display employee name."""
        return obj.payroll.employee.full_name
    payroll_employee.short_description = 'Employee'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('payroll', 'payroll_run', 'component', 'item_type')
        }),
        ('Amounts', {
            'fields': ('quantity', 'rate', 'amount')
        }),
        ('Tax Settings', {
            'fields': ('is_taxable', 'is_pretax')
        }),
        ('Additional Information', {
            'fields': ('description', 'reference')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(PayrollAdjustment)
class PayrollAdjustmentAdmin(admin.ModelAdmin):
    """Admin for PayrollAdjustment."""
    list_display = [
        'payroll_employee', 'adjustment_type', 'amount', 'is_positive',
        'is_taxable', 'approved_by', 'approved_at', 'created_at'
    ]
    list_filter = [
        'adjustment_type', 'is_positive', 'is_taxable', 'is_pretax',
        'approved_at', 'created_at'
    ]
    search_fields = [
        'payroll__employee__user__first_name', 'payroll__employee__user__last_name',
        'reason', 'reference_document'
    ]
    readonly_fields = ['created_at', 'modified_at', 'approved_at']
    
    def payroll_employee(self, obj):
        """Display employee name."""
        return obj.payroll.employee.full_name
    payroll_employee.short_description = 'Employee'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('payroll', 'payroll_run', 'adjustment_type')
        }),
        ('Amounts', {
            'fields': ('amount', 'is_positive')
        }),
        ('Tax Settings', {
            'fields': ('is_taxable', 'is_pretax')
        }),
        ('Approval', {
            'fields': ('approved_by', 'approved_at')
        }),
        ('Additional Information', {
            'fields': ('reason', 'reference_document')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        })
    )


# ==================== TAX AND COMPLIANCE ADMIN ====================

@admin.register(TaxYear)
class TaxYearAdmin(admin.ModelAdmin):
    """Admin for TaxYear."""
    list_display = [
        'year', 'organization', 'federal_tax_rate', 'state_tax_rate',
        'social_security_rate', 'medicare_rate', 'is_active'
    ]
    list_filter = ['year', 'is_active', 'organization']
    search_fields = ['organization__name']
    readonly_fields = ['created_at', 'modified_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'year', 'is_active')
        }),
        ('Tax Rates', {
            'fields': (
                'federal_tax_rate', 'state_tax_rate', 'local_tax_rate'
            )
        }),
        ('Social Security', {
            'fields': ('social_security_rate', 'social_security_wage_base')
        }),
        ('Medicare', {
            'fields': (
                'medicare_rate', 'medicare_additional_rate', 'medicare_additional_threshold'
            )
        }),
        ('Standard Deductions', {
            'fields': ('standard_deduction_single', 'standard_deduction_married')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(EmployeeTaxInfo)
class EmployeeTaxInfoAdmin(admin.ModelAdmin):
    """Admin for EmployeeTaxInfo."""
    list_display = [
        'employee', 'tax_year', 'filing_status', 'federal_exemptions',
        'state_exemptions', 'ytd_gross_wages', 'ytd_federal_tax'
    ]
    list_filter = [
        'filing_status', 'tax_year', 'w4_form_date', 'state_tax_form_date'
    ]
    search_fields = [
        'employee__user__first_name', 'employee__user__last_name',
        'employee__employee_id', 'employee__organization__name'
    ]
    readonly_fields = ['created_at', 'modified_at']
    
    fieldsets = (
        ('Employee Information', {
            'fields': ('employee', 'tax_year')
        }),
        ('Filing Status', {
            'fields': ('filing_status',)
        }),
        ('Exemptions', {
            'fields': ('federal_exemptions', 'state_exemptions')
        }),
        ('Additional Withholding', {
            'fields': (
                'additional_federal_withholding', 'additional_state_withholding'
            )
        }),
        ('Tax Forms', {
            'fields': ('w4_form_date', 'state_tax_form_date')
        }),
        ('Year-to-Date Totals', {
            'fields': (
                'ytd_gross_wages', 'ytd_federal_tax', 'ytd_state_tax',
                'ytd_social_security', 'ytd_medicare'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        })
    )


# ==================== PAYROLL REPORTS AND ANALYTICS ADMIN ====================

@admin.register(PayrollReport)
class PayrollReportAdmin(admin.ModelAdmin):
    """Admin for PayrollReport."""
    list_display = [
        'report_name', 'organization', 'report_type', 'start_date',
        'end_date', 'status', 'generated_by', 'generated_at'
    ]
    list_filter = [
        'report_type', 'status', 'generated_at', 'start_date', 'end_date'
    ]
    search_fields = [
        'report_name', 'organization__name', 'generated_by__username'
    ]
    readonly_fields = [
        'created_at', 'modified_at', 'generated_at', 'report_data', 'totals'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'report_name', 'report_type', 'status')
        }),
        ('Date Range', {
            'fields': ('start_date', 'end_date')
        }),
        ('Filters', {
            'fields': ('departments', 'employees', 'payroll_periods'),
            'classes': ('collapse',)
        }),
        ('Report Data', {
            'fields': ('report_data', 'totals'),
            'classes': ('collapse',)
        }),
        ('Generation Information', {
            'fields': ('generated_by', 'generated_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(PayrollAnalytics)
class PayrollAnalyticsAdmin(admin.ModelAdmin):
    """Admin for PayrollAnalytics."""
    list_display = [
        'organization', 'period_start', 'period_end', 'period_type',
        'total_employees', 'total_gross_pay', 'total_net_pay', 'average_gross_pay'
    ]
    list_filter = [
        'period_type', 'period_start', 'period_end', 'organization'
    ]
    search_fields = ['organization__name']
    readonly_fields = [
        'created_at', 'modified_at', 'total_employees', 'total_gross_pay',
        'total_net_pay', 'total_taxes', 'total_benefits', 'total_overtime',
        'average_gross_pay', 'average_net_pay', 'average_hours_worked',
        'gross_pay_trend', 'employee_count_trend'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'period_start', 'period_end', 'period_type')
        }),
        ('Employee Statistics', {
            'fields': ('total_employees', 'average_gross_pay', 'average_net_pay', 'average_hours_worked')
        }),
        ('Payroll Totals', {
            'fields': (
                'total_gross_pay', 'total_net_pay', 'total_taxes',
                'total_benefits', 'total_overtime'
            )
        }),
        ('Trends', {
            'fields': ('gross_pay_trend', 'employee_count_trend')
        }),
        ('Additional Metrics', {
            'fields': ('metrics',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        })
    )


# ==================== PAYROLL INTEGRATION ADMIN ====================

@admin.register(PayrollIntegration)
class PayrollIntegrationAdmin(admin.ModelAdmin):
    """Admin for PayrollIntegration."""
    list_display = [
        'integration_name', 'organization', 'integration_type',
        'provider_name', 'is_active', 'sync_status', 'last_sync'
    ]
    list_filter = [
        'integration_type', 'is_active', 'sync_status', 'last_sync'
    ]
    search_fields = [
        'integration_name', 'provider_name', 'organization__name'
    ]
    readonly_fields = [
        'created_at', 'modified_at', 'last_sync', 'token_expires_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'integration_name', 'integration_type')
        }),
        ('Provider Information', {
            'fields': ('provider_name', 'provider_url')
        }),
        ('Configuration', {
            'fields': ('is_active', 'configuration'),
            'classes': ('collapse',)
        }),
        ('Authentication', {
            'fields': (
                'api_key', 'api_secret', 'access_token', 'refresh_token', 'token_expires_at'
            ),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('sync_status', 'last_sync', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(PayrollWebhook)
class PayrollWebhookAdmin(admin.ModelAdmin):
    """Admin for PayrollWebhook."""
    list_display = [
        'event_type', 'integration', 'webhook_url', 'is_active',
        'total_calls', 'successful_calls', 'failed_calls', 'success_rate'
    ]
    list_filter = [
        'event_type', 'is_active', 'integration__integration_type'
    ]
    search_fields = [
        'event_type', 'webhook_url', 'integration__integration_name'
    ]
    readonly_fields = [
        'created_at', 'modified_at', 'total_calls', 'successful_calls',
        'failed_calls', 'last_called'
    ]
    
    def success_rate(self, obj):
        """Calculate success rate."""
        if obj.total_calls > 0:
            rate = (obj.successful_calls / obj.total_calls) * 100
            return f"{rate:.1f}%"
        return "N/A"
    success_rate.short_description = 'Success Rate'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'integration', 'event_type', 'webhook_url')
        }),
        ('Security', {
            'fields': ('secret_key', 'is_active'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': (
                'total_calls', 'successful_calls', 'failed_calls', 'last_called'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        })
    )


# ==================== PAYROLL NOTIFICATIONS ADMIN ====================

@admin.register(PayrollNotification)
class PayrollNotificationAdmin(admin.ModelAdmin):
    """Admin for PayrollNotification."""
    list_display = [
        'notification_type', 'subject', 'organization', 'delivery_method',
        'status', 'scheduled_at', 'sent_at', 'created_at'
    ]
    list_filter = [
        'notification_type', 'delivery_method', 'status', 'scheduled_at', 'sent_at'
    ]
    search_fields = [
        'subject', 'message', 'organization__name'
    ]
    readonly_fields = [
        'created_at', 'modified_at', 'sent_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'notification_type', 'subject', 'message')
        }),
        ('Recipients', {
            'fields': ('recipients',)
        }),
        ('Delivery', {
            'fields': ('delivery_method', 'status', 'scheduled_at', 'sent_at')
        }),
        ('Related Objects', {
            'fields': ('related_payroll', 'related_payroll_run'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        })
    )


# ==================== ADMIN CUSTOMIZATIONS ====================

# Customize admin site
admin.site.site_header = "TidyGen ERP - Payroll Management"
admin.site.site_title = "Payroll Admin"
admin.site.index_title = "Payroll Management System"

# Add custom admin actions
def approve_payroll_runs(modeladmin, request, queryset):
    """Approve selected payroll runs."""
    updated = queryset.filter(status='review').update(
        status='approved',
        approved_by=request.user,
        approved_at=timezone.now()
    )
    modeladmin.message_user(request, f"{updated} payroll runs approved.")

def process_payroll_runs(modeladmin, request, queryset):
    """Process selected payroll runs."""
    updated = queryset.filter(status='draft').update(
        status='processing',
        processed_by=request.user,
        processed_at=timezone.now()
    )
    modeladmin.message_user(request, f"{updated} payroll runs processed.")

def mark_payroll_runs_paid(modeladmin, request, queryset):
    """Mark selected payroll runs as paid."""
    updated = queryset.filter(status='approved').update(status='paid')
    modeladmin.message_user(request, f"{updated} payroll runs marked as paid.")

# Add actions to PayrollRunAdmin
PayrollRunAdmin.actions = [approve_payroll_runs, process_payroll_runs, mark_payroll_runs_paid]

# Add custom admin actions for adjustments
def approve_adjustments(modeladmin, request, queryset):
    """Approve selected payroll adjustments."""
    updated = queryset.filter(approved_at__isnull=True).update(
        approved_by=request.user,
        approved_at=timezone.now()
    )
    modeladmin.message_user(request, f"{updated} adjustments approved.")

PayrollAdjustmentAdmin.actions = [approve_adjustments]

# Add custom admin actions for notifications
def send_notifications(modeladmin, request, queryset):
    """Send selected notifications."""
    updated = queryset.filter(status='pending').update(
        status='sent',
        sent_at=timezone.now()
    )
    modeladmin.message_user(request, f"{updated} notifications sent.")

PayrollNotificationAdmin.actions = [send_notifications]
