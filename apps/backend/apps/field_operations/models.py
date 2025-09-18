"""
Field Operations models for TidyGen ERP.
Handles field service teams, dispatch, routes, and job management.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel
from decimal import Decimal


class FieldTeam(BaseModel):
    """
    Represents a field service team.
    """
    TEAM_TYPES = [
        ('cleaning', 'Cleaning Team'),
        ('maintenance', 'Maintenance Team'),
        ('specialized', 'Specialized Services'),
        ('emergency', 'Emergency Response'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_break', 'On Break'),
        ('off_duty', 'Off Duty'),
    ]
    
    # Basic Information
    name = models.CharField(_('team name'), max_length=100)
    team_type = models.CharField(_('team type'), max_length=20, choices=TEAM_TYPES)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Team Details
    description = models.TextField(_('description'), blank=True)
    max_capacity = models.IntegerField(_('max capacity'), default=5)
    current_capacity = models.IntegerField(_('current capacity'), default=0)
    
    # Vehicle Assignment
    assigned_vehicle = models.ForeignKey('facility_management.Vehicle', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_teams')
    
    # Location
    home_base = models.ForeignKey('facility_management.Facility', on_delete=models.SET_NULL, null=True, blank=True, related_name='field_teams')
    current_location = models.CharField(_('current location'), max_length=200, blank=True)
    
    # Performance Metrics
    total_jobs_completed = models.IntegerField(_('total jobs completed'), default=0)
    average_rating = models.DecimalField(_('average rating'), max_digits=3, decimal_places=2, default=0)
    on_time_percentage = models.DecimalField(_('on time percentage'), max_digits=5, decimal_places=2, default=0)
    
    # Web3 Integration
    blockchain_address = models.CharField(_('blockchain address'), max_length=42, blank=True)
    nft_token_id = models.CharField(_('NFT token ID'), max_length=100, blank=True)
    
    class Meta:
        verbose_name = _('Field Team')
        verbose_name_plural = _('Field Teams')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_team_type_display()})"


class TeamMember(BaseModel):
    """
    Represents a member of a field team.
    """
    ROLE_CHOICES = [
        ('team_leader', 'Team Leader'),
        ('specialist', 'Specialist'),
        ('technician', 'Technician'),
        ('helper', 'Helper'),
        ('trainee', 'Trainee'),
    ]
    
    # Relationships
    team = models.ForeignKey(FieldTeam, on_delete=models.CASCADE, related_name='members')
    employee = models.ForeignKey('hr.Employee', on_delete=models.CASCADE, related_name='team_memberships')
    
    # Role Information
    role = models.CharField(_('role'), max_length=20, choices=ROLE_CHOICES)
    is_team_leader = models.BooleanField(_('is team leader'), default=False)
    
    # Assignment Details
    assigned_date = models.DateField(_('assigned date'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    
    # Performance
    individual_rating = models.DecimalField(_('individual rating'), max_digits=3, decimal_places=2, default=0)
    jobs_completed = models.IntegerField(_('jobs completed'), default=0)
    
    class Meta:
        verbose_name = _('Team Member')
        verbose_name_plural = _('Team Members')
        unique_together = ['team', 'employee']
        ordering = ['team', 'role']
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.team.name}"


class ServiceRoute(BaseModel):
    """
    Represents a service route with multiple stops.
    """
    ROUTE_TYPES = [
        ('daily', 'Daily Route'),
        ('weekly', 'Weekly Route'),
        ('monthly', 'Monthly Route'),
        ('custom', 'Custom Route'),
    ]
    
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Basic Information
    name = models.CharField(_('route name'), max_length=200)
    route_type = models.CharField(_('route type'), max_length=20, choices=ROUTE_TYPES)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='planned')
    
    # Route Details
    description = models.TextField(_('description'), blank=True)
    total_distance = models.DecimalField(_('total distance (miles)'), max_digits=8, decimal_places=2, default=0)
    estimated_duration = models.DurationField(_('estimated duration'), null=True, blank=True)
    actual_duration = models.DurationField(_('actual duration'), null=True, blank=True)
    
    # Scheduling
    scheduled_date = models.DateField(_('scheduled date'))
    start_time = models.TimeField(_('start time'), null=True, blank=True)
    end_time = models.TimeField(_('end time'), null=True, blank=True)
    
    # Team Assignment
    assigned_team = models.ForeignKey(FieldTeam, on_delete=models.SET_NULL, null=True, blank=True, related_name='routes')
    
    # Performance Metrics
    total_stops = models.IntegerField(_('total stops'), default=0)
    completed_stops = models.IntegerField(_('completed stops'), default=0)
    efficiency_rating = models.DecimalField(_('efficiency rating'), max_digits=3, decimal_places=2, default=0)
    
    # Web3 Integration
    blockchain_transaction_hash = models.CharField(_('blockchain transaction hash'), max_length=66, blank=True)
    
    class Meta:
        verbose_name = _('Service Route')
        verbose_name_plural = _('Service Routes')
        ordering = ['-scheduled_date', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.scheduled_date}"


class RouteStop(BaseModel):
    """
    Represents a stop on a service route.
    """
    STOP_TYPES = [
        ('service', 'Service Stop'),
        ('pickup', 'Pickup Stop'),
        ('delivery', 'Delivery Stop'),
        ('maintenance', 'Maintenance Stop'),
        ('break', 'Break Stop'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Relationships
    route = models.ForeignKey(ServiceRoute, on_delete=models.CASCADE, related_name='stops')
    client = models.ForeignKey('sales.Client', on_delete=models.CASCADE, null=True, blank=True, related_name='route_stops')
    
    # Stop Details
    stop_type = models.CharField(_('stop type'), max_length=20, choices=STOP_TYPES)
    sequence_number = models.IntegerField(_('sequence number'), validators=[MinValueValidator(1)])
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Location
    address = models.TextField(_('address'))
    latitude = models.DecimalField(_('latitude'), max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(_('longitude'), max_digits=11, decimal_places=8, null=True, blank=True)
    
    # Timing
    estimated_arrival = models.DateTimeField(_('estimated arrival'), null=True, blank=True)
    actual_arrival = models.DateTimeField(_('actual arrival'), null=True, blank=True)
    estimated_departure = models.DateTimeField(_('estimated departure'), null=True, blank=True)
    actual_departure = models.DateTimeField(_('actual departure'), null=True, blank=True)
    estimated_duration = models.DurationField(_('estimated duration'), null=True, blank=True)
    actual_duration = models.DurationField(_('actual duration'), null=True, blank=True)
    
    # Service Details
    service_notes = models.TextField(_('service notes'), blank=True)
    completion_notes = models.TextField(_('completion notes'), blank=True)
    
    # Web3 Integration
    blockchain_transaction_hash = models.CharField(_('blockchain transaction hash'), max_length=66, blank=True)
    
    class Meta:
        verbose_name = _('Route Stop')
        verbose_name_plural = _('Route Stops')
        ordering = ['route', 'sequence_number']
        unique_together = ['route', 'sequence_number']
    
    def __str__(self):
        return f"{self.route.name} - Stop {self.sequence_number}"


class FieldJob(BaseModel):
    """
    Represents a field service job.
    """
    JOB_TYPES = [
        ('cleaning', 'Cleaning Service'),
        ('maintenance', 'Maintenance'),
        ('inspection', 'Inspection'),
        ('repair', 'Repair'),
        ('installation', 'Installation'),
        ('emergency', 'Emergency Service'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
        ('emergency', 'Emergency'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('on_hold', 'On Hold'),
    ]
    
    # Basic Information
    job_number = models.CharField(_('job number'), max_length=50, unique=True)
    title = models.CharField(_('job title'), max_length=200)
    job_type = models.CharField(_('job type'), max_length=20, choices=JOB_TYPES)
    priority = models.CharField(_('priority'), max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Job Details
    description = models.TextField(_('description'))
    special_instructions = models.TextField(_('special instructions'), blank=True)
    
    # Client Information
    client = models.ForeignKey('sales.Client', on_delete=models.CASCADE, related_name='field_jobs')
    contact_person = models.CharField(_('contact person'), max_length=100, blank=True)
    contact_phone = models.CharField(_('contact phone'), max_length=20, blank=True)
    
    # Location
    service_address = models.TextField(_('service address'))
    latitude = models.DecimalField(_('latitude'), max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(_('longitude'), max_digits=11, decimal_places=8, null=True, blank=True)
    
    # Scheduling
    scheduled_date = models.DateField(_('scheduled date'))
    scheduled_start_time = models.TimeField(_('scheduled start time'))
    scheduled_end_time = models.TimeField(_('scheduled end time'))
    estimated_duration = models.DurationField(_('estimated duration'), null=True, blank=True)
    actual_duration = models.DurationField(_('actual duration'), null=True, blank=True)
    
    # Assignment
    assigned_team = models.ForeignKey(FieldTeam, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_jobs')
    assigned_route = models.ForeignKey(ServiceRoute, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs')
    
    # Financial Information
    estimated_cost = models.DecimalField(_('estimated cost'), max_digits=10, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(_('actual cost'), max_digits=10, decimal_places=2, null=True, blank=True)
    client_rate = models.DecimalField(_('client rate'), max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Completion
    completion_notes = models.TextField(_('completion notes'), blank=True)
    client_satisfaction_rating = models.IntegerField(_('client satisfaction rating'), validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    completion_photos = models.JSONField(_('completion photos'), default=list, blank=True)
    
    # Web3 Integration
    smart_contract_address = models.CharField(_('smart contract address'), max_length=42, blank=True)
    blockchain_transaction_hash = models.CharField(_('blockchain transaction hash'), max_length=66, blank=True)
    payment_released = models.BooleanField(_('payment released'), default=False)
    
    class Meta:
        verbose_name = _('Field Job')
        verbose_name_plural = _('Field Jobs')
        ordering = ['-scheduled_date', 'scheduled_start_time']
    
    def __str__(self):
        return f"{self.job_number} - {self.title}"


class JobEquipment(BaseModel):
    """
    Tracks equipment used for specific jobs.
    """
    job = models.ForeignKey(FieldJob, on_delete=models.CASCADE, related_name='equipment_used')
    equipment = models.ForeignKey('facility_management.Equipment', on_delete=models.CASCADE, related_name='job_usage')
    
    # Usage Details
    quantity_used = models.IntegerField(_('quantity used'), default=1)
    usage_notes = models.TextField(_('usage notes'), blank=True)
    
    # Condition
    condition_before = models.CharField(_('condition before'), max_length=20, choices=[
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ], default='good')
    condition_after = models.CharField(_('condition after'), max_length=20, choices=[
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ], default='good')
    
    class Meta:
        verbose_name = _('Job Equipment')
        verbose_name_plural = _('Job Equipment')
        unique_together = ['job', 'equipment']
    
    def __str__(self):
        return f"{self.job.job_number} - {self.equipment.name}"


class DispatchLog(BaseModel):
    """
    Logs dispatch activities and communications.
    """
    LOG_TYPES = [
        ('assignment', 'Job Assignment'),
        ('update', 'Status Update'),
        ('communication', 'Communication'),
        ('route_change', 'Route Change'),
        ('emergency', 'Emergency'),
    ]
    
    # Related Objects
    job = models.ForeignKey(FieldJob, on_delete=models.CASCADE, null=True, blank=True, related_name='dispatch_logs')
    team = models.ForeignKey(FieldTeam, on_delete=models.CASCADE, null=True, blank=True, related_name='dispatch_logs')
    
    # Log Details
    log_type = models.CharField(_('log type'), max_length=20, choices=LOG_TYPES)
    message = models.TextField(_('message'))
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)
    
    # Personnel
    created_by = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='dispatch_logs')
    
    # Web3 Integration
    blockchain_transaction_hash = models.CharField(_('blockchain transaction hash'), max_length=66, blank=True)
    
    class Meta:
        verbose_name = _('Dispatch Log')
        verbose_name_plural = _('Dispatch Logs')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.get_log_type_display()} - {self.timestamp}"
