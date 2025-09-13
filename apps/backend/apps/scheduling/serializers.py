"""
Comprehensive scheduling management serializers for iNEAT ERP platform.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

from apps.core.models import User
from apps.hr.models import Employee
from .models import (
    ScheduleTemplate, Resource, Team, TeamMember, Appointment,
    ScheduleConflict, ScheduleRule, ScheduleNotification,
    ScheduleAnalytics, ScheduleIntegration
)

User = get_user_model()


# ==================== SCHEDULE TEMPLATE SERIALIZERS ====================

class ScheduleTemplateSerializer(serializers.ModelSerializer):
    """Serializer for ScheduleTemplate."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    schedule_type_display = serializers.CharField(source='get_schedule_type_display', read_only=True)
    duration_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = ScheduleTemplate
        fields = [
            'id', 'organization', 'organization_name', 'name', 'description',
            'schedule_type', 'schedule_type_display', 'recurrence_interval',
            'recurrence_days', 'recurrence_dates', 'start_time', 'end_time',
            'duration_minutes', 'duration_hours', 'break_duration_minutes',
            'break_start_time', 'max_capacity', 'min_advance_booking_hours',
            'max_advance_booking_days', 'base_price', 'currency',
            'is_active', 'is_default', 'created_at', 'modified_at'
        ]
        read_only_fields = ['created_at', 'modified_at']
    
    def get_duration_hours(self, obj):
        """Calculate duration in hours."""
        return round(obj.duration_minutes / 60, 2)
    
    def validate(self, data):
        """Validate schedule template data."""
        if data.get('end_time') and data.get('start_time'):
            if data['end_time'] <= data['start_time']:
                raise serializers.ValidationError("End time must be after start time.")
        
        if data.get('duration_minutes', 0) <= 0:
            raise serializers.ValidationError("Duration must be positive.")
        
        return data


class ScheduleTemplateCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ScheduleTemplate."""
    
    class Meta:
        model = ScheduleTemplate
        fields = [
            'organization', 'name', 'description', 'schedule_type',
            'recurrence_interval', 'recurrence_days', 'recurrence_dates',
            'start_time', 'end_time', 'duration_minutes', 'break_duration_minutes',
            'break_start_time', 'max_capacity', 'min_advance_booking_hours',
            'max_advance_booking_days', 'base_price', 'currency',
            'is_active', 'is_default'
        ]


# ==================== RESOURCE SERIALIZERS ====================

class ResourceSerializer(serializers.ModelSerializer):
    """Serializer for Resource."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    resource_type_display = serializers.CharField(source='get_resource_type_display', read_only=True)
    is_available_display = serializers.SerializerMethodField()
    maintenance_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Resource
        fields = [
            'id', 'organization', 'organization_name', 'name', 'resource_type',
            'resource_type_display', 'description', 'location', 'capacity',
            'specifications', 'is_active', 'is_available', 'is_available_display',
            'maintenance_schedule', 'last_maintenance', 'next_maintenance',
            'maintenance_status', 'hourly_rate', 'daily_rate', 'currency',
            'image_url', 'documents', 'created_at', 'modified_at'
        ]
        read_only_fields = ['created_at', 'modified_at']
    
    def get_is_available_display(self, obj):
        """Get availability status display."""
        if not obj.is_active:
            return "Inactive"
        if not obj.is_available:
            return "Unavailable"
        return "Available"
    
    def get_maintenance_status(self, obj):
        """Get maintenance status."""
        if not obj.next_maintenance:
            return "No maintenance scheduled"
        
        now = timezone.now()
        if obj.next_maintenance <= now:
            return "Maintenance overdue"
        elif (obj.next_maintenance - now).days <= 7:
            return "Maintenance due soon"
        else:
            return "Maintenance scheduled"


class ResourceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Resource."""
    
    class Meta:
        model = Resource
        fields = [
            'organization', 'name', 'resource_type', 'description', 'location',
            'capacity', 'specifications', 'is_active', 'is_available',
            'maintenance_schedule', 'hourly_rate', 'daily_rate', 'currency',
            'image_url', 'documents'
        ]


# ==================== TEAM SERIALIZERS ====================

class TeamMemberSerializer(serializers.ModelSerializer):
    """Serializer for TeamMember."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = TeamMember
        fields = [
            'id', 'team', 'user', 'user_name', 'user_email', 'role', 'role_display',
            'joined_date', 'is_active', 'skills', 'certifications',
            'availability_schedule', 'max_hours_per_week', 'created_at', 'modified_at'
        ]
        read_only_fields = ['created_at', 'modified_at']


class TeamSerializer(serializers.ModelSerializer):
    """Serializer for Team."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    team_lead_name = serializers.CharField(source='team_lead.get_full_name', read_only=True)
    member_count = serializers.SerializerMethodField()
    active_member_count = serializers.SerializerMethodField()
    members = TeamMemberSerializer(many=True, read_only=True)
    
    class Meta:
        model = Team
        fields = [
            'id', 'organization', 'organization_name', 'name', 'description',
            'is_active', 'max_members', 'team_lead', 'team_lead_name',
            'skills', 'specializations', 'availability_schedule',
            'member_count', 'active_member_count', 'members',
            'created_at', 'modified_at'
        ]
        read_only_fields = ['created_at', 'modified_at']
    
    def get_member_count(self, obj):
        """Get total member count."""
        return obj.members.count()
    
    def get_active_member_count(self, obj):
        """Get active member count."""
        return obj.members.filter(is_active=True).count()


class TeamCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Team."""
    
    class Meta:
        model = Team
        fields = [
            'organization', 'name', 'description', 'is_active', 'max_members',
            'team_lead', 'skills', 'specializations', 'availability_schedule'
        ]


class TeamMemberCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating TeamMember."""
    
    class Meta:
        model = TeamMember
        fields = [
            'team', 'user', 'role', 'joined_date', 'is_active',
            'skills', 'certifications', 'availability_schedule', 'max_hours_per_week'
        ]


# ==================== APPOINTMENT SERIALIZERS ====================

class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for Appointment."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    duration_hours = serializers.SerializerMethodField()
    assigned_users_names = serializers.SerializerMethodField()
    required_resources_names = serializers.SerializerMethodField()
    assigned_team_name = serializers.CharField(source='assigned_team.name', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    is_upcoming = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'organization', 'organization_name', 'title', 'description',
            'start_datetime', 'end_datetime', 'duration_minutes', 'duration_hours',
            'status', 'status_display', 'priority', 'priority_display',
            'client_name', 'client_email', 'client_phone', 'client_notes',
            'assigned_team', 'assigned_team_name', 'assigned_users', 'assigned_users_names',
            'required_resources', 'required_resources_names', 'location', 'is_virtual',
            'meeting_url', 'is_recurring', 'recurrence_rule', 'parent_appointment',
            'estimated_cost', 'actual_cost', 'currency', 'is_billable',
            'reminder_sent', 'reminder_datetime', 'completion_notes',
            'completion_rating', 'completion_feedback', 'external_id', 'external_url',
            'is_overdue', 'is_upcoming', 'created_at', 'modified_at'
        ]
        read_only_fields = ['created_at', 'modified_at']
    
    def get_duration_hours(self, obj):
        """Calculate duration in hours."""
        return round(obj.duration_minutes / 60, 2)
    
    def get_assigned_users_names(self, obj):
        """Get assigned users names."""
        return [user.get_full_name() for user in obj.assigned_users.all()]
    
    def get_required_resources_names(self, obj):
        """Get required resources names."""
        return [resource.name for resource in obj.required_resources.all()]
    
    def get_is_overdue(self, obj):
        """Check if appointment is overdue."""
        now = timezone.now()
        return obj.end_datetime < now and obj.status not in ['completed', 'cancelled']
    
    def get_is_upcoming(self, obj):
        """Check if appointment is upcoming."""
        now = timezone.now()
        return obj.start_datetime > now and obj.status in ['scheduled', 'confirmed']


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Appointment."""
    
    class Meta:
        model = Appointment
        fields = [
            'organization', 'title', 'description', 'start_datetime', 'end_datetime',
            'duration_minutes', 'status', 'priority', 'client_name', 'client_email',
            'client_phone', 'client_notes', 'assigned_team', 'assigned_users',
            'required_resources', 'location', 'is_virtual', 'meeting_url',
            'is_recurring', 'recurrence_rule', 'parent_appointment',
            'estimated_cost', 'actual_cost', 'currency', 'is_billable',
            'reminder_datetime', 'external_id', 'external_url'
        ]
    
    def validate(self, data):
        """Validate appointment data."""
        if data.get('end_datetime') and data.get('start_datetime'):
            if data['end_datetime'] <= data['start_datetime']:
                raise serializers.ValidationError("End datetime must be after start datetime.")
        
        if data.get('duration_minutes', 0) <= 0:
            raise serializers.ValidationError("Duration must be positive.")
        
        return data


class AppointmentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating Appointment."""
    
    class Meta:
        model = Appointment
        fields = [
            'title', 'description', 'start_datetime', 'end_datetime',
            'duration_minutes', 'status', 'priority', 'client_name', 'client_email',
            'client_phone', 'client_notes', 'assigned_team', 'assigned_users',
            'required_resources', 'location', 'is_virtual', 'meeting_url',
            'estimated_cost', 'actual_cost', 'is_billable', 'completion_notes',
            'completion_rating', 'completion_feedback'
        ]


# ==================== SCHEDULE CONFLICT SERIALIZERS ====================

class ScheduleConflictSerializer(serializers.ModelSerializer):
    """Serializer for ScheduleConflict."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    conflict_type_display = serializers.CharField(source='get_conflict_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    impact_level_display = serializers.CharField(source='get_impact_level_display', read_only=True)
    primary_appointment_title = serializers.CharField(source='primary_appointment.title', read_only=True)
    conflicting_appointment_title = serializers.CharField(source='conflicting_appointment.title', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.get_full_name', read_only=True)
    affected_resources_names = serializers.SerializerMethodField()
    affected_users_names = serializers.SerializerMethodField()
    
    class Meta:
        model = ScheduleConflict
        fields = [
            'id', 'organization', 'organization_name', 'conflict_type', 'conflict_type_display',
            'status', 'status_display', 'primary_appointment', 'primary_appointment_title',
            'conflicting_appointment', 'conflicting_appointment_title', 'conflict_description',
            'conflict_datetime', 'affected_resources', 'affected_resources_names',
            'affected_users', 'affected_users_names', 'resolution_notes', 'resolved_by',
            'resolved_by_name', 'resolved_at', 'impact_level', 'impact_level_display',
            'created_at', 'modified_at'
        ]
        read_only_fields = ['created_at', 'modified_at']
    
    def get_affected_resources_names(self, obj):
        """Get affected resources names."""
        return [resource.name for resource in obj.affected_resources.all()]
    
    def get_affected_users_names(self, obj):
        """Get affected users names."""
        return [user.get_full_name() for user in obj.affected_users.all()]


class ScheduleConflictCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ScheduleConflict."""
    
    class Meta:
        model = ScheduleConflict
        fields = [
            'organization', 'conflict_type', 'primary_appointment', 'conflicting_appointment',
            'conflict_description', 'conflict_datetime', 'affected_resources',
            'affected_users', 'impact_level'
        ]


class ScheduleConflictResolveSerializer(serializers.ModelSerializer):
    """Serializer for resolving ScheduleConflict."""
    
    class Meta:
        model = ScheduleConflict
        fields = ['status', 'resolution_notes', 'resolved_by', 'resolved_at']


# ==================== SCHEDULE RULE SERIALIZERS ====================

class ScheduleRuleSerializer(serializers.ModelSerializer):
    """Serializer for ScheduleRule."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    rule_type_display = serializers.CharField(source='get_rule_type_display', read_only=True)
    applies_to_resources_names = serializers.SerializerMethodField()
    applies_to_users_names = serializers.SerializerMethodField()
    applies_to_teams_names = serializers.SerializerMethodField()
    
    class Meta:
        model = ScheduleRule
        fields = [
            'id', 'organization', 'organization_name', 'name', 'rule_type',
            'rule_type_display', 'description', 'is_active', 'is_global',
            'applies_to_resources', 'applies_to_resources_names',
            'applies_to_users', 'applies_to_users_names',
            'applies_to_teams', 'applies_to_teams_names',
            'start_date', 'end_date', 'start_time', 'end_time',
            'is_recurring', 'recurrence_rule', 'parameters',
            'created_at', 'modified_at'
        ]
        read_only_fields = ['created_at', 'modified_at']
    
    def get_applies_to_resources_names(self, obj):
        """Get applies to resources names."""
        return [resource.name for resource in obj.applies_to_resources.all()]
    
    def get_applies_to_users_names(self, obj):
        """Get applies to users names."""
        return [user.get_full_name() for user in obj.applies_to_users.all()]
    
    def get_applies_to_teams_names(self, obj):
        """Get applies to teams names."""
        return [team.name for team in obj.applies_to_teams.all()]


class ScheduleRuleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ScheduleRule."""
    
    class Meta:
        model = ScheduleRule
        fields = [
            'organization', 'name', 'rule_type', 'description', 'is_active',
            'is_global', 'applies_to_resources', 'applies_to_users',
            'applies_to_teams', 'start_date', 'end_date', 'start_time',
            'end_time', 'is_recurring', 'recurrence_rule', 'parameters'
        ]


# ==================== SCHEDULE NOTIFICATION SERIALIZERS ====================

class ScheduleNotificationSerializer(serializers.ModelSerializer):
    """Serializer for ScheduleNotification."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    delivery_method_display = serializers.CharField(source='get_delivery_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    recipients_names = serializers.SerializerMethodField()
    related_appointment_title = serializers.CharField(source='related_appointment.title', read_only=True)
    
    class Meta:
        model = ScheduleNotification
        fields = [
            'id', 'organization', 'organization_name', 'notification_type',
            'notification_type_display', 'delivery_method', 'delivery_method_display',
            'recipients', 'recipients_names', 'subject', 'message',
            'related_appointment', 'related_appointment_title', 'related_conflict',
            'scheduled_at', 'sent_at', 'status', 'status_display',
            'delivery_details', 'error_message', 'created_at', 'modified_at'
        ]
        read_only_fields = ['created_at', 'modified_at']
    
    def get_recipients_names(self, obj):
        """Get recipients names."""
        return [user.get_full_name() for user in obj.recipients.all()]


class ScheduleNotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ScheduleNotification."""
    
    class Meta:
        model = ScheduleNotification
        fields = [
            'organization', 'notification_type', 'delivery_method', 'recipients',
            'subject', 'message', 'related_appointment', 'related_conflict',
            'scheduled_at'
        ]


# ==================== SCHEDULE ANALYTICS SERIALIZERS ====================

class ScheduleAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for ScheduleAnalytics."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    period_type_display = serializers.CharField(source='get_period_type_display', read_only=True)
    utilization_percentage = serializers.SerializerMethodField()
    completion_rate = serializers.SerializerMethodField()
    conflict_resolution_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = ScheduleAnalytics
        fields = [
            'id', 'organization', 'organization_name', 'period_start', 'period_end',
            'period_type', 'period_type_display', 'total_appointments',
            'completed_appointments', 'cancelled_appointments', 'no_show_appointments',
            'total_scheduled_hours', 'total_available_hours', 'utilization_rate',
            'utilization_percentage', 'resource_utilization', 'team_utilization',
            'total_conflicts', 'resolved_conflicts', 'conflict_resolution_time',
            'conflict_resolution_rate', 'total_revenue', 'average_appointment_value',
            'completion_rate', 'metrics', 'created_at', 'modified_at'
        ]
        read_only_fields = ['created_at', 'modified_at']
    
    def get_utilization_percentage(self, obj):
        """Get utilization percentage."""
        return round(float(obj.utilization_rate), 2)
    
    def get_completion_rate(self, obj):
        """Get completion rate."""
        if obj.total_appointments > 0:
            return round((obj.completed_appointments / obj.total_appointments) * 100, 2)
        return 0
    
    def get_conflict_resolution_rate(self, obj):
        """Get conflict resolution rate."""
        if obj.total_conflicts > 0:
            return round((obj.resolved_conflicts / obj.total_conflicts) * 100, 2)
        return 0


class ScheduleAnalyticsCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ScheduleAnalytics."""
    
    class Meta:
        model = ScheduleAnalytics
        fields = [
            'organization', 'period_start', 'period_end', 'period_type',
            'total_appointments', 'completed_appointments', 'cancelled_appointments',
            'no_show_appointments', 'total_scheduled_hours', 'total_available_hours',
            'utilization_rate', 'resource_utilization', 'team_utilization',
            'total_conflicts', 'resolved_conflicts', 'conflict_resolution_time',
            'total_revenue', 'average_appointment_value', 'metrics'
        ]


# ==================== SCHEDULE INTEGRATION SERIALIZERS ====================

class ScheduleIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for ScheduleIntegration."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    integration_type_display = serializers.CharField(source='get_integration_type_display', read_only=True)
    sync_frequency_display = serializers.CharField(source='get_sync_frequency_display', read_only=True)
    sync_status_display = serializers.CharField(source='get_sync_status_display', read_only=True)
    is_token_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = ScheduleIntegration
        fields = [
            'id', 'organization', 'organization_name', 'name', 'integration_type',
            'integration_type_display', 'provider_name', 'provider_url',
            'is_active', 'configuration', 'sync_enabled', 'sync_frequency',
            'sync_frequency_display', 'last_sync', 'sync_status', 'sync_status_display',
            'error_message', 'retry_count', 'max_retries', 'is_token_expired',
            'created_at', 'modified_at'
        ]
        read_only_fields = ['created_at', 'modified_at']
        extra_kwargs = {
            'api_key': {'write_only': True},
            'api_secret': {'write_only': True},
            'access_token': {'write_only': True},
            'refresh_token': {'write_only': True},
        }
    
    def get_is_token_expired(self, obj):
        """Check if token is expired."""
        if not obj.token_expires_at:
            return False
        return obj.token_expires_at <= timezone.now()


class ScheduleIntegrationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ScheduleIntegration."""
    
    class Meta:
        model = ScheduleIntegration
        fields = [
            'organization', 'name', 'integration_type', 'provider_name',
            'provider_url', 'is_active', 'configuration', 'api_key',
            'api_secret', 'sync_enabled', 'sync_frequency'
        ]


class ScheduleIntegrationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating ScheduleIntegration."""
    
    class Meta:
        model = ScheduleIntegration
        fields = [
            'name', 'provider_name', 'provider_url', 'is_active',
            'configuration', 'sync_enabled', 'sync_frequency'
        ]


# ==================== DASHBOARD AND SUMMARY SERIALIZERS ====================

class SchedulingDashboardSerializer(serializers.Serializer):
    """Serializer for scheduling dashboard data."""
    total_appointments = serializers.IntegerField()
    upcoming_appointments = serializers.IntegerField()
    overdue_appointments = serializers.IntegerField()
    total_conflicts = serializers.IntegerField()
    unresolved_conflicts = serializers.IntegerField()
    total_resources = serializers.IntegerField()
    available_resources = serializers.IntegerField()
    total_teams = serializers.IntegerField()
    active_teams = serializers.IntegerField()
    utilization_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    completion_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    recent_appointments = AppointmentSerializer(many=True)
    recent_conflicts = ScheduleConflictSerializer(many=True)
    upcoming_appointments_list = AppointmentSerializer(many=True)


class SchedulingSummarySerializer(serializers.Serializer):
    """Serializer for scheduling summary data."""
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    total_appointments = serializers.IntegerField()
    completed_appointments = serializers.IntegerField()
    cancelled_appointments = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_appointment_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    utilization_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    conflict_count = serializers.IntegerField()
    resolution_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
