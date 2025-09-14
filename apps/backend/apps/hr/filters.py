"""
HR management filters for TidyGen ERP platform.
"""
import django_filters
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from apps.hr.models import (
    Department, Position, Employee, Attendance, LeaveType, LeaveRequest,
    PayrollPeriod, Payroll, PerformanceReview, Training, TrainingEnrollment,
    Document, Policy, PolicyAcknowledgment
)


class DepartmentFilter(django_filters.FilterSet):
    """Filter for Department model."""
    name = django_filters.CharFilter(lookup_expr='icontains')
    code = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    
    # Manager filter
    manager = django_filters.ModelChoiceFilter(queryset=Department._meta.get_field('manager').related_model.objects.all())
    
    # Parent department filter
    parent_department = django_filters.ModelChoiceFilter(queryset=Department.objects.all())
    
    # Budget filters
    budget_min = django_filters.NumberFilter(field_name='budget', lookup_expr='gte')
    budget_max = django_filters.NumberFilter(field_name='budget', lookup_expr='lte')
    
    # Cost center filter
    cost_center = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Department
        fields = ['name', 'code', 'is_active', 'manager', 'parent_department', 'cost_center']


class PositionFilter(django_filters.FilterSet):
    """Filter for Position model."""
    title = django_filters.CharFilter(lookup_expr='icontains')
    code = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    job_level = django_filters.ChoiceFilter(choices=Position._meta.get_field('job_level').choices)
    employment_type = django_filters.ChoiceFilter(choices=Position._meta.get_field('employment_type').choices)
    is_active = django_filters.BooleanFilter()
    is_remote = django_filters.BooleanFilter()
    
    # Department filter
    department = django_filters.ModelChoiceFilter(queryset=Department.objects.all())
    
    # Reports to filter
    reports_to = django_filters.ModelChoiceFilter(queryset=Position.objects.all())
    
    # Salary filters
    min_salary_min = django_filters.NumberFilter(field_name='min_salary', lookup_expr='gte')
    min_salary_max = django_filters.NumberFilter(field_name='min_salary', lookup_expr='lte')
    max_salary_min = django_filters.NumberFilter(field_name='max_salary', lookup_expr='gte')
    max_salary_max = django_filters.NumberFilter(field_name='max_salary', lookup_expr='lte')
    
    # Experience filter
    required_experience_min = django_filters.NumberFilter(field_name='required_experience', lookup_expr='gte')
    required_experience_max = django_filters.NumberFilter(field_name='required_experience', lookup_expr='lte')
    
    # Currency filter
    currency = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Position
        fields = ['title', 'code', 'job_level', 'employment_type', 'is_active', 'is_remote', 'department', 'currency']


class EmployeeFilter(django_filters.FilterSet):
    """Filter for Employee model."""
    # Basic filters
    employee_id = django_filters.CharFilter(lookup_expr='icontains')
    badge_number = django_filters.CharFilter(lookup_expr='icontains')
    gender = django_filters.ChoiceFilter(choices=Employee._meta.get_field('gender').choices)
    marital_status = django_filters.ChoiceFilter(choices=Employee._meta.get_field('marital_status').choices)
    employment_status = django_filters.ChoiceFilter(choices=Employee._meta.get_field('employment_status').choices)
    work_schedule = django_filters.ChoiceFilter(choices=Employee._meta.get_field('work_schedule').choices)
    
    # Contact filters
    personal_email = django_filters.CharFilter(lookup_expr='icontains')
    personal_phone = django_filters.CharFilter(lookup_expr='icontains')
    
    # Address filters
    city = django_filters.CharFilter(lookup_expr='icontains')
    state = django_filters.CharFilter(lookup_expr='icontains')
    country = django_filters.CharFilter(lookup_expr='icontains')
    
    # Employment filters
    position = django_filters.ModelChoiceFilter(queryset=Position.objects.all())
    department = django_filters.ModelChoiceFilter(queryset=Department.objects.all())
    manager = django_filters.ModelChoiceFilter(queryset=Employee.objects.all())
    
    # Date filters
    hire_date_after = django_filters.DateFilter(field_name='hire_date', lookup_expr='gte')
    hire_date_before = django_filters.DateFilter(field_name='hire_date', lookup_expr='lte')
    probation_end_date_after = django_filters.DateFilter(field_name='probation_end_date', lookup_expr='gte')
    probation_end_date_before = django_filters.DateFilter(field_name='probation_end_date', lookup_expr='lte')
    termination_date_after = django_filters.DateFilter(field_name='termination_date', lookup_expr='gte')
    termination_date_before = django_filters.DateFilter(field_name='termination_date', lookup_expr='lte')
    
    # Work arrangement filters
    work_location = django_filters.CharFilter(lookup_expr='icontains')
    is_remote = django_filters.BooleanFilter()
    
    # Compensation filters
    salary_min = django_filters.NumberFilter(field_name='salary', lookup_expr='gte')
    salary_max = django_filters.NumberFilter(field_name='salary', lookup_expr='lte')
    hourly_rate_min = django_filters.NumberFilter(field_name='hourly_rate', lookup_expr='gte')
    hourly_rate_max = django_filters.NumberFilter(field_name='hourly_rate', lookup_expr='lte')
    currency = django_filters.CharFilter(lookup_expr='icontains')
    
    # Benefits filters
    benefits_eligible = django_filters.BooleanFilter()
    health_insurance = django_filters.BooleanFilter()
    dental_insurance = django_filters.BooleanFilter()
    vision_insurance = django_filters.BooleanFilter()
    retirement_plan = django_filters.BooleanFilter()
    
    # Additional filters
    nationality = django_filters.CharFilter(lookup_expr='icontains')
    skills = django_filters.CharFilter(lookup_expr='icontains')
    
    # Probation filter
    is_on_probation = django_filters.BooleanFilter(method='filter_on_probation')
    
    def filter_on_probation(self, queryset, name, value):
        if value:
            today = timezone.now().date()
            return queryset.filter(probation_end_date__gte=today)
        return queryset.filter(Q(probation_end_date__lt=today) | Q(probation_end_date__isnull=True))
    
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'badge_number', 'gender', 'marital_status', 'employment_status',
            'work_schedule', 'position', 'department', 'manager', 'is_remote',
            'benefits_eligible', 'health_insurance', 'dental_insurance', 'vision_insurance',
            'retirement_plan', 'nationality', 'currency'
        ]


class AttendanceFilter(django_filters.FilterSet):
    """Filter for Attendance model."""
    # Employee filter
    employee = django_filters.ModelChoiceFilter(queryset=Employee.objects.all())
    
    # Date filters
    date_after = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_before = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    
    # Time filters
    check_in_time_after = django_filters.TimeFilter(field_name='check_in_time', lookup_expr='gte')
    check_in_time_before = django_filters.TimeFilter(field_name='check_in_time', lookup_expr='lte')
    check_out_time_after = django_filters.TimeFilter(field_name='check_out_time', lookup_expr='gte')
    check_out_time_before = django_filters.TimeFilter(field_name='check_out_time', lookup_expr='lte')
    
    # Status filter
    status = django_filters.ChoiceFilter(choices=Attendance._meta.get_field('status').choices)
    
    # Hours filters
    total_hours_min = django_filters.NumberFilter(field_name='total_hours', lookup_expr='gte')
    total_hours_max = django_filters.NumberFilter(field_name='total_hours', lookup_expr='lte')
    overtime_hours_min = django_filters.NumberFilter(field_name='overtime_hours', lookup_expr='gte')
    overtime_hours_max = django_filters.NumberFilter(field_name='overtime_hours', lookup_expr='lte')
    
    # Approval filter
    approved_by = django_filters.ModelChoiceFilter(queryset=Attendance._meta.get_field('approved_by').related_model.objects.all())
    
    class Meta:
        model = Attendance
        fields = ['employee', 'status', 'approved_by']


class LeaveTypeFilter(django_filters.FilterSet):
    """Filter for LeaveType model."""
    name = django_filters.CharFilter(lookup_expr='icontains')
    code = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    is_paid = django_filters.BooleanFilter()
    requires_approval = django_filters.BooleanFilter()
    can_carryover = django_filters.BooleanFilter()
    accrues_monthly = django_filters.BooleanFilter()
    
    # Days filters
    max_days_per_year_min = django_filters.NumberFilter(field_name='max_days_per_year', lookup_expr='gte')
    max_days_per_year_max = django_filters.NumberFilter(field_name='max_days_per_year', lookup_expr='lte')
    advance_notice_days_min = django_filters.NumberFilter(field_name='advance_notice_days', lookup_expr='gte')
    advance_notice_days_max = django_filters.NumberFilter(field_name='advance_notice_days', lookup_expr='lte')
    max_carryover_days_min = django_filters.NumberFilter(field_name='max_carryover_days', lookup_expr='gte')
    max_carryover_days_max = django_filters.NumberFilter(field_name='max_carryover_days', lookup_expr='lte')
    
    # Accrual rate filter
    accrual_rate_min = django_filters.NumberFilter(field_name='accrual_rate', lookup_expr='gte')
    accrual_rate_max = django_filters.NumberFilter(field_name='accrual_rate', lookup_expr='lte')
    
    class Meta:
        model = LeaveType
        fields = ['name', 'code', 'is_active', 'is_paid', 'requires_approval', 'can_carryover', 'accrues_monthly']


class LeaveRequestFilter(django_filters.FilterSet):
    """Filter for LeaveRequest model."""
    # Employee filter
    employee = django_filters.ModelChoiceFilter(queryset=Employee.objects.all())
    
    # Leave type filter
    leave_type = django_filters.ModelChoiceFilter(queryset=LeaveType.objects.all())
    
    # Status filter
    status = django_filters.ChoiceFilter(choices=LeaveRequest._meta.get_field('status').choices)
    
    # Date filters
    start_date_after = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_before = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')
    end_date_after = django_filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_date_before = django_filters.DateFilter(field_name='end_date', lookup_expr='lte')
    
    # Days filter
    total_days_min = django_filters.NumberFilter(field_name='total_days', lookup_expr='gte')
    total_days_max = django_filters.NumberFilter(field_name='total_days', lookup_expr='lte')
    
    # Approval filters
    requested_by = django_filters.ModelChoiceFilter(queryset=LeaveRequest._meta.get_field('requested_by').related_model.objects.all())
    approved_by = django_filters.ModelChoiceFilter(queryset=LeaveRequest._meta.get_field('approved_by').related_model.objects.all())
    
    # Approval date filters
    approved_at_after = django_filters.DateTimeFilter(field_name='approved_at', lookup_expr='gte')
    approved_at_before = django_filters.DateTimeFilter(field_name='approved_at', lookup_expr='lte')
    
    class Meta:
        model = LeaveRequest
        fields = ['employee', 'leave_type', 'status', 'requested_by', 'approved_by']


class PayrollPeriodFilter(django_filters.FilterSet):
    """Filter for PayrollPeriod model."""
    name = django_filters.CharFilter(lookup_expr='icontains')
    period_type = django_filters.ChoiceFilter(choices=PayrollPeriod._meta.get_field('period_type').choices)
    status = django_filters.ChoiceFilter(choices=PayrollPeriod._meta.get_field('status').choices)
    
    # Date filters
    start_date_after = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_before = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')
    end_date_after = django_filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_date_before = django_filters.DateFilter(field_name='end_date', lookup_expr='lte')
    pay_date_after = django_filters.DateFilter(field_name='pay_date', lookup_expr='gte')
    pay_date_before = django_filters.DateFilter(field_name='pay_date', lookup_expr='lte')
    
    # Processing filters
    processed_by = django_filters.ModelChoiceFilter(queryset=PayrollPeriod._meta.get_field('processed_by').related_model.objects.all())
    processed_at_after = django_filters.DateTimeFilter(field_name='processed_at', lookup_expr='gte')
    processed_at_before = django_filters.DateTimeFilter(field_name='processed_at', lookup_expr='lte')
    
    class Meta:
        model = PayrollPeriod
        fields = ['name', 'period_type', 'status', 'processed_by']


class PayrollFilter(django_filters.FilterSet):
    """Filter for Payroll model."""
    # Employee filter
    employee = django_filters.ModelChoiceFilter(queryset=Employee.objects.all())
    
    # Payroll period filter
    payroll_period = django_filters.ModelChoiceFilter(queryset=PayrollPeriod.objects.all())
    
    # Status filter
    status = django_filters.ChoiceFilter(choices=Payroll._meta.get_field('status').choices)
    
    # Amount filters
    basic_salary_min = django_filters.NumberFilter(field_name='basic_salary', lookup_expr='gte')
    basic_salary_max = django_filters.NumberFilter(field_name='basic_salary', lookup_expr='lte')
    gross_pay_min = django_filters.NumberFilter(field_name='gross_pay', lookup_expr='gte')
    gross_pay_max = django_filters.NumberFilter(field_name='gross_pay', lookup_expr='lte')
    net_pay_min = django_filters.NumberFilter(field_name='net_pay', lookup_expr='gte')
    net_pay_max = django_filters.NumberFilter(field_name='net_pay', lookup_expr='lte')
    
    # Hours filters
    hours_worked_min = django_filters.NumberFilter(field_name='hours_worked', lookup_expr='gte')
    hours_worked_max = django_filters.NumberFilter(field_name='hours_worked', lookup_expr='lte')
    overtime_hours_min = django_filters.NumberFilter(field_name='overtime_hours', lookup_expr='gte')
    overtime_hours_max = django_filters.NumberFilter(field_name='overtime_hours', lookup_expr='lte')
    
    class Meta:
        model = Payroll
        fields = ['employee', 'payroll_period', 'status']


class PerformanceReviewFilter(django_filters.FilterSet):
    """Filter for PerformanceReview model."""
    # Employee filter
    employee = django_filters.ModelChoiceFilter(queryset=Employee.objects.all())
    
    # Reviewer filter
    reviewer = django_filters.ModelChoiceFilter(queryset=PerformanceReview._meta.get_field('reviewer').related_model.objects.all())
    
    # Review type filter
    review_type = django_filters.ChoiceFilter(choices=PerformanceReview._meta.get_field('review_type').choices)
    status = django_filters.ChoiceFilter(choices=PerformanceReview._meta.get_field('status').choices)
    
    # Date filters
    review_period_start_after = django_filters.DateFilter(field_name='review_period_start', lookup_expr='gte')
    review_period_start_before = django_filters.DateFilter(field_name='review_period_start', lookup_expr='lte')
    review_period_end_after = django_filters.DateFilter(field_name='review_period_end', lookup_expr='gte')
    review_period_end_before = django_filters.DateFilter(field_name='review_period_end', lookup_expr='lte')
    review_date_after = django_filters.DateFilter(field_name='review_date', lookup_expr='gte')
    review_date_before = django_filters.DateFilter(field_name='review_date', lookup_expr='lte')
    
    # Rating filters
    overall_rating_min = django_filters.NumberFilter(field_name='overall_rating', lookup_expr='gte')
    overall_rating_max = django_filters.NumberFilter(field_name='overall_rating', lookup_expr='lte')
    quality_rating_min = django_filters.NumberFilter(field_name='quality_rating', lookup_expr='gte')
    quality_rating_max = django_filters.NumberFilter(field_name='quality_rating', lookup_expr='lte')
    productivity_rating_min = django_filters.NumberFilter(field_name='productivity_rating', lookup_expr='gte')
    productivity_rating_max = django_filters.NumberFilter(field_name='productivity_rating', lookup_expr='lte')
    teamwork_rating_min = django_filters.NumberFilter(field_name='teamwork_rating', lookup_expr='gte')
    teamwork_rating_max = django_filters.NumberFilter(field_name='teamwork_rating', lookup_expr='lte')
    communication_rating_min = django_filters.NumberFilter(field_name='communication_rating', lookup_expr='gte')
    communication_rating_max = django_filters.NumberFilter(field_name='communication_rating', lookup_expr='lte')
    
    # Acknowledgment filter
    employee_acknowledged = django_filters.BooleanFilter()
    
    class Meta:
        model = PerformanceReview
        fields = ['employee', 'reviewer', 'review_type', 'status', 'employee_acknowledged']


class TrainingFilter(django_filters.FilterSet):
    """Filter for Training model."""
    title = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    training_type = django_filters.ChoiceFilter(choices=Training._meta.get_field('training_type').choices)
    status = django_filters.ChoiceFilter(choices=Training._meta.get_field('status').choices)
    is_online = django_filters.BooleanFilter()
    
    # Date filters
    start_date_after = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_before = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')
    end_date_after = django_filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_date_before = django_filters.DateFilter(field_name='end_date', lookup_expr='lte')
    
    # Duration filters
    duration_hours_min = django_filters.NumberFilter(field_name='duration_hours', lookup_expr='gte')
    duration_hours_max = django_filters.NumberFilter(field_name='duration_hours', lookup_expr='lte')
    
    # Cost filters
    cost_per_participant_min = django_filters.NumberFilter(field_name='cost_per_participant', lookup_expr='gte')
    cost_per_participant_max = django_filters.NumberFilter(field_name='cost_per_participant', lookup_expr='lte')
    total_budget_min = django_filters.NumberFilter(field_name='total_budget', lookup_expr='gte')
    total_budget_max = django_filters.NumberFilter(field_name='total_budget', lookup_expr='lte')
    
    # Location and instructor filters
    location = django_filters.CharFilter(lookup_expr='icontains')
    instructor = django_filters.CharFilter(lookup_expr='icontains')
    
    # Participants filter
    max_participants_min = django_filters.NumberFilter(field_name='max_participants', lookup_expr='gte')
    max_participants_max = django_filters.NumberFilter(field_name='max_participants', lookup_expr='lte')
    
    class Meta:
        model = Training
        fields = ['title', 'training_type', 'status', 'is_online', 'location', 'instructor']


class TrainingEnrollmentFilter(django_filters.FilterSet):
    """Filter for TrainingEnrollment model."""
    # Training filter
    training = django_filters.ModelChoiceFilter(queryset=Training.objects.all())
    
    # Employee filter
    employee = django_filters.ModelChoiceFilter(queryset=Employee.objects.all())
    
    # Status filter
    status = django_filters.ChoiceFilter(choices=TrainingEnrollment._meta.get_field('status').choices)
    
    # Enrollment filters
    enrolled_by = django_filters.ModelChoiceFilter(queryset=TrainingEnrollment._meta.get_field('enrolled_by').related_model.objects.all())
    enrolled_at_after = django_filters.DateTimeFilter(field_name='enrolled_at', lookup_expr='gte')
    enrolled_at_before = django_filters.DateTimeFilter(field_name='enrolled_at', lookup_expr='lte')
    
    # Completion filters
    completion_date_after = django_filters.DateFilter(field_name='completion_date', lookup_expr='gte')
    completion_date_before = django_filters.DateFilter(field_name='completion_date', lookup_expr='lte')
    certificate_issued = django_filters.BooleanFilter()
    
    # Score filters
    score_min = django_filters.NumberFilter(field_name='score', lookup_expr='gte')
    score_max = django_filters.NumberFilter(field_name='score', lookup_expr='lte')
    rating_min = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    rating_max = django_filters.NumberFilter(field_name='rating', lookup_expr='lte')
    
    class Meta:
        model = TrainingEnrollment
        fields = ['training', 'employee', 'status', 'enrolled_by', 'certificate_issued']


class DocumentFilter(django_filters.FilterSet):
    """Filter for Document model."""
    # Employee filter
    employee = django_filters.ModelChoiceFilter(queryset=Employee.objects.all())
    
    # Document type filter
    document_type = django_filters.ChoiceFilter(choices=Document._meta.get_field('document_type').choices)
    
    # Document details
    title = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    
    # Date filters
    issue_date_after = django_filters.DateFilter(field_name='issue_date', lookup_expr='gte')
    issue_date_before = django_filters.DateFilter(field_name='issue_date', lookup_expr='lte')
    expiry_date_after = django_filters.DateFilter(field_name='expiry_date', lookup_expr='gte')
    expiry_date_before = django_filters.DateFilter(field_name='expiry_date', lookup_expr='lte')
    
    # Verification filters
    is_verified = django_filters.BooleanFilter()
    verified_by = django_filters.ModelChoiceFilter(queryset=Document._meta.get_field('verified_by').related_model.objects.all())
    verified_at_after = django_filters.DateTimeFilter(field_name='verified_at', lookup_expr='gte')
    verified_at_before = django_filters.DateTimeFilter(field_name='verified_at', lookup_expr='lte')
    
    # Access filter
    is_public = django_filters.BooleanFilter()
    
    # File size filters
    file_size_min = django_filters.NumberFilter(field_name='file_size', lookup_expr='gte')
    file_size_max = django_filters.NumberFilter(field_name='file_size', lookup_expr='lte')
    
    class Meta:
        model = Document
        fields = ['employee', 'document_type', 'is_verified', 'is_public', 'verified_by']


class PolicyFilter(django_filters.FilterSet):
    """Filter for Policy model."""
    title = django_filters.CharFilter(lookup_expr='icontains')
    policy_type = django_filters.ChoiceFilter(choices=Policy._meta.get_field('policy_type').choices)
    status = django_filters.ChoiceFilter(choices=Policy._meta.get_field('status').choices)
    requires_acknowledgment = django_filters.BooleanFilter()
    
    # Content filters
    content = django_filters.CharFilter(lookup_expr='icontains')
    summary = django_filters.CharFilter(lookup_expr='icontains')
    
    # Version filter
    version = django_filters.CharFilter(lookup_expr='icontains')
    
    # Date filters
    effective_date_after = django_filters.DateFilter(field_name='effective_date', lookup_expr='gte')
    effective_date_before = django_filters.DateFilter(field_name='effective_date', lookup_expr='lte')
    expiry_date_after = django_filters.DateFilter(field_name='expiry_date', lookup_expr='gte')
    expiry_date_before = django_filters.DateFilter(field_name='expiry_date', lookup_expr='lte')
    
    # Approval filters
    approved_by = django_filters.ModelChoiceFilter(queryset=Policy._meta.get_field('approved_by').related_model.objects.all())
    approved_at_after = django_filters.DateTimeFilter(field_name='approved_at', lookup_expr='gte')
    approved_at_before = django_filters.DateTimeFilter(field_name='approved_at', lookup_expr='lte')
    
    class Meta:
        model = Policy
        fields = ['title', 'policy_type', 'status', 'requires_acknowledgment', 'approved_by']


class PolicyAcknowledgmentFilter(django_filters.FilterSet):
    """Filter for PolicyAcknowledgment model."""
    # Policy filter
    policy = django_filters.ModelChoiceFilter(queryset=Policy.objects.all())
    
    # Employee filter
    employee = django_filters.ModelChoiceFilter(queryset=Employee.objects.all())
    
    # Acknowledgment date filters
    acknowledged_at_after = django_filters.DateTimeFilter(field_name='acknowledged_at', lookup_expr='gte')
    acknowledged_at_before = django_filters.DateTimeFilter(field_name='acknowledged_at', lookup_expr='lte')
    
    # IP address filter
    ip_address = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = PolicyAcknowledgment
        fields = ['policy', 'employee']


# Advanced filters for analytics and reporting
class HRAnalyticsFilter(django_filters.FilterSet):
    """Advanced filter for HR analytics."""
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
    
    start_date = django_filters.DateFilter(field_name='hire_date', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='hire_date', lookup_expr='lte')
    
    def filter_date_range(self, queryset, name, value):
        today = timezone.now().date()
        
        if value == 'today':
            return queryset.filter(hire_date=today)
        elif value == 'yesterday':
            yesterday = today - timedelta(days=1)
            return queryset.filter(hire_date=yesterday)
        elif value == 'this_week':
            start_of_week = today - timedelta(days=today.weekday())
            return queryset.filter(hire_date__gte=start_of_week)
        elif value == 'last_week':
            start_of_last_week = today - timedelta(days=today.weekday() + 7)
            end_of_last_week = start_of_last_week + timedelta(days=6)
            return queryset.filter(hire_date__gte=start_of_last_week, hire_date__lte=end_of_last_week)
        elif value == 'this_month':
            start_of_month = today.replace(day=1)
            return queryset.filter(hire_date__gte=start_of_month)
        elif value == 'last_month':
            if today.month == 1:
                start_of_last_month = today.replace(year=today.year - 1, month=12, day=1)
            else:
                start_of_last_month = today.replace(month=today.month - 1, day=1)
            end_of_last_month = today.replace(day=1) - timedelta(days=1)
            return queryset.filter(hire_date__gte=start_of_last_month, hire_date__lte=end_of_last_month)
        elif value == 'this_quarter':
            quarter = (today.month - 1) // 3 + 1
            start_of_quarter = today.replace(month=(quarter - 1) * 3 + 1, day=1)
            return queryset.filter(hire_date__gte=start_of_quarter)
        elif value == 'last_quarter':
            quarter = (today.month - 1) // 3 + 1
            if quarter == 1:
                start_of_last_quarter = today.replace(year=today.year - 1, month=10, day=1)
            else:
                start_of_last_quarter = today.replace(month=(quarter - 2) * 3 + 1, day=1)
            end_of_last_quarter = today.replace(month=(quarter - 1) * 3 + 1, day=1) - timedelta(days=1)
            return queryset.filter(hire_date__gte=start_of_last_quarter, hire_date__lte=end_of_last_quarter)
        elif value == 'this_year':
            start_of_year = today.replace(month=1, day=1)
            return queryset.filter(hire_date__gte=start_of_year)
        elif value == 'last_year':
            start_of_last_year = today.replace(year=today.year - 1, month=1, day=1)
            end_of_last_year = today.replace(year=today.year - 1, month=12, day=31)
            return queryset.filter(hire_date__gte=start_of_last_year, hire_date__lte=end_of_last_year)
        
        return queryset
    
    class Meta:
        model = Employee
        fields = ['date_range', 'start_date', 'end_date']


class AttendanceAnalyticsFilter(django_filters.FilterSet):
    """Advanced filter for attendance analytics."""
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
    
    start_date = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    
    def filter_date_range(self, queryset, name, value):
        today = timezone.now().date()
        
        if value == 'today':
            return queryset.filter(date=today)
        elif value == 'yesterday':
            yesterday = today - timedelta(days=1)
            return queryset.filter(date=yesterday)
        elif value == 'this_week':
            start_of_week = today - timedelta(days=today.weekday())
            return queryset.filter(date__gte=start_of_week)
        elif value == 'last_week':
            start_of_last_week = today - timedelta(days=today.weekday() + 7)
            end_of_last_week = start_of_last_week + timedelta(days=6)
            return queryset.filter(date__gte=start_of_last_week, date__lte=end_of_last_week)
        elif value == 'this_month':
            start_of_month = today.replace(day=1)
            return queryset.filter(date__gte=start_of_month)
        elif value == 'last_month':
            if today.month == 1:
                start_of_last_month = today.replace(year=today.year - 1, month=12, day=1)
            else:
                start_of_last_month = today.replace(month=today.month - 1, day=1)
            end_of_last_month = today.replace(day=1) - timedelta(days=1)
            return queryset.filter(date__gte=start_of_last_month, date__lte=end_of_last_month)
        elif value == 'this_quarter':
            quarter = (today.month - 1) // 3 + 1
            start_of_quarter = today.replace(month=(quarter - 1) * 3 + 1, day=1)
            return queryset.filter(date__gte=start_of_quarter)
        elif value == 'last_quarter':
            quarter = (today.month - 1) // 3 + 1
            if quarter == 1:
                start_of_last_quarter = today.replace(year=today.year - 1, month=10, day=1)
            else:
                start_of_last_quarter = today.replace(month=(quarter - 2) * 3 + 1, day=1)
            end_of_last_quarter = today.replace(month=(quarter - 1) * 3 + 1, day=1) - timedelta(days=1)
            return queryset.filter(date__gte=start_of_last_quarter, date__lte=end_of_last_quarter)
        elif value == 'this_year':
            start_of_year = today.replace(month=1, day=1)
            return queryset.filter(date__gte=start_of_year)
        elif value == 'last_year':
            start_of_last_year = today.replace(year=today.year - 1, month=1, day=1)
            end_of_last_year = today.replace(year=today.year - 1, month=12, day=31)
            return queryset.filter(date__gte=start_of_last_year, date__lte=end_of_last_year)
        
        return queryset
    
    class Meta:
        model = Attendance
        fields = ['date_range', 'start_date', 'end_date']
