"""
Comprehensive scheduling management models for iNEAT ERP platform.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal
import uuid

from apps.core.models import BaseModel

User = get_user_model()


class ScheduleTemplate(BaseModel):
    """
    Template for creating recurring schedules.
    """
    SCHEDULE_TYPES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('custom', 'Custom'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_TYPES, default='weekly')
    
    # Template settings
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    
    # Recurrence settings
    recurrence_interval = models.PositiveIntegerField(default=1)  # Every X days/weeks/months
    recurrence_days = models.JSONField(default=list, blank=True)  # Days of week for weekly
    recurrence_dates = models.JSONField(default=list, blank=True)  # Specific dates for custom
    
    # Time settings
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    
    # Break settings
    break_duration_minutes = models.PositiveIntegerField(default=0)
    break_start_time = models.TimeField(null=True, blank=True)
    
    # Capacity and limits
    max_capacity = models.PositiveIntegerField(default=1)
    min_advance_booking_hours = models.PositiveIntegerField(default=24)
    max_advance_booking_days = models.PositiveIntegerField(default=30)
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=3, default='USD')
    
    class Meta:
        verbose_name = 'Schedule Template'
        verbose_name_plural = 'Schedule Templates'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Resource(BaseModel):
    """
    Resources that can be scheduled (rooms, equipment, vehicles, etc.).
    """
    RESOURCE_TYPES = [
        ('room', 'Room'),
        ('equipment', 'Equipment'),
        ('vehicle', 'Vehicle'),
        ('person', 'Person'),
        ('service', 'Service'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, default='room')
    description = models.TextField(blank=True)
    
    # Location and details
    location = models.CharField(max_length=200, blank=True)
    capacity = models.PositiveIntegerField(default=1)
    specifications = models.JSONField(default=dict, blank=True)  # Technical specs, features, etc.
    
    # Availability
    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    
    # Maintenance
    maintenance_schedule = models.JSONField(default=dict, blank=True)
    last_maintenance = models.DateTimeField(null=True, blank=True)
    next_maintenance = models.DateTimeField(null=True, blank=True)
    
    # Cost
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=3, default='USD')
    
    # Images and documents
    image_url = models.URLField(blank=True)
    documents = models.JSONField(default=list, blank=True)  # List of document URLs
    
    class Meta:
        verbose_name = 'Resource'
        verbose_name_plural = 'Resources'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_resource_type_display()})"


class Team(BaseModel):
    """
    Teams that can be assigned to appointments or tasks.
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Team settings
    is_active = models.BooleanField(default=True)
    max_members = models.PositiveIntegerField(null=True, blank=True)
    
    # Team lead
    team_lead = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_teams'
    )
    
    # Skills and specializations
    skills = models.JSONField(default=list, blank=True)
    specializations = models.JSONField(default=list, blank=True)
    
    # Availability
    availability_schedule = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class TeamMember(BaseModel):
    """
    Members of teams with their roles and availability.
    """
    ROLES = [
        ('member', 'Member'),
        ('lead', 'Lead'),
        ('specialist', 'Specialist'),
        ('trainee', 'Trainee'),
        ('consultant', 'Consultant'),
    ]
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    role = models.CharField(max_length=20, choices=ROLES, default='member')
    
    # Membership details
    joined_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    # Skills and certifications
    skills = models.JSONField(default=list, blank=True)
    certifications = models.JSONField(default=list, blank=True)
    
    # Availability
    availability_schedule = models.JSONField(default=dict, blank=True)
    max_hours_per_week = models.PositiveIntegerField(default=40)
    
    class Meta:
        verbose_name = 'Team Member'
        verbose_name_plural = 'Team Members'
        unique_together = ['team', 'user']
        ordering = ['team', 'user']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.team.name} ({self.get_role_display()})"


class Appointment(BaseModel):
    """
    Scheduled appointments with clients, teams, and resources.
    """
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Scheduling
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField()
    
    # Status and priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    
    # Client information
    client_name = models.CharField(max_length=200, blank=True)
    client_email = models.EmailField(blank=True)
    client_phone = models.CharField(max_length=20, blank=True)
    client_notes = models.TextField(blank=True)
    
    # Assignment
    assigned_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    assigned_users = models.ManyToManyField(User, blank=True, related_name='assigned_appointments')
    required_resources = models.ManyToManyField(Resource, blank=True, related_name='appointments')
    
    # Location
    location = models.CharField(max_length=200, blank=True)
    is_virtual = models.BooleanField(default=False)
    meeting_url = models.URLField(blank=True)
    
    # Recurrence
    is_recurring = models.BooleanField(default=False)
    recurrence_rule = models.JSONField(default=dict, blank=True)
    parent_appointment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='recurring_instances')
    
    # Pricing and billing
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=3, default='USD')
    is_billable = models.BooleanField(default=True)
    
    # Reminders and notifications
    reminder_sent = models.BooleanField(default=False)
    reminder_datetime = models.DateTimeField(null=True, blank=True)
    
    # Completion
    completion_notes = models.TextField(blank=True)
    completion_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    completion_feedback = models.TextField(blank=True)
    
    # External references
    external_id = models.CharField(max_length=100, blank=True)  # For integration with external systems
    external_url = models.URLField(blank=True)
    
    class Meta:
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        ordering = ['start_datetime']
        indexes = [
            models.Index(fields=['start_datetime', 'end_datetime']),
            models.Index(fields=['status']),
            models.Index(fields=['start_datetime']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.start_datetime.strftime('%Y-%m-%d %H:%M')}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.end_datetime <= self.start_datetime:
            raise ValidationError("End datetime must be after start datetime.")
        
        if self.duration_minutes <= 0:
            raise ValidationError("Duration must be positive.")


class ScheduleConflict(BaseModel):
    """
    Tracks scheduling conflicts and resolutions.
    """
    CONFLICT_TYPES = [
        ('double_booking', 'Double Booking'),
        ('resource_conflict', 'Resource Conflict'),
        ('team_conflict', 'Team Conflict'),
        ('time_conflict', 'Time Conflict'),
        ('location_conflict', 'Location Conflict'),
        ('capacity_exceeded', 'Capacity Exceeded'),
    ]
    
    RESOLUTION_STATUS = [
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('ignored', 'Ignored'),
        ('escalated', 'Escalated'),
    ]
    
    conflict_type = models.CharField(max_length=20, choices=CONFLICT_TYPES)
    status = models.CharField(max_length=20, choices=RESOLUTION_STATUS, default='pending')
    
    # Conflicting appointments
    primary_appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='primary_conflicts'
    )
    conflicting_appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='conflicting_conflicts'
    )
    
    # Conflict details
    conflict_description = models.TextField()
    conflict_datetime = models.DateTimeField()
    affected_resources = models.ManyToManyField(Resource, blank=True)
    affected_users = models.ManyToManyField(User, blank=True)
    
    # Resolution
    resolution_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_conflicts')
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Impact assessment
    impact_level = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], default='medium')
    
    class Meta:
        verbose_name = 'Schedule Conflict'
        verbose_name_plural = 'Schedule Conflicts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_conflict_type_display()} - {self.primary_appointment.title}"


class ScheduleRule(BaseModel):
    """
    Business rules for scheduling (working hours, holidays, etc.).
    """
    RULE_TYPES = [
        ('working_hours', 'Working Hours'),
        ('holiday', 'Holiday'),
        ('break_time', 'Break Time'),
        ('maintenance', 'Maintenance'),
        ('blackout', 'Blackout Period'),
        ('capacity_limit', 'Capacity Limit'),
        ('advance_booking', 'Advance Booking'),
        ('cancellation', 'Cancellation'),
    ]
    
    name = models.CharField(max_length=200)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES)
    description = models.TextField(blank=True)
    
    # Rule settings
    is_active = models.BooleanField(default=True)
    is_global = models.BooleanField(default=False)  # Applies to all resources/users
    
    # Scope
    applies_to_resources = models.ManyToManyField(Resource, blank=True)
    applies_to_users = models.ManyToManyField(User, blank=True)
    applies_to_teams = models.ManyToManyField(Team, blank=True)
    
    # Time settings
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    
    # Recurrence
    is_recurring = models.BooleanField(default=False)
    recurrence_rule = models.JSONField(default=dict, blank=True)
    
    # Rule parameters
    parameters = models.JSONField(default=dict, blank=True)  # Flexible parameters for different rule types
    
    class Meta:
        verbose_name = 'Schedule Rule'
        verbose_name_plural = 'Schedule Rules'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_rule_type_display()})"


class ScheduleNotification(BaseModel):
    """
    Notifications related to scheduling events.
    """
    NOTIFICATION_TYPES = [
        ('appointment_created', 'Appointment Created'),
        ('appointment_updated', 'Appointment Updated'),
        ('appointment_cancelled', 'Appointment Cancelled'),
        ('appointment_reminder', 'Appointment Reminder'),
        ('conflict_detected', 'Conflict Detected'),
        ('resource_unavailable', 'Resource Unavailable'),
        ('team_member_unavailable', 'Team Member Unavailable'),
        ('schedule_change', 'Schedule Change'),
    ]
    
    DELIVERY_METHODS = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App Notification'),
    ]
    
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHODS, default='email')
    
    # Recipients
    recipients = models.ManyToManyField(User, related_name='schedule_notifications')
    
    # Content
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related objects
    related_appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    related_conflict = models.ForeignKey(ScheduleConflict, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    
    # Delivery
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    
    # Delivery details
    delivery_details = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Schedule Notification'
        verbose_name_plural = 'Schedule Notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.subject}"


class ScheduleAnalytics(BaseModel):
    """
    Analytics and reporting for scheduling data.
    """
    
    # Time period
    period_start = models.DateField()
    period_end = models.DateField()
    period_type = models.CharField(max_length=20, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ])
    
    # Appointment metrics
    total_appointments = models.PositiveIntegerField(default=0)
    completed_appointments = models.PositiveIntegerField(default=0)
    cancelled_appointments = models.PositiveIntegerField(default=0)
    no_show_appointments = models.PositiveIntegerField(default=0)
    
    # Utilization metrics
    total_scheduled_hours = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_available_hours = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    utilization_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    # Resource metrics
    resource_utilization = models.JSONField(default=dict, blank=True)
    team_utilization = models.JSONField(default=dict, blank=True)
    
    # Conflict metrics
    total_conflicts = models.PositiveIntegerField(default=0)
    resolved_conflicts = models.PositiveIntegerField(default=0)
    conflict_resolution_time = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Revenue metrics
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    average_appointment_value = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Additional metrics
    metrics = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = 'Schedule Analytics'
        verbose_name_plural = 'Schedule Analytics'
        ordering = ['-period_start']
        unique_together = ['period_start', 'period_end', 'period_type']
    
    def __str__(self):
        return f"Analytics ({self.period_start} to {self.period_end})"


class ScheduleIntegration(BaseModel):
    """
    Integration with external scheduling systems.
    """
    INTEGRATION_TYPES = [
        ('calendar', 'Calendar System'),
        ('booking', 'Booking System'),
        ('crm', 'CRM System'),
        ('erp', 'ERP System'),
        ('communication', 'Communication Platform'),
        ('payment', 'Payment System'),
    ]
    
    name = models.CharField(max_length=200)
    integration_type = models.CharField(max_length=20, choices=INTEGRATION_TYPES)
    provider_name = models.CharField(max_length=100)
    provider_url = models.URLField(blank=True)
    
    # Configuration
    is_active = models.BooleanField(default=True)
    configuration = models.JSONField(default=dict, blank=True)
    
    # Authentication
    api_key = models.CharField(max_length=500, blank=True)
    api_secret = models.CharField(max_length=500, blank=True)
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Sync settings
    sync_enabled = models.BooleanField(default=True)
    sync_frequency = models.CharField(max_length=20, choices=[
        ('realtime', 'Real-time'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ], default='hourly')
    last_sync = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=20, choices=[
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('error', 'Error'),
        ('syncing', 'Syncing'),
    ], default='disconnected')
    
    # Error handling
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    
    class Meta:
        verbose_name = 'Schedule Integration'
        verbose_name_plural = 'Schedule Integrations'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_integration_type_display()})"
