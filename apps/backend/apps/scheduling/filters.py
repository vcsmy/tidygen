"""
Comprehensive scheduling management filters for TidyGen ERP platform.
"""
import django_filters
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, date

from .models import (
    ScheduleTemplate, Resource, Team, TeamMember, Appointment,
    ScheduleConflict, ScheduleRule, ScheduleNotification,
    ScheduleAnalytics, ScheduleIntegration
)


# ==================== SCHEDULE TEMPLATE FILTERS ====================

class ScheduleTemplateFilter(django_filters.FilterSet):
    """Filter for ScheduleTemplate."""
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    schedule_type = django_filters.ChoiceFilter(choices=ScheduleTemplate.SCHEDULE_TYPES)
    is_active = django_filters.BooleanFilter()
    is_default = django_filters.BooleanFilter()
    
    # Date range filters
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    
    # Time range filters
    start_time_after = django_filters.TimeFilter(field_name='start_time', lookup_expr='gte')
    start_time_before = django_filters.TimeFilter(field_name='start_time', lookup_expr='lte')
    end_time_after = django_filters.TimeFilter(field_name='end_time', lookup_expr='gte')
    end_time_before = django_filters.TimeFilter(field_name='end_time', lookup_expr='lte')
    
    # Duration filters
    duration_min = django_filters.NumberFilter(field_name='duration_minutes', lookup_expr='gte')
    duration_max = django_filters.NumberFilter(field_name='duration_minutes', lookup_expr='lte')
    
    # Capacity filters
    capacity_min = django_filters.NumberFilter(field_name='max_capacity', lookup_expr='gte')
    capacity_max = django_filters.NumberFilter(field_name='max_capacity', lookup_expr='lte')
    
    # Price filters
    price_min = django_filters.NumberFilter(field_name='base_price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='base_price', lookup_expr='lte')
    currency = django_filters.CharFilter(lookup_expr='iexact')
    
    class Meta:
        model = ScheduleTemplate
        fields = [
            'name', 'description', 'schedule_type', 'is_active', 'is_default',
            'created_after', 'created_before', 'start_time_after', 'start_time_before',
            'end_time_after', 'end_time_before', 'duration_min', 'duration_max',
            'capacity_min', 'capacity_max', 'price_min', 'price_max', 'currency'
        ]


# ==================== RESOURCE FILTERS ====================

class ResourceFilter(django_filters.FilterSet):
    """Filter for Resource."""
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    resource_type = django_filters.ChoiceFilter(choices=Resource.RESOURCE_TYPES)
    location = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    is_available = django_filters.BooleanFilter()
    
    # Date range filters
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    
    # Capacity filters
    capacity_min = django_filters.NumberFilter(field_name='capacity', lookup_expr='gte')
    capacity_max = django_filters.NumberFilter(field_name='capacity', lookup_expr='lte')
    
    # Rate filters
    hourly_rate_min = django_filters.NumberFilter(field_name='hourly_rate', lookup_expr='gte')
    hourly_rate_max = django_filters.NumberFilter(field_name='hourly_rate', lookup_expr='lte')
    daily_rate_min = django_filters.NumberFilter(field_name='daily_rate', lookup_expr='gte')
    daily_rate_max = django_filters.NumberFilter(field_name='daily_rate', lookup_expr='lte')
    currency = django_filters.CharFilter(lookup_expr='iexact')
    
    class Meta:
        model = Resource
        fields = [
            'name', 'description', 'resource_type', 'location', 'is_active', 'is_available',
            'created_after', 'created_before', 'capacity_min', 'capacity_max',
            'hourly_rate_min', 'hourly_rate_max', 'daily_rate_min', 'daily_rate_max',
            'currency'
        ]


# ==================== TEAM FILTERS ====================

class TeamFilter(django_filters.FilterSet):
    """Filter for Team."""
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    
    # Date range filters
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    
    # Team lead filter
    team_lead = django_filters.NumberFilter(field_name='team_lead__id')
    team_lead_name = django_filters.CharFilter(field_name='team_lead__first_name', lookup_expr='icontains')
    
    class Meta:
        model = Team
        fields = [
            'name', 'description', 'is_active', 'created_after', 'created_before',
            'team_lead', 'team_lead_name'
        ]


# ==================== APPOINTMENT FILTERS ====================

class AppointmentFilter(django_filters.FilterSet):
    """Filter for Appointment."""
    title = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.ChoiceFilter(choices=Appointment.STATUS_CHOICES)
    priority = django_filters.ChoiceFilter(choices=Appointment.PRIORITY_CHOICES)
    
    # Client filters
    client_name = django_filters.CharFilter(lookup_expr='icontains')
    client_email = django_filters.CharFilter(lookup_expr='icontains')
    client_phone = django_filters.CharFilter(lookup_expr='icontains')
    
    # Date range filters
    start_date_after = django_filters.DateTimeFilter(field_name='start_datetime', lookup_expr='gte')
    start_date_before = django_filters.DateTimeFilter(field_name='start_datetime', lookup_expr='lte')
    end_date_after = django_filters.DateTimeFilter(field_name='end_datetime', lookup_expr='gte')
    end_date_before = django_filters.DateTimeFilter(field_name='end_datetime', lookup_expr='lte')
    
    # Date filters
    start_date = django_filters.DateFilter(field_name='start_datetime', lookup_expr='date')
    end_date = django_filters.DateFilter(field_name='end_datetime', lookup_expr='date')
    
    # Duration filters
    duration_min = django_filters.NumberFilter(field_name='duration_minutes', lookup_expr='gte')
    duration_max = django_filters.NumberFilter(field_name='duration_minutes', lookup_expr='lte')
    
    # Assignment filters
    assigned_team = django_filters.NumberFilter(field_name='assigned_team__id')
    assigned_team_name = django_filters.CharFilter(field_name='assigned_team__name', lookup_expr='icontains')
    assigned_user = django_filters.NumberFilter(field_name='assigned_users__id')
    assigned_user_name = django_filters.CharFilter(field_name='assigned_users__first_name', lookup_expr='icontains')
    required_resource = django_filters.NumberFilter(field_name='required_resources__id')
    required_resource_name = django_filters.CharFilter(field_name='required_resources__name', lookup_expr='icontains')
    
    # Location filters
    location = django_filters.CharFilter(lookup_expr='icontains')
    is_virtual = django_filters.BooleanFilter()
    
    # Recurrence filters
    is_recurring = django_filters.BooleanFilter()
    parent_appointment = django_filters.NumberFilter(field_name='parent_appointment__id')
    
    # Cost filters
    estimated_cost_min = django_filters.NumberFilter(field_name='estimated_cost', lookup_expr='gte')
    estimated_cost_max = django_filters.NumberFilter(field_name='estimated_cost', lookup_expr='lte')
    actual_cost_min = django_filters.NumberFilter(field_name='actual_cost', lookup_expr='gte')
    actual_cost_max = django_filters.NumberFilter(field_name='actual_cost', lookup_expr='lte')
    currency = django_filters.CharFilter(lookup_expr='iexact')
    is_billable = django_filters.BooleanFilter()
    
    # Completion filters
    completion_rating_min = django_filters.NumberFilter(field_name='completion_rating', lookup_expr='gte')
    completion_rating_max = django_filters.NumberFilter(field_name='completion_rating', lookup_expr='lte')
    
    class Meta:
        model = Appointment
        fields = [
            'title', 'description', 'status', 'priority', 'client_name', 'client_email',
            'client_phone', 'start_date_after', 'start_date_before', 'end_date_after',
            'end_date_before', 'start_date', 'end_date', 'duration_min', 'duration_max',
            'assigned_team', 'assigned_team_name', 'assigned_user', 'assigned_user_name',
            'required_resource', 'required_resource_name', 'location', 'is_virtual',
            'is_recurring', 'parent_appointment', 'estimated_cost_min', 'estimated_cost_max',
            'actual_cost_min', 'actual_cost_max', 'currency', 'is_billable',
            'completion_rating_min', 'completion_rating_max'
        ]


# ==================== SCHEDULE CONFLICT FILTERS ====================

class ScheduleConflictFilter(django_filters.FilterSet):
    """Filter for ScheduleConflict."""
    conflict_type = django_filters.ChoiceFilter(choices=ScheduleConflict.CONFLICT_TYPES)
    status = django_filters.ChoiceFilter(choices=ScheduleConflict.RESOLUTION_STATUS)
    impact_level = django_filters.ChoiceFilter(choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ])
    
    # Date range filters
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    conflict_date_after = django_filters.DateTimeFilter(field_name='conflict_datetime', lookup_expr='gte')
    conflict_date_before = django_filters.DateTimeFilter(field_name='conflict_datetime', lookup_expr='lte')
    resolved_after = django_filters.DateTimeFilter(field_name='resolved_at', lookup_expr='gte')
    resolved_before = django_filters.DateTimeFilter(field_name='resolved_at', lookup_expr='lte')
    
    # Appointment filters
    primary_appointment = django_filters.NumberFilter(field_name='primary_appointment__id')
    primary_appointment_title = django_filters.CharFilter(field_name='primary_appointment__title', lookup_expr='icontains')
    conflicting_appointment = django_filters.NumberFilter(field_name='conflicting_appointment__id')
    conflicting_appointment_title = django_filters.CharFilter(field_name='conflicting_appointment__title', lookup_expr='icontains')
    
    # Resolution filters
    resolved_by = django_filters.NumberFilter(field_name='resolved_by__id')
    resolved_by_name = django_filters.CharFilter(field_name='resolved_by__first_name', lookup_expr='icontains')
    
    class Meta:
        model = ScheduleConflict
        fields = [
            'conflict_type', 'status', 'impact_level', 'created_after', 'created_before',
            'conflict_date_after', 'conflict_date_before', 'resolved_after', 'resolved_before',
            'primary_appointment', 'primary_appointment_title', 'conflicting_appointment',
            'conflicting_appointment_title', 'resolved_by', 'resolved_by_name'
        ]


# ==================== SCHEDULE RULE FILTERS ====================

class ScheduleRuleFilter(django_filters.FilterSet):
    """Filter for ScheduleRule."""
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    rule_type = django_filters.ChoiceFilter(choices=ScheduleRule.RULE_TYPES)
    is_active = django_filters.BooleanFilter()
    is_global = django_filters.BooleanFilter()
    is_recurring = django_filters.BooleanFilter()
    
    # Date range filters
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    start_date_after = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_before = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')
    end_date_after = django_filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_date_before = django_filters.DateFilter(field_name='end_date', lookup_expr='lte')
    
    # Time filters
    start_time_after = django_filters.TimeFilter(field_name='start_time', lookup_expr='gte')
    start_time_before = django_filters.TimeFilter(field_name='start_time', lookup_expr='lte')
    end_time_after = django_filters.TimeFilter(field_name='end_time', lookup_expr='gte')
    end_time_before = django_filters.TimeFilter(field_name='end_time', lookup_expr='lte')
    
    class Meta:
        model = ScheduleRule
        fields = [
            'name', 'description', 'rule_type', 'is_active', 'is_global', 'is_recurring',
            'created_after', 'created_before', 'start_date_after', 'start_date_before',
            'end_date_after', 'end_date_before', 'start_time_after', 'start_time_before',
            'end_time_after', 'end_time_before'
        ]


# ==================== SCHEDULE NOTIFICATION FILTERS ====================

class ScheduleNotificationFilter(django_filters.FilterSet):
    """Filter for ScheduleNotification."""
    notification_type = django_filters.ChoiceFilter(choices=ScheduleNotification.NOTIFICATION_TYPES)
    delivery_method = django_filters.ChoiceFilter(choices=ScheduleNotification.DELIVERY_METHODS)
    status = django_filters.ChoiceFilter(choices=[
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ])
    
    # Content filters
    subject = django_filters.CharFilter(lookup_expr='icontains')
    message = django_filters.CharFilter(lookup_expr='icontains')
    
    # Date range filters
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    scheduled_after = django_filters.DateTimeFilter(field_name='scheduled_at', lookup_expr='gte')
    scheduled_before = django_filters.DateTimeFilter(field_name='scheduled_at', lookup_expr='lte')
    sent_after = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    sent_before = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')
    
    # Recipient filters
    recipient = django_filters.NumberFilter(field_name='recipients__id')
    recipient_name = django_filters.CharFilter(field_name='recipients__first_name', lookup_expr='icontains')
    
    # Related object filters
    related_appointment = django_filters.NumberFilter(field_name='related_appointment__id')
    related_conflict = django_filters.NumberFilter(field_name='related_conflict__id')
    
    class Meta:
        model = ScheduleNotification
        fields = [
            'notification_type', 'delivery_method', 'status', 'subject', 'message',
            'created_after', 'created_before', 'scheduled_after', 'scheduled_before',
            'sent_after', 'sent_before', 'recipient', 'recipient_name',
            'related_appointment', 'related_conflict'
        ]


# ==================== SCHEDULE ANALYTICS FILTERS ====================

class ScheduleAnalyticsFilter(django_filters.FilterSet):
    """Filter for ScheduleAnalytics."""
    period_type = django_filters.ChoiceFilter(choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ])
    
    # Date range filters
    period_start_after = django_filters.DateFilter(field_name='period_start', lookup_expr='gte')
    period_start_before = django_filters.DateFilter(field_name='period_start', lookup_expr='lte')
    period_end_after = django_filters.DateFilter(field_name='period_end', lookup_expr='gte')
    period_end_before = django_filters.DateFilter(field_name='period_end', lookup_expr='lte')
    
    # Appointment count filters
    total_appointments_min = django_filters.NumberFilter(field_name='total_appointments', lookup_expr='gte')
    total_appointments_max = django_filters.NumberFilter(field_name='total_appointments', lookup_expr='lte')
    completed_appointments_min = django_filters.NumberFilter(field_name='completed_appointments', lookup_expr='gte')
    completed_appointments_max = django_filters.NumberFilter(field_name='completed_appointments', lookup_expr='lte')
    
    # Utilization filters
    utilization_rate_min = django_filters.NumberFilter(field_name='utilization_rate', lookup_expr='gte')
    utilization_rate_max = django_filters.NumberFilter(field_name='utilization_rate', lookup_expr='lte')
    
    # Revenue filters
    total_revenue_min = django_filters.NumberFilter(field_name='total_revenue', lookup_expr='gte')
    total_revenue_max = django_filters.NumberFilter(field_name='total_revenue', lookup_expr='lte')
    average_appointment_value_min = django_filters.NumberFilter(field_name='average_appointment_value', lookup_expr='gte')
    average_appointment_value_max = django_filters.NumberFilter(field_name='average_appointment_value', lookup_expr='lte')
    
    class Meta:
        model = ScheduleAnalytics
        fields = [
            'period_type', 'period_start_after', 'period_start_before',
            'period_end_after', 'period_end_before', 'total_appointments_min',
            'total_appointments_max', 'completed_appointments_min', 'completed_appointments_max',
            'utilization_rate_min', 'utilization_rate_max', 'total_revenue_min',
            'total_revenue_max', 'average_appointment_value_min', 'average_appointment_value_max'
        ]


# ==================== SCHEDULE INTEGRATION FILTERS ====================

class ScheduleIntegrationFilter(django_filters.FilterSet):
    """Filter for ScheduleIntegration."""
    name = django_filters.CharFilter(lookup_expr='icontains')
    integration_type = django_filters.ChoiceFilter(choices=ScheduleIntegration.INTEGRATION_TYPES)
    provider_name = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    sync_enabled = django_filters.BooleanFilter()
    
    # Date range filters
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    last_sync_after = django_filters.DateTimeFilter(field_name='last_sync', lookup_expr='gte')
    last_sync_before = django_filters.DateTimeFilter(field_name='last_sync', lookup_expr='lte')
    
    # Sync filters
    sync_frequency = django_filters.ChoiceFilter(choices=[
        ('realtime', 'Real-time'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ])
    sync_status = django_filters.ChoiceFilter(choices=[
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('error', 'Error'),
        ('syncing', 'Syncing'),
    ])
    
    class Meta:
        model = ScheduleIntegration
        fields = [
            'name', 'integration_type', 'provider_name', 'is_active', 'sync_enabled',
            'created_after', 'created_before', 'last_sync_after', 'last_sync_before',
            'sync_frequency', 'sync_status'
        ]
