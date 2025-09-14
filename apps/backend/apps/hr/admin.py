"""
Django admin configuration for HR management models.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from apps.hr.models import (
    Department, Position, Employee, Attendance, LeaveType, LeaveRequest,
    PayrollPeriod, Payroll, PerformanceReview, Training, TrainingEnrollment,
    Document, Policy, PolicyAcknowledgment
)


class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0
    fields = ['date', 'check_in_time', 'check_out_time', 'total_hours', 'status']
    readonly_fields = ['created']


class LeaveRequestInline(admin.TabularInline):
    model = LeaveRequest
    extra = 0
    fields = ['leave_type', 'start_date', 'end_date', 'total_days', 'status']
    readonly_fields = ['created']


class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0
    fields = ['document_type', 'title', 'file', 'is_verified', 'expiry_date']
    readonly_fields = ['created']


class PerformanceReviewInline(admin.TabularInline):
    model = PerformanceReview
    extra = 0
    fields = ['review_type', 'review_date', 'overall_rating', 'status']
    readonly_fields = ['created']


class TrainingEnrollmentInline(admin.TabularInline):
    model = TrainingEnrollment
    extra = 0
    fields = ['training', 'status', 'completion_date', 'score']
    readonly_fields = ['enrolled_at']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'manager_name', 'is_active', 'employee_count', 'created']
    list_filter = ['is_active', 'created']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description', 'is_active')
        }),
        ('Hierarchy', {
            'fields': ('parent_department', 'manager')
        }),
        ('Financial', {
            'fields': ('budget', 'cost_center'),
            'classes': ('collapse',)
        }),
    )
    
    def manager_name(self, obj):
        return obj.manager.get_full_name() if obj.manager else '-'
    manager_name.short_description = 'Manager'
    
    def employee_count(self, obj):
        return obj.employees.count()
    employee_count.short_description = 'Employees'


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'job_level', 'employment_type', 'is_active', 'employee_count', 'created']
    list_filter = ['job_level', 'employment_type', 'is_active', 'is_remote', 'created']
    search_fields = ['title', 'code', 'description']
    ordering = ['title']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'code', 'description', 'is_active', 'is_remote')
        }),
        ('Organization', {
            'fields': ('department', 'reports_to')
        }),
        ('Job Details', {
            'fields': ('job_level', 'employment_type')
        }),
        ('Compensation', {
            'fields': ('min_salary', 'max_salary', 'currency')
        }),
        ('Requirements', {
            'fields': ('required_skills', 'required_education', 'required_experience'),
            'classes': ('collapse',)
        }),
    )
    
    def employee_count(self, obj):
        return obj.employees.count()
    employee_count.short_description = 'Employees'


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'employee_id', 'department', 'position', 'employment_status',
        'hire_date', 'is_on_probation', 'salary', 'created'
    ]
    list_filter = [
        'employment_status', 'gender', 'marital_status', 'work_schedule',
        'is_remote', 'benefits_eligible', 'department', 'position', 'created'
    ]
    search_fields = [
        'user__first_name', 'user__last_name', 'user__email', 'employee_id',
        'badge_number', 'personal_email'
    ]
    ordering = ['user__last_name', 'user__first_name']
    list_editable = ['employment_status']
    inlines = [AttendanceInline, LeaveRequestInline, DocumentInline, PerformanceReviewInline, TrainingEnrollmentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'employee_id', 'badge_number', 'organization')
        }),
        ('Personal Information', {
            'fields': ('date_of_birth', 'gender', 'marital_status', 'nationality')
        }),
        ('Contact Information', {
            'fields': ('personal_email', 'personal_phone', 'emergency_contact_name',
                      'emergency_contact_phone', 'emergency_contact_relationship')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Employment', {
            'fields': ('position', 'department', 'manager', 'hire_date', 'probation_end_date',
                      'termination_date', 'employment_status')
        }),
        ('Work Arrangement', {
            'fields': ('work_location', 'is_remote', 'work_schedule')
        }),
        ('Compensation', {
            'fields': ('salary', 'hourly_rate', 'currency')
        }),
        ('Benefits', {
            'fields': ('benefits_eligible', 'health_insurance', 'dental_insurance',
                      'vision_insurance', 'retirement_plan')
        }),
        ('Additional Information', {
            'fields': ('skills', 'certifications', 'notes'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created']
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Full Name'
    
    def is_on_probation(self, obj):
        return obj.is_on_probation
    is_on_probation.short_description = 'On Probation'
    is_on_probation.boolean = True


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = [
        'employee_name', 'date', 'check_in_time', 'check_out_time',
        'total_hours', 'status', 'approved_by_name', 'created'
    ]
    list_filter = ['status', 'date', 'approved_by', 'created']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'notes']
    ordering = ['-date']
    list_editable = ['status']
    
    fieldsets = (
        ('Attendance Information', {
            'fields': ('employee', 'date', 'status')
        }),
        ('Time Tracking', {
            'fields': ('check_in_time', 'check_out_time', 'break_start_time', 'break_end_time')
        }),
        ('Calculated Fields', {
            'fields': ('total_hours', 'overtime_hours')
        }),
        ('Approval', {
            'fields': ('approved_by', 'notes')
        }),
    )
    
    readonly_fields = ['created']
    
    def employee_name(self, obj):
        return obj.employee.full_name
    employee_name.short_description = 'Employee'
    
    def approved_by_name(self, obj):
        return obj.approved_by.get_full_name() if obj.approved_by else '-'
    approved_by_name.short_description = 'Approved By'


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'code', 'max_days_per_year', 'is_paid', 'requires_approval',
        'can_carryover', 'is_active', 'created'
    ]
    list_filter = ['is_paid', 'requires_approval', 'can_carryover', 'accrues_monthly', 'is_active', 'created']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description', 'is_active')
        }),
        ('Leave Configuration', {
            'fields': ('max_days_per_year', 'is_paid', 'requires_approval', 'advance_notice_days')
        }),
        ('Carryover and Accrual', {
            'fields': ('can_carryover', 'max_carryover_days', 'accrues_monthly', 'accrual_rate')
        }),
    )


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = [
        'employee_name', 'leave_type', 'start_date', 'end_date', 'total_days',
        'status', 'requested_by_name', 'approved_by_name', 'created'
    ]
    list_filter = ['status', 'leave_type', 'start_date', 'end_date', 'requested_by', 'approved_by', 'created']
    search_fields = [
        'employee__user__first_name', 'employee__user__last_name', 'reason'
    ]
    ordering = ['-created']
    list_editable = ['status']
    
    fieldsets = (
        ('Leave Information', {
            'fields': ('employee', 'leave_type', 'start_date', 'end_date', 'total_days', 'reason')
        }),
        ('Status and Approval', {
            'fields': ('status', 'requested_by', 'approved_by', 'approved_at', 'rejection_reason')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
    )
    
    readonly_fields = ['created', 'approved_at']
    
    def employee_name(self, obj):
        return obj.employee.full_name
    employee_name.short_description = 'Employee'
    
    def requested_by_name(self, obj):
        return obj.requested_by.get_full_name()
    requested_by_name.short_description = 'Requested By'
    
    def approved_by_name(self, obj):
        return obj.approved_by.get_full_name() if obj.approved_by else '-'
    approved_by_name.short_description = 'Approved By'


@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'start_date', 'end_date', 'period_type', 'status',
        'pay_date', 'processed_by_name', 'payroll_count', 'created'
    ]
    list_filter = ['period_type', 'status', 'start_date', 'end_date', 'processed_by', 'created']
    search_fields = ['name']
    ordering = ['-start_date']
    list_editable = ['status']
    
    fieldsets = (
        ('Period Information', {
            'fields': ('name', 'start_date', 'end_date', 'period_type', 'status')
        }),
        ('Processing', {
            'fields': ('pay_date', 'processed_by', 'processed_at')
        }),
    )
    
    readonly_fields = ['created', 'processed_at']
    
    def processed_by_name(self, obj):
        return obj.processed_by.get_full_name() if obj.processed_by else '-'
    processed_by_name.short_description = 'Processed By'
    
    def payroll_count(self, obj):
        return obj.payrolls.count()
    payroll_count.short_description = 'Payrolls'


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = [
        'employee_name', 'payroll_period', 'basic_salary', 'gross_pay',
        'total_deductions', 'net_pay', 'status', 'created'
    ]
    list_filter = ['status', 'payroll_period', 'created']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'notes']
    ordering = ['-payroll_period__start_date']
    list_editable = ['status']
    
    fieldsets = (
        ('Payroll Information', {
            'fields': ('employee', 'payroll_period', 'status')
        }),
        ('Basic Pay', {
            'fields': ('basic_salary', 'hours_worked', 'overtime_hours', 'overtime_pay')
        }),
        ('Allowances', {
            'fields': ('allowances', 'bonuses', 'commissions')
        }),
        ('Deductions', {
            'fields': ('tax_deduction', 'social_security', 'health_insurance', 'other_deductions')
        }),
        ('Totals', {
            'fields': ('gross_pay', 'total_deductions', 'net_pay')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
    )
    
    readonly_fields = ['created']
    
    def employee_name(self, obj):
        return obj.employee.full_name
    employee_name.short_description = 'Employee'


@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = [
        'employee_name', 'reviewer_name', 'review_type', 'review_date',
        'overall_rating', 'status', 'employee_acknowledged', 'created'
    ]
    list_filter = [
        'review_type', 'status', 'employee_acknowledged', 'review_date', 'created'
    ]
    search_fields = [
        'employee__user__first_name', 'employee__user__last_name',
        'reviewer__first_name', 'reviewer__last_name', 'strengths', 'areas_for_improvement'
    ]
    ordering = ['-review_date']
    list_editable = ['status']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('employee', 'reviewer', 'review_type', 'review_date', 'status')
        }),
        ('Review Period', {
            'fields': ('review_period_start', 'review_period_end')
        }),
        ('Ratings', {
            'fields': ('overall_rating', 'quality_rating', 'productivity_rating',
                      'teamwork_rating', 'communication_rating')
        }),
        ('Review Content', {
            'fields': ('strengths', 'areas_for_improvement', 'goals_achieved',
                      'goals_for_next_period', 'comments')
        }),
        ('Acknowledgment', {
            'fields': ('employee_acknowledged', 'acknowledged_at')
        }),
    )
    
    readonly_fields = ['created', 'acknowledged_at']
    
    def employee_name(self, obj):
        return obj.employee.full_name
    employee_name.short_description = 'Employee'
    
    def reviewer_name(self, obj):
        return obj.reviewer.get_full_name()
    reviewer_name.short_description = 'Reviewer'


@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'training_type', 'start_date', 'end_date', 'duration_hours',
        'location', 'instructor', 'status', 'enrollment_count', 'created'
    ]
    list_filter = ['training_type', 'status', 'is_online', 'start_date', 'end_date', 'created']
    search_fields = ['title', 'description', 'instructor', 'location']
    ordering = ['-start_date']
    list_editable = ['status']
    
    fieldsets = (
        ('Training Information', {
            'fields': ('title', 'description', 'training_type', 'status')
        }),
        ('Scheduling', {
            'fields': ('start_date', 'end_date', 'duration_hours')
        }),
        ('Location and Delivery', {
            'fields': ('location', 'is_online', 'instructor')
        }),
        ('Cost and Budget', {
            'fields': ('cost_per_participant', 'total_budget')
        }),
        ('Requirements', {
            'fields': ('prerequisites', 'max_participants'),
            'classes': ('collapse',)
        }),
    )
    
    def enrollment_count(self, obj):
        return obj.enrollments.count()
    enrollment_count.short_description = 'Enrollments'


@admin.register(TrainingEnrollment)
class TrainingEnrollmentAdmin(admin.ModelAdmin):
    list_display = [
        'employee_name', 'training_title', 'status', 'enrolled_at',
        'completion_date', 'score', 'certificate_issued', 'created'
    ]
    list_filter = ['status', 'certificate_issued', 'enrolled_at', 'completion_date', 'created']
    search_fields = [
        'employee__user__first_name', 'employee__user__last_name',
        'training__title', 'feedback'
    ]
    ordering = ['-enrolled_at']
    list_editable = ['status']
    
    fieldsets = (
        ('Enrollment Information', {
            'fields': ('training', 'employee', 'status', 'enrolled_by')
        }),
        ('Completion', {
            'fields': ('completion_date', 'score', 'certificate_issued')
        }),
        ('Feedback', {
            'fields': ('feedback', 'rating')
        }),
    )
    
    readonly_fields = ['created', 'enrolled_at']
    
    def employee_name(self, obj):
        return obj.employee.full_name
    employee_name.short_description = 'Employee'
    
    def training_title(self, obj):
        return obj.training.title
    training_title.short_description = 'Training'


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        'employee_name', 'document_type', 'title', 'file_size_mb',
        'is_verified', 'verified_by_name', 'expiry_date', 'created'
    ]
    list_filter = ['document_type', 'is_verified', 'is_public', 'verified_by', 'created']
    search_fields = [
        'employee__user__first_name', 'employee__user__last_name',
        'title', 'description'
    ]
    ordering = ['-created']
    list_editable = ['is_verified']
    
    fieldsets = (
        ('Document Information', {
            'fields': ('employee', 'document_type', 'title', 'description')
        }),
        ('File Information', {
            'fields': ('file', 'file_size', 'is_public')
        }),
        ('Dates', {
            'fields': ('issue_date', 'expiry_date')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verified_by', 'verified_at')
        }),
    )
    
    readonly_fields = ['created', 'file_size', 'verified_at']
    
    def employee_name(self, obj):
        return obj.employee.full_name
    employee_name.short_description = 'Employee'
    
    def verified_by_name(self, obj):
        return obj.verified_by.get_full_name() if obj.verified_by else '-'
    verified_by_name.short_description = 'Verified By'
    
    def file_size_mb(self, obj):
        if obj.file_size:
            return f"{round(obj.file_size / (1024 * 1024), 2)} MB"
        return "Unknown"
    file_size_mb.short_description = 'File Size'


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'policy_type', 'version', 'status', 'effective_date',
        'approved_by_name', 'acknowledgment_count', 'created'
    ]
    list_filter = ['policy_type', 'status', 'requires_acknowledgment', 'effective_date', 'created']
    search_fields = ['title', 'content', 'summary']
    ordering = ['-effective_date']
    list_editable = ['status']
    
    fieldsets = (
        ('Policy Information', {
            'fields': ('title', 'policy_type', 'content', 'summary', 'status')
        }),
        ('Version Control', {
            'fields': ('version', 'effective_date', 'expiry_date')
        }),
        ('Approval', {
            'fields': ('approved_by', 'approved_at', 'requires_acknowledgment')
        }),
    )
    
    readonly_fields = ['created', 'approved_at']
    
    def approved_by_name(self, obj):
        return obj.approved_by.get_full_name() if obj.approved_by else '-'
    approved_by_name.short_description = 'Approved By'
    
    def acknowledgment_count(self, obj):
        return obj.acknowledgments.count()
    acknowledgment_count.short_description = 'Acknowledgments'


@admin.register(PolicyAcknowledgment)
class PolicyAcknowledgmentAdmin(admin.ModelAdmin):
    list_display = [
        'employee_name', 'policy_title', 'acknowledged_at', 'ip_address', 'created'
    ]
    list_filter = ['acknowledged_at', 'created']
    search_fields = [
        'employee__user__first_name', 'employee__user__last_name',
        'policy__title'
    ]
    ordering = ['-acknowledged_at']
    
    fieldsets = (
        ('Acknowledgment Information', {
            'fields': ('policy', 'employee', 'acknowledged_at', 'ip_address')
        }),
    )
    
    readonly_fields = ['created', 'acknowledged_at']
    
    def employee_name(self, obj):
        return obj.employee.full_name
    employee_name.short_description = 'Employee'
    
    def policy_title(self, obj):
        return obj.policy.title
    policy_title.short_description = 'Policy'


# Customize admin site
admin.site.site_header = "TidyGen ERP HR Management"
admin.site.site_title = "TidyGen HR Admin"
admin.site.index_title = "HR Management Administration"
