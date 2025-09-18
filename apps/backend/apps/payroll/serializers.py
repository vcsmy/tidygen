"""
Comprehensive payroll management serializers.
"""
from rest_framework import serializers
from decimal import Decimal
from datetime import date, timedelta

from .models import (
    PayrollConfiguration, PayrollComponent, EmployeePayrollProfile,
    PayrollRun, PayrollItem, PayrollAdjustment, TaxYear, EmployeeTaxInfo,
    PayrollReport, PayrollAnalytics, PayrollIntegration, PayrollWebhook,
    PayrollNotification
)
from apps.hr.models import Employee, PayrollPeriod, Payroll


# ==================== PAYROLL CONFIGURATION SERIALIZERS ====================

class PayrollConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for PayrollConfiguration."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = PayrollConfiguration
        fields = [
            'id', 'organization', 'organization_name', 'currency', 'pay_frequency',
            'tax_year', 'federal_tax_rate', 'state_tax_rate', 'local_tax_rate',
            'social_security_rate', 'social_security_wage_base', 'medicare_rate',
            'medicare_additional_rate', 'medicare_additional_threshold',
            'overtime_multiplier', 'double_time_multiplier', 'overtime_threshold',
            'holiday_pay_multiplier', 'vacation_accrual_rate', 'sick_leave_accrual_rate',
            'auto_process_payroll', 'require_approval', 'allow_manual_adjustments',
            'notify_employees', 'notify_managers', 'notify_hr', 'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']


class PayrollComponentSerializer(serializers.ModelSerializer):
    """Serializer for PayrollComponent."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = PayrollComponent
        fields = [
            'id', 'organization', 'organization_name', 'name', 'component_type',
            'calculation_type', 'amount', 'percentage', 'is_taxable', 'is_pretax',
            'is_active', 'is_mandatory', 'description', 'category', 'sort_order',
            'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']


class EmployeePayrollProfileSerializer(serializers.ModelSerializer):
    """Serializer for EmployeePayrollProfile."""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    
    class Meta:
        model = EmployeePayrollProfile
        fields = [
            'id', 'employee', 'employee_name', 'employee_id', 'pay_type',
            'base_salary', 'hourly_rate', 'commission_rate', 'federal_exemptions',
            'state_exemptions', 'additional_federal_withholding', 'additional_state_withholding',
            'bank_name', 'bank_routing_number', 'bank_account_number', 'account_type',
            'health_insurance_deduction', 'dental_insurance_deduction', 'vision_insurance_deduction',
            'retirement_contribution', 'retirement_match', 'custom_allowances',
            'custom_deductions', 'is_active', 'effective_date', 'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']


# ==================== ENHANCED PAYROLL SERIALIZERS ====================

class PayrollRunSerializer(serializers.ModelSerializer):
    """Serializer for PayrollRun."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    payroll_period_name = serializers.CharField(source='payroll_period.name', read_only=True)
    processed_by_name = serializers.CharField(source='processed_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = PayrollRun
        fields = [
            'id', 'organization', 'organization_name', 'payroll_period', 'payroll_period_name',
            'run_name', 'run_type', 'status', 'processed_by', 'processed_by_name',
            'processed_at', 'approved_by', 'approved_by_name', 'approved_at',
            'total_employees', 'total_gross_pay', 'total_deductions', 'total_net_pay',
            'total_taxes', 'notes', 'error_log', 'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']


class PayrollItemSerializer(serializers.ModelSerializer):
    """Serializer for PayrollItem."""
    payroll_employee_name = serializers.CharField(source='payroll.employee.full_name', read_only=True)
    component_name = serializers.CharField(source='component.name', read_only=True)
    component_type = serializers.CharField(source='component.component_type', read_only=True)
    
    class Meta:
        model = PayrollItem
        fields = [
            'id', 'payroll', 'payroll_run', 'component', 'component_name', 'component_type',
            'item_type', 'quantity', 'rate', 'amount', 'is_taxable', 'is_pretax',
            'description', 'reference', 'payroll_employee_name', 'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']


class PayrollAdjustmentSerializer(serializers.ModelSerializer):
    """Serializer for PayrollAdjustment."""
    payroll_employee_name = serializers.CharField(source='payroll.employee.full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = PayrollAdjustment
        fields = [
            'id', 'payroll', 'payroll_run', 'adjustment_type', 'amount', 'is_positive',
            'is_taxable', 'is_pretax', 'approved_by', 'approved_by_name', 'approved_at',
            'reason', 'reference_document', 'payroll_employee_name', 'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']


# ==================== TAX AND COMPLIANCE SERIALIZERS ====================

class TaxYearSerializer(serializers.ModelSerializer):
    """Serializer for TaxYear."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = TaxYear
        fields = [
            'id', 'organization', 'organization_name', 'year', 'federal_tax_rate',
            'state_tax_rate', 'local_tax_rate', 'social_security_rate', 'social_security_wage_base',
            'medicare_rate', 'medicare_additional_rate', 'medicare_additional_threshold',
            'standard_deduction_single', 'standard_deduction_married', 'is_active',
            'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']


class EmployeeTaxInfoSerializer(serializers.ModelSerializer):
    """Serializer for EmployeeTaxInfo."""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    tax_year_year = serializers.IntegerField(source='tax_year.year', read_only=True)
    
    class Meta:
        model = EmployeeTaxInfo
        fields = [
            'id', 'employee', 'employee_name', 'tax_year', 'tax_year_year', 'filing_status',
            'federal_exemptions', 'state_exemptions', 'additional_federal_withholding',
            'additional_state_withholding', 'w4_form_date', 'state_tax_form_date',
            'ytd_gross_wages', 'ytd_federal_tax', 'ytd_state_tax', 'ytd_social_security',
            'ytd_medicare', 'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']


# ==================== PAYROLL REPORTS AND ANALYTICS SERIALIZERS ====================

class PayrollReportSerializer(serializers.ModelSerializer):
    """Serializer for PayrollReport."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)
    
    class Meta:
        model = PayrollReport
        fields = [
            'id', 'organization', 'organization_name', 'report_name', 'report_type',
            'start_date', 'end_date', 'departments', 'employees', 'payroll_periods',
            'report_data', 'totals', 'status', 'generated_by', 'generated_by_name',
            'generated_at', 'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']


class PayrollAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for PayrollAnalytics."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = PayrollAnalytics
        fields = [
            'id', 'organization', 'organization_name', 'period_start', 'period_end',
            'period_type', 'total_employees', 'total_gross_pay', 'total_net_pay',
            'total_taxes', 'total_benefits', 'total_overtime', 'average_gross_pay',
            'average_net_pay', 'average_hours_worked', 'gross_pay_trend',
            'employee_count_trend', 'metrics', 'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']


# ==================== PAYROLL INTEGRATION SERIALIZERS ====================

class PayrollIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for PayrollIntegration."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = PayrollIntegration
        fields = [
            'id', 'organization', 'organization_name', 'integration_name', 'integration_type',
            'provider_name', 'provider_url', 'is_active', 'configuration',
            'last_sync', 'sync_status', 'error_message', 'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']
        extra_kwargs = {
            'api_key': {'write_only': True},
            'api_secret': {'write_only': True},
            'access_token': {'write_only': True},
            'refresh_token': {'write_only': True},
        }


class PayrollWebhookSerializer(serializers.ModelSerializer):
    """Serializer for PayrollWebhook."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    integration_name = serializers.CharField(source='integration.integration_name', read_only=True)
    
    class Meta:
        model = PayrollWebhook
        fields = [
            'id', 'organization', 'organization_name', 'integration', 'integration_name',
            'event_type', 'webhook_url', 'is_active', 'total_calls', 'successful_calls',
            'failed_calls', 'last_called', 'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']
        extra_kwargs = {
            'secret_key': {'write_only': True},
        }


# ==================== PAYROLL NOTIFICATIONS SERIALIZERS ====================

class PayrollNotificationSerializer(serializers.ModelSerializer):
    """Serializer for PayrollNotification."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    related_payroll_employee = serializers.CharField(source='related_payroll.employee.full_name', read_only=True)
    
    class Meta:
        model = PayrollNotification
        fields = [
            'id', 'organization', 'organization_name', 'notification_type', 'recipients',
            'subject', 'message', 'delivery_method', 'status', 'scheduled_at', 'sent_at',
            'related_payroll', 'related_payroll_run', 'related_payroll_employee',
            'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']


# ==================== ENHANCED PAYROLL SERIALIZERS ====================

class EnhancedPayrollSerializer(serializers.ModelSerializer):
    """Enhanced serializer for Payroll with detailed information."""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    payroll_period_name = serializers.CharField(source='payroll_period.name', read_only=True)
    payroll_items = PayrollItemSerializer(many=True, read_only=True)
    adjustments = PayrollAdjustmentSerializer(many=True, read_only=True)
    
    # Calculated fields
    total_earnings = serializers.SerializerMethodField()
    total_deductions = serializers.SerializerMethodField()
    total_taxes = serializers.SerializerMethodField()
    net_pay_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Payroll
        fields = [
            'id', 'employee', 'employee_name', 'employee_id', 'payroll_period',
            'payroll_period_name', 'basic_salary', 'hours_worked', 'overtime_hours',
            'overtime_pay', 'allowances', 'bonuses', 'commissions', 'tax_deduction',
            'social_security', 'health_insurance', 'other_deductions', 'gross_pay',
            'total_deductions', 'net_pay', 'status', 'notes', 'payroll_items',
            'adjustments', 'total_earnings', 'total_taxes', 'net_pay_percentage',
            'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']
    
    def get_total_earnings(self, obj):
        """Calculate total earnings from payroll items."""
        earnings_items = obj.items.filter(item_type='earnings')
        return sum(item.amount for item in earnings_items)
    
    def get_total_deductions(self, obj):
        """Calculate total deductions from payroll items."""
        deduction_items = obj.items.filter(item_type='deduction')
        return sum(item.amount for item in deduction_items)
    
    def get_total_taxes(self, obj):
        """Calculate total taxes from payroll items."""
        tax_items = obj.items.filter(item_type='tax')
        return sum(item.amount for item in tax_items)
    
    def get_net_pay_percentage(self, obj):
        """Calculate net pay as percentage of gross pay."""
        if obj.gross_pay > 0:
            return round((obj.net_pay / obj.gross_pay) * 100, 2)
        return 0


class PayrollRunDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for PayrollRun with payrolls."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    payroll_period_name = serializers.CharField(source='payroll_period.name', read_only=True)
    processed_by_name = serializers.CharField(source='processed_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    # Related payrolls
    payrolls = EnhancedPayrollSerializer(many=True, read_only=True)
    payroll_items = PayrollItemSerializer(many=True, read_only=True)
    adjustments = PayrollAdjustmentSerializer(many=True, read_only=True)
    
    # Statistics
    payroll_count = serializers.SerializerMethodField()
    average_gross_pay = serializers.SerializerMethodField()
    average_net_pay = serializers.SerializerMethodField()
    
    class Meta:
        model = PayrollRun
        fields = [
            'id', 'organization', 'organization_name', 'payroll_period', 'payroll_period_name',
            'run_name', 'run_type', 'status', 'processed_by', 'processed_by_name',
            'processed_at', 'approved_by', 'approved_by_name', 'approved_at',
            'total_employees', 'total_gross_pay', 'total_deductions', 'total_net_pay',
            'total_taxes', 'notes', 'error_log', 'payrolls', 'payroll_items', 'adjustments',
            'payroll_count', 'average_gross_pay', 'average_net_pay', 'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']
    
    def get_payroll_count(self, obj):
        """Get count of payrolls in this run."""
        return obj.payrolls.count()
    
    def get_average_gross_pay(self, obj):
        """Calculate average gross pay."""
        if obj.total_employees > 0:
            return round(obj.total_gross_pay / obj.total_employees, 2)
        return 0
    
    def get_average_net_pay(self, obj):
        """Calculate average net pay."""
        if obj.total_employees > 0:
            return round(obj.total_net_pay / obj.total_employees, 2)
        return 0


# ==================== SPECIALIZED SERIALIZERS ====================

class PayrollCalculationSerializer(serializers.Serializer):
    """Serializer for payroll calculations."""
    employee_id = serializers.IntegerField()
    payroll_period_id = serializers.IntegerField()
    hours_worked = serializers.DecimalField(max_digits=5, decimal_places=2, default=0)
    overtime_hours = serializers.DecimalField(max_digits=5, decimal_places=2, default=0)
    allowances = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    bonuses = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    commissions = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    custom_deductions = serializers.JSONField(default=dict)
    
    def validate_employee_id(self, value):
        """Validate employee exists and is active."""
        try:
            employee = Employee.objects.get(id=value, employment_status='active')
        except Employee.DoesNotExist:
            raise serializers.ValidationError('Employee not found or not active.')
        return value
    
    def validate_payroll_period_id(self, value):
        """Validate payroll period exists."""
        try:
            PayrollPeriod.objects.get(id=value)
        except PayrollPeriod.DoesNotExist:
            raise serializers.ValidationError('Payroll period not found.')
        return value


class PayrollProcessingSerializer(serializers.Serializer):
    """Serializer for payroll processing."""
    payroll_run_id = serializers.IntegerField()
    process_type = serializers.ChoiceField(choices=[
        ('calculate', 'Calculate Payroll'),
        ('approve', 'Approve Payroll'),
        ('process', 'Process Payroll'),
        ('pay', 'Pay Employees'),
    ])
    employee_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_payroll_run_id(self, value):
        """Validate payroll run exists."""
        try:
            PayrollRun.objects.get(id=value)
        except PayrollRun.DoesNotExist:
            raise serializers.ValidationError('Payroll run not found.')
        return value


class PayrollReportRequestSerializer(serializers.Serializer):
    """Serializer for payroll report requests."""
    report_type = serializers.ChoiceField(choices=[
        ('summary', 'Payroll Summary'),
        ('detailed', 'Detailed Payroll'),
        ('tax_summary', 'Tax Summary'),
        ('benefits_summary', 'Benefits Summary'),
        ('overtime_report', 'Overtime Report'),
        ('attendance_report', 'Attendance Report'),
    ])
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    departments = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    employees = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    payroll_periods = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    include_inactive = serializers.BooleanField(default=False)
    format = serializers.ChoiceField(choices=[
        ('json', 'JSON'),
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
    ], default='json')
    
    def validate(self, data):
        """Validate date range."""
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError('Start date must be before end date.')
        return data


class PayrollAnalyticsRequestSerializer(serializers.Serializer):
    """Serializer for payroll analytics requests."""
    period_type = serializers.ChoiceField(choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ])
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    departments = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    include_trends = serializers.BooleanField(default=True)
    include_forecasts = serializers.BooleanField(default=False)
    
    def validate(self, data):
        """Validate date range."""
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError('Start date must be before end date.')
        return data
