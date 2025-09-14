"""
HR management models for TidyGen ERP platform.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel

User = get_user_model()


class Department(BaseModel):
    """
    Department model for organizational structure.
    """
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    
    # Department hierarchy
    parent_department = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sub_departments'
    )
    
    # Management
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments'
    )
    
    # Financial
    budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    cost_center = models.CharField(max_length=50, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        unique_together = ['name']
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Position(BaseModel):
    """
    Job position model.
    """
    title = models.CharField(max_length=200)
    code = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    
    # Department and reporting
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='positions')
    reports_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates'
    )
    
    # Job details
    job_level = models.CharField(
        max_length=20,
        choices=[
            ('entry', 'Entry Level'),
            ('junior', 'Junior'),
            ('mid', 'Mid Level'),
            ('senior', 'Senior'),
            ('lead', 'Lead'),
            ('manager', 'Manager'),
            ('director', 'Director'),
            ('executive', 'Executive'),
        ],
        default='mid'
    )
    
    employment_type = models.CharField(
        max_length=20,
        choices=[
            ('full_time', 'Full Time'),
            ('part_time', 'Part Time'),
            ('contract', 'Contract'),
            ('intern', 'Intern'),
            ('consultant', 'Consultant'),
        ],
        default='full_time'
    )
    
    # Compensation
    min_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    
    # Requirements
    required_skills = models.TextField(blank=True)
    required_education = models.TextField(blank=True)
    required_experience = models.IntegerField(null=True, blank=True)  # years
    
    # Status
    is_active = models.BooleanField(default=True)
    is_remote = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Position'
        verbose_name_plural = 'Positions'
        unique_together = ['title', 'department']
        ordering = ['title']
    
    def __str__(self):
        return f"{self.title} - {self.department.name}"


class Employee(BaseModel):
    """
    Employee model extending the base User model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    
    # Employee identification
    employee_id = models.CharField(max_length=50, unique=True)
    badge_number = models.CharField(max_length=50, blank=True)
    
    # Personal information
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
            ('prefer_not_to_say', 'Prefer not to say'),
        ],
        blank=True
    )
    marital_status = models.CharField(
        max_length=20,
        choices=[
            ('single', 'Single'),
            ('married', 'Married'),
            ('divorced', 'Divorced'),
            ('widowed', 'Widowed'),
            ('separated', 'Separated'),
        ],
        blank=True
    )
    nationality = models.CharField(max_length=100, blank=True)
    
    # Contact information
    personal_email = models.EmailField(blank=True)
    personal_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)
    
    # Address
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Employment details
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates'
    )
    
    # Employment dates
    hire_date = models.DateField()
    probation_end_date = models.DateField(null=True, blank=True)
    termination_date = models.DateField(null=True, blank=True)
    
    # Employment status
    employment_status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('on_leave', 'On Leave'),
            ('terminated', 'Terminated'),
            ('resigned', 'Resigned'),
        ],
        default='active'
    )
    
    # Work arrangement
    work_location = models.CharField(max_length=200, blank=True)
    is_remote = models.BooleanField(default=False)
    work_schedule = models.CharField(
        max_length=20,
        choices=[
            ('full_time', 'Full Time'),
            ('part_time', 'Part Time'),
            ('flexible', 'Flexible'),
            ('shift', 'Shift Work'),
        ],
        default='full_time'
    )
    
    # Compensation
    salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    
    # Benefits
    benefits_eligible = models.BooleanField(default=True)
    health_insurance = models.BooleanField(default=False)
    dental_insurance = models.BooleanField(default=False)
    vision_insurance = models.BooleanField(default=False)
    retirement_plan = models.BooleanField(default=False)
    
    # Additional information
    skills = models.TextField(blank=True)
    certifications = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        ordering = ['user__last_name', 'user__first_name']
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['employment_status', 'hire_date']),
            models.Index(fields=['department', 'position']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"
    
    @property
    def full_name(self):
        return self.user.get_full_name()
    
    @property
    def is_on_probation(self):
        if self.probation_end_date:
            from django.utils import timezone
            return timezone.now().date() <= self.probation_end_date
        return False


class Attendance(BaseModel):
    """
    Employee attendance tracking.
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    
    # Time tracking
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    break_start_time = models.TimeField(null=True, blank=True)
    break_end_time = models.TimeField(null=True, blank=True)
    
    # Calculated fields
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('present', 'Present'),
            ('absent', 'Absent'),
            ('late', 'Late'),
            ('half_day', 'Half Day'),
            ('on_leave', 'On Leave'),
            ('holiday', 'Holiday'),
        ],
        default='present'
    )
    
    # Additional information
    notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_attendances'
    )
    
    class Meta:
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances'
        unique_together = ['employee', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.date}"


class LeaveType(BaseModel):
    """
    Leave type model for different types of leave.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    
    # Leave configuration
    max_days_per_year = models.IntegerField(null=True, blank=True)
    is_paid = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=True)
    advance_notice_days = models.IntegerField(default=0)
    
    # Carryover and accrual
    can_carryover = models.BooleanField(default=False)
    max_carryover_days = models.IntegerField(null=True, blank=True)
    accrues_monthly = models.BooleanField(default=False)
    accrual_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Leave Type'
        verbose_name_plural = 'Leave Types'
        unique_together = ['name']
        ordering = ['name']
    
    def __str__(self):
        return self.name


class LeaveRequest(BaseModel):
    """
    Employee leave request model.
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='requests')
    
    # Leave details
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.DecimalField(max_digits=5, decimal_places=2)
    reason = models.TextField()
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    
    # Approval workflow
    requested_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='requested_leaves'
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Additional information
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Leave Request'
        verbose_name_plural = 'Leave Requests'
        ordering = ['-created']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} ({self.start_date} to {self.end_date})"


class PayrollPeriod(BaseModel):
    """
    Payroll period model.
    """
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Period details
    period_type = models.CharField(
        max_length=20,
        choices=[
            ('weekly', 'Weekly'),
            ('bi_weekly', 'Bi-weekly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
        ],
        default='monthly'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft'
    )
    
    # Processing dates
    pay_date = models.DateField()
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_payrolls'
    )
    
    class Meta:
        verbose_name = 'Payroll Period'
        verbose_name_plural = 'Payroll Periods'
        unique_together = ['name']
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"


class Payroll(BaseModel):
    """
    Employee payroll model.
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payrolls')
    payroll_period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE, related_name='payrolls')
    
    # Basic pay
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overtime_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Allowances
    allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bonuses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    commissions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Deductions
    tax_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    social_security = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    health_insurance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Totals
    gross_pay = models.DecimalField(max_digits=12, decimal_places=2)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('approved', 'Approved'),
            ('paid', 'Paid'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft'
    )
    
    # Additional information
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Payroll'
        verbose_name_plural = 'Payrolls'
        unique_together = ['employee', 'payroll_period']
        ordering = ['-payroll_period__start_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.payroll_period.name}"


class PerformanceReview(BaseModel):
    """
    Employee performance review model.
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='performance_reviews')
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conducted_reviews'
    )
    
    # Review period
    review_period_start = models.DateField()
    review_period_end = models.DateField()
    review_date = models.DateField()
    
    # Review details
    review_type = models.CharField(
        max_length=20,
        choices=[
            ('annual', 'Annual'),
            ('quarterly', 'Quarterly'),
            ('probation', 'Probation'),
            ('project', 'Project'),
            ('informal', 'Informal'),
        ],
        default='annual'
    )
    
    # Ratings (1-5 scale)
    overall_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    quality_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    productivity_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    teamwork_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    communication_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    
    # Review content
    strengths = models.TextField(blank=True)
    areas_for_improvement = models.TextField(blank=True)
    goals_achieved = models.TextField(blank=True)
    goals_for_next_period = models.TextField(blank=True)
    comments = models.TextField(blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('acknowledged', 'Acknowledged'),
        ],
        default='draft'
    )
    
    # Acknowledgment
    employee_acknowledged = models.BooleanField(default=False)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Performance Review'
        verbose_name_plural = 'Performance Reviews'
        ordering = ['-review_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.review_type.title()} Review ({self.review_date})"


class Training(BaseModel):
    """
    Training and development model.
    """
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Training details
    training_type = models.CharField(
        max_length=20,
        choices=[
            ('internal', 'Internal'),
            ('external', 'External'),
            ('online', 'Online'),
            ('workshop', 'Workshop'),
            ('conference', 'Conference'),
            ('certification', 'Certification'),
        ],
        default='internal'
    )
    
    # Scheduling
    start_date = models.DateField()
    end_date = models.DateField()
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Location and delivery
    location = models.CharField(max_length=200, blank=True)
    is_online = models.BooleanField(default=False)
    instructor = models.CharField(max_length=200, blank=True)
    
    # Cost and budget
    cost_per_participant = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Requirements
    prerequisites = models.TextField(blank=True)
    max_participants = models.IntegerField(null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('planned', 'Planned'),
            ('open', 'Open for Registration'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        default='planned'
    )
    
    class Meta:
        verbose_name = 'Training'
        verbose_name_plural = 'Trainings'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.title} ({self.start_date} to {self.end_date})"


class TrainingEnrollment(BaseModel):
    """
    Training enrollment model.
    """
    training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name='enrollments')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='training_enrollments')
    
    # Enrollment details
    enrolled_at = models.DateTimeField(auto_now_add=True)
    enrolled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='enrolled_trainings'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('enrolled', 'Enrolled'),
            ('attending', 'Attending'),
            ('completed', 'Completed'),
            ('dropped', 'Dropped'),
            ('failed', 'Failed'),
        ],
        default='enrolled'
    )
    
    # Completion
    completion_date = models.DateField(null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    certificate_issued = models.BooleanField(default=False)
    
    # Feedback
    feedback = models.TextField(blank=True)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = 'Training Enrollment'
        verbose_name_plural = 'Training Enrollments'
        unique_together = ['training', 'employee']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.training.title}"


class Document(BaseModel):
    """
    HR document model for employee documents.
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    
    # Document details
    document_type = models.CharField(
        max_length=30,
        choices=[
            ('contract', 'Employment Contract'),
            ('id_copy', 'ID Copy'),
            ('passport', 'Passport'),
            ('visa', 'Visa'),
            ('work_permit', 'Work Permit'),
            ('degree', 'Degree Certificate'),
            ('certificate', 'Professional Certificate'),
            ('resume', 'Resume'),
            ('reference', 'Reference Letter'),
            ('medical', 'Medical Certificate'),
            ('other', 'Other'),
        ]
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='hr_documents/')
    file_size = models.IntegerField(null=True, blank=True)
    
    # Document metadata
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_documents'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Access control
    is_public = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'HR Document'
        verbose_name_plural = 'HR Documents'
        ordering = ['-created']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.title}"


class Policy(BaseModel):
    """
    HR policy model.
    """
    title = models.CharField(max_length=200)
    policy_type = models.CharField(
        max_length=30,
        choices=[
            ('general', 'General'),
            ('leave', 'Leave Policy'),
            ('attendance', 'Attendance Policy'),
            ('code_of_conduct', 'Code of Conduct'),
            ('harassment', 'Anti-Harassment'),
            ('safety', 'Safety Policy'),
            ('remote_work', 'Remote Work Policy'),
            ('dress_code', 'Dress Code'),
            ('other', 'Other'),
        ],
        default='general'
    )
    
    # Policy content
    content = models.TextField()
    summary = models.TextField(blank=True)
    
    # Version control
    version = models.CharField(max_length=20, default='1.0')
    effective_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    
    # Approval
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='approved_policies'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('under_review', 'Under Review'),
            ('approved', 'Approved'),
            ('active', 'Active'),
            ('archived', 'Archived'),
        ],
        default='draft'
    )
    
    # Acknowledgment
    requires_acknowledgment = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'HR Policy'
        verbose_name_plural = 'HR Policies'
        ordering = ['-effective_date']
    
    def __str__(self):
        return f"{self.title} (v{self.version})"


class PolicyAcknowledgment(BaseModel):
    """
    Policy acknowledgment model.
    """
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='acknowledgments')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='policy_acknowledgments')
    
    # Acknowledgment details
    acknowledged_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Policy Acknowledgment'
        verbose_name_plural = 'Policy Acknowledgments'
        unique_together = ['policy', 'employee']
        ordering = ['-acknowledged_at']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.policy.title}"
