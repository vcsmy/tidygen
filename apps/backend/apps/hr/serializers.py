"""
HR management serializers for iNEAT ERP platform.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.hr.models import (
    Department, Position, Employee, Attendance, LeaveType, LeaveRequest,
    PayrollPeriod, Payroll, PerformanceReview, Training, TrainingEnrollment,
    Document, Policy, PolicyAcknowledgment
)

User = get_user_model()


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model."""
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)
    parent_department_name = serializers.CharField(source='parent_department.name', read_only=True)
    employee_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id', 'name', 'code', 'description', 'parent_department', 'parent_department_name',
            'manager', 'manager_name', 'budget', 'cost_center', 'is_active',
            'employee_count', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']
    
    def get_employee_count(self, obj):
        return obj.employees.count()


class PositionSerializer(serializers.ModelSerializer):
    """Serializer for Position model."""
    job_level_display = serializers.CharField(source='get_job_level_display', read_only=True)
    employment_type_display = serializers.CharField(source='get_employment_type_display', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    reports_to_title = serializers.CharField(source='reports_to.title', read_only=True)
    employee_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Position
        fields = [
            'id', 'title', 'code', 'description', 'department', 'department_name',
            'reports_to', 'reports_to_title', 'job_level', 'job_level_display',
            'employment_type', 'employment_type_display', 'min_salary', 'max_salary',
            'currency', 'required_skills', 'required_education', 'required_experience',
            'is_active', 'is_remote', 'employee_count', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']
    
    def get_employee_count(self, obj):
        return obj.employees.count()


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for Employee model."""
    # User fields
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    full_name = serializers.ReadOnlyField()
    
    # Related fields
    position_title = serializers.CharField(source='position.title', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    manager_name = serializers.CharField(source='manager.full_name', read_only=True)
    
    # Choice field displays
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    marital_status_display = serializers.CharField(source='get_marital_status_display', read_only=True)
    employment_status_display = serializers.CharField(source='get_employment_status_display', read_only=True)
    work_schedule_display = serializers.CharField(source='get_work_schedule_display', read_only=True)
    
    # Computed fields
    is_on_probation = serializers.ReadOnlyField()
    years_of_service = serializers.SerializerMethodField()
    current_leave_balance = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'employee_id', 'badge_number', 'date_of_birth', 'gender', 'gender_display',
            'marital_status', 'marital_status_display', 'nationality', 'personal_email',
            'personal_phone', 'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship', 'address_line1', 'address_line2', 'city',
            'state', 'postal_code', 'country', 'position', 'position_title', 'department',
            'department_name', 'manager', 'manager_name', 'hire_date', 'probation_end_date',
            'termination_date', 'employment_status', 'employment_status_display',
            'work_location', 'is_remote', 'work_schedule', 'work_schedule_display',
            'salary', 'hourly_rate', 'currency', 'benefits_eligible', 'health_insurance',
            'dental_insurance', 'vision_insurance', 'retirement_plan', 'skills',
            'certifications', 'notes', 'is_on_probation', 'years_of_service',
            'current_leave_balance', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']
    
    def get_years_of_service(self, obj):
        from django.utils import timezone
        if obj.hire_date:
            today = timezone.now().date()
            years = (today - obj.hire_date).days / 365.25
            return round(years, 1)
        return 0
    
    def get_current_leave_balance(self, obj):
        # This would need to be calculated based on leave types and usage
        # For now, returning a placeholder
        return 0


class AttendanceSerializer(serializers.ModelSerializer):
    """Serializer for Attendance model."""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'employee', 'employee_name', 'date', 'check_in_time', 'check_out_time',
            'break_start_time', 'break_end_time', 'total_hours', 'overtime_hours',
            'status', 'status_display', 'notes', 'approved_by', 'approved_by_name',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class LeaveTypeSerializer(serializers.ModelSerializer):
    """Serializer for LeaveType model."""
    class Meta:
        model = LeaveType
        fields = [
            'id', 'name', 'code', 'description', 'max_days_per_year', 'is_paid',
            'requires_approval', 'advance_notice_days', 'can_carryover',
            'max_carryover_days', 'accrues_monthly', 'accrual_rate', 'is_active',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class LeaveRequestSerializer(serializers.ModelSerializer):
    """Serializer for LeaveRequest model."""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'employee', 'employee_name', 'leave_type', 'leave_type_name',
            'start_date', 'end_date', 'total_days', 'reason', 'status', 'status_display',
            'requested_by', 'requested_by_name', 'approved_by', 'approved_by_name',
            'approved_at', 'rejection_reason', 'notes', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified', 'approved_by', 'approved_at']


class PayrollPeriodSerializer(serializers.ModelSerializer):
    """Serializer for PayrollPeriod model."""
    period_type_display = serializers.CharField(source='get_period_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    processed_by_name = serializers.CharField(source='processed_by.get_full_name', read_only=True)
    payroll_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PayrollPeriod
        fields = [
            'id', 'name', 'start_date', 'end_date', 'period_type', 'period_type_display',
            'status', 'status_display', 'pay_date', 'processed_at', 'processed_by',
            'processed_by_name', 'payroll_count', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified', 'processed_at', 'processed_by']
    
    def get_payroll_count(self, obj):
        return obj.payrolls.count()


class PayrollSerializer(serializers.ModelSerializer):
    """Serializer for Payroll model."""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    payroll_period_name = serializers.CharField(source='payroll_period.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Payroll
        fields = [
            'id', 'employee', 'employee_name', 'payroll_period', 'payroll_period_name',
            'basic_salary', 'hours_worked', 'overtime_hours', 'overtime_pay',
            'allowances', 'bonuses', 'commissions', 'tax_deduction', 'social_security',
            'health_insurance', 'other_deductions', 'gross_pay', 'total_deductions',
            'net_pay', 'status', 'status_display', 'notes', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class PerformanceReviewSerializer(serializers.ModelSerializer):
    """Serializer for PerformanceReview model."""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    reviewer_name = serializers.CharField(source='reviewer.get_full_name', read_only=True)
    review_type_display = serializers.CharField(source='get_review_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = PerformanceReview
        fields = [
            'id', 'employee', 'employee_name', 'reviewer', 'reviewer_name',
            'review_period_start', 'review_period_end', 'review_date', 'review_type',
            'review_type_display', 'overall_rating', 'quality_rating', 'productivity_rating',
            'teamwork_rating', 'communication_rating', 'strengths', 'areas_for_improvement',
            'goals_achieved', 'goals_for_next_period', 'comments', 'status', 'status_display',
            'employee_acknowledged', 'acknowledged_at', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified', 'acknowledged_at']


class TrainingSerializer(serializers.ModelSerializer):
    """Serializer for Training model."""
    training_type_display = serializers.CharField(source='get_training_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    enrollment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Training
        fields = [
            'id', 'title', 'description', 'training_type', 'training_type_display',
            'start_date', 'end_date', 'duration_hours', 'location', 'is_online',
            'instructor', 'cost_per_participant', 'total_budget', 'prerequisites',
            'max_participants', 'status', 'status_display', 'enrollment_count',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']
    
    def get_enrollment_count(self, obj):
        return obj.enrollments.count()


class TrainingEnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for TrainingEnrollment model."""
    training_title = serializers.CharField(source='training.title', read_only=True)
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    enrolled_by_name = serializers.CharField(source='enrolled_by.get_full_name', read_only=True)
    
    class Meta:
        model = TrainingEnrollment
        fields = [
            'id', 'training', 'training_title', 'employee', 'employee_name',
            'enrolled_at', 'enrolled_by', 'enrolled_by_name', 'status', 'status_display',
            'completion_date', 'score', 'certificate_issued', 'feedback', 'rating',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified', 'enrolled_at']


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for Document model."""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.get_full_name', read_only=True)
    file_url = serializers.SerializerMethodField()
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'employee', 'employee_name', 'document_type', 'document_type_display',
            'title', 'description', 'file', 'file_url', 'file_size', 'file_size_mb',
            'issue_date', 'expiry_date', 'is_verified', 'verified_by', 'verified_by_name',
            'verified_at', 'is_public', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified', 'file_size', 'verified_at']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None
    
    def get_file_size_mb(self, obj):
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return None


class PolicySerializer(serializers.ModelSerializer):
    """Serializer for Policy model."""
    policy_type_display = serializers.CharField(source='get_policy_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    acknowledgment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Policy
        fields = [
            'id', 'title', 'policy_type', 'policy_type_display', 'content', 'summary',
            'version', 'effective_date', 'expiry_date', 'approved_by', 'approved_by_name',
            'approved_at', 'status', 'status_display', 'requires_acknowledgment',
            'acknowledgment_count', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified', 'approved_at']
    
    def get_acknowledgment_count(self, obj):
        return obj.acknowledgments.count()


class PolicyAcknowledgmentSerializer(serializers.ModelSerializer):
    """Serializer for PolicyAcknowledgment model."""
    policy_title = serializers.CharField(source='policy.title', read_only=True)
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    
    class Meta:
        model = PolicyAcknowledgment
        fields = [
            'id', 'policy', 'policy_title', 'employee', 'employee_name',
            'acknowledged_at', 'ip_address', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified', 'acknowledged_at']


# Dashboard and Analytics Serializers
class HRDashboardSerializer(serializers.Serializer):
    """Serializer for HR dashboard data."""
    total_employees = serializers.IntegerField()
    active_employees = serializers.IntegerField()
    new_employees_this_month = serializers.IntegerField()
    employees_on_leave = serializers.IntegerField()
    employees_on_probation = serializers.IntegerField()
    total_departments = serializers.IntegerField()
    total_positions = serializers.IntegerField()
    employees_by_department = serializers.ListField(child=serializers.DictField())
    employees_by_status = serializers.ListField(child=serializers.DictField())
    recent_employees = serializers.ListField(child=serializers.DictField())
    upcoming_birthdays = serializers.ListField(child=serializers.DictField())
    pending_leave_requests = serializers.ListField(child=serializers.DictField())
    attendance_summary = serializers.DictField()


class HRAnalyticsSerializer(serializers.Serializer):
    """Serializer for HR analytics."""
    total_employees = serializers.IntegerField()
    employee_growth_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    average_tenure = serializers.DecimalField(max_digits=5, decimal_places=2)
    turnover_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    gender_distribution = serializers.ListField(child=serializers.DictField())
    age_distribution = serializers.ListField(child=serializers.DictField())
    department_distribution = serializers.ListField(child=serializers.DictField())
    position_distribution = serializers.ListField(child=serializers.DictField())
    salary_distribution = serializers.ListField(child=serializers.DictField())
    performance_trends = serializers.ListField(child=serializers.DictField())


class AttendanceAnalyticsSerializer(serializers.Serializer):
    """Serializer for attendance analytics."""
    total_attendance_records = serializers.IntegerField()
    average_attendance_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    attendance_by_status = serializers.ListField(child=serializers.DictField())
    attendance_trends = serializers.ListField(child=serializers.DictField())
    late_arrivals = serializers.IntegerField()
    early_departures = serializers.IntegerField()
    overtime_hours = serializers.DecimalField(max_digits=10, decimal_places=2)
    attendance_by_department = serializers.ListField(child=serializers.DictField())


class PayrollAnalyticsSerializer(serializers.Serializer):
    """Serializer for payroll analytics."""
    total_payroll_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    payroll_by_department = serializers.ListField(child=serializers.DictField())
    salary_distribution = serializers.ListField(child=serializers.DictField())
    overtime_costs = serializers.DecimalField(max_digits=12, decimal_places=2)
    benefits_costs = serializers.DecimalField(max_digits=12, decimal_places=2)
    tax_deductions = serializers.DecimalField(max_digits=12, decimal_places=2)
    payroll_trends = serializers.ListField(child=serializers.DictField())


class LeaveAnalyticsSerializer(serializers.Serializer):
    """Serializer for leave analytics."""
    total_leave_requests = serializers.IntegerField()
    approved_leave_requests = serializers.IntegerField()
    pending_leave_requests = serializers.IntegerField()
    rejected_leave_requests = serializers.IntegerField()
    leave_by_type = serializers.ListField(child=serializers.DictField())
    leave_by_department = serializers.ListField(child=serializers.DictField())
    average_leave_duration = serializers.DecimalField(max_digits=5, decimal_places=2)
    leave_trends = serializers.ListField(child=serializers.DictField())
    upcoming_leaves = serializers.ListField(child=serializers.DictField())


class PerformanceAnalyticsSerializer(serializers.Serializer):
    """Serializer for performance analytics."""
    total_reviews = serializers.IntegerField()
    average_overall_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    performance_by_rating = serializers.ListField(child=serializers.DictField())
    performance_by_department = serializers.ListField(child=serializers.DictField())
    top_performers = serializers.ListField(child=serializers.DictField())
    improvement_areas = serializers.ListField(child=serializers.DictField())
    review_completion_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    performance_trends = serializers.ListField(child=serializers.DictField())


class TrainingAnalyticsSerializer(serializers.Serializer):
    """Serializer for training analytics."""
    total_trainings = serializers.IntegerField()
    total_enrollments = serializers.IntegerField()
    completed_trainings = serializers.IntegerField()
    average_completion_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    training_by_type = serializers.ListField(child=serializers.DictField())
    training_by_department = serializers.ListField(child=serializers.DictField())
    top_training_programs = serializers.ListField(child=serializers.DictField())
    training_costs = serializers.DecimalField(max_digits=12, decimal_places=2)
    training_trends = serializers.ListField(child=serializers.DictField())
