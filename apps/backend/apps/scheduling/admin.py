"""
Comprehensive scheduling management admin configuration.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum, Avg
from django.utils import timezone

from .models import (
    ScheduleTemplate, Resource, Team, TeamMember, Appointment,
    ScheduleConflict, ScheduleRule, ScheduleNotification,
    ScheduleAnalytics, ScheduleIntegration
)


# ==================== SCHEDULE TEMPLATE ADMIN ====================

@admin.register(ScheduleTemplate)
class ScheduleTemplateAdmin(admin.ModelAdmin):
    """Admin for ScheduleTemplate."""
    list_display = [
        'name', 'schedule_type', 'start_time', 'end_time',
        'duration_minutes', 'max_capacity', 'base_price', 'is_active', 'is_default'
    ]
    list_filter = [
        'schedule_type', 'is_active', 'is_default', 'currency', 'created'
    ]
    search_fields = ['name', 'description', 'name']
    readonly_fields = ['created', 'modified']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'schedule_type')
        }),
        ('Schedule Settings', {
            'fields': (
                'recurrence_interval', 'recurrence_days', 'recurrence_dates',
                'start_time', 'end_time', 'duration_minutes'
            )
        }),
        ('Break Settings', {
            'fields': ('break_duration_minutes', 'break_start_time')
        }),
        ('Capacity and Booking', {
            'fields': (
                'max_capacity', 'min_advance_booking_hours', 'max_advance_booking_days'
            )
        }),
        ('Pricing', {
            'fields': ('base_price', 'currency')
        }),
        ('Status', {
            'fields': ('is_active', 'is_default')
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )


# ==================== RESOURCE ADMIN ====================

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    """Admin for Resource."""
    list_display = [
        'name', 'resource_type', 'location', 'capacity',
        'is_active', 'is_available', 'hourly_rate', 'daily_rate'
    ]
    list_filter = [
        'resource_type', 'is_active', 'is_available', 'currency', 'created'
    ]
    search_fields = ['name', 'description', 'location', 'name']
    readonly_fields = ['created', 'modified']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'resource_type', 'description', 'location')
        }),
        ('Capacity and Specifications', {
            'fields': ('capacity', 'specifications')
        }),
        ('Availability', {
            'fields': ('is_active', 'is_available')
        }),
        ('Maintenance', {
            'fields': (
                'maintenance_schedule', 'last_maintenance', 'next_maintenance'
            )
        }),
        ('Pricing', {
            'fields': ('hourly_rate', 'daily_rate', 'currency')
        }),
        ('Media', {
            'fields': ('image_url', 'documents')
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )


# ==================== TEAM ADMIN ====================

class TeamMemberInline(admin.TabularInline):
    """Inline admin for TeamMember."""
    model = TeamMember
    extra = 0
    readonly_fields = ['created', 'modified']
    fields = [
        'user', 'role', 'joined_date', 'is_active', 'skills', 'certifications',
        'max_hours_per_week'
    ]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin for Team."""
    list_display = [
        'name', 'team_lead', 'member_count', 'is_active', 'created'
    ]
    list_filter = [
        'is_active', 'created'
    ]
    search_fields = ['name', 'description', 'name', 'team_lead__first_name']
    readonly_fields = ['created', 'modified', 'member_count']
    inlines = [TeamMemberInline]
    
    def member_count(self, obj):
        """Get member count."""
        return obj.members.count()
    member_count.short_description = 'Members'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Team Settings', {
            'fields': ('is_active', 'max_members', 'team_lead')
        }),
        ('Skills and Specializations', {
            'fields': ('skills', 'specializations')
        }),
        ('Availability', {
            'fields': ('availability_schedule',)
        }),
        ('Statistics', {
            'fields': ('member_count',)
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    """Admin for TeamMember."""
    list_display = [
        'user', 'team', 'role', 'joined_date', 'is_active', 'max_hours_per_week'
    ]
    list_filter = [
        'role', 'is_active', 'joined_date', 'created'
    ]
    search_fields = [
        'user__first_name', 'user__last_name', 'teamname', 'team__name'
    ]
    readonly_fields = ['created', 'modified']
    
    fieldsets = (
        ('Membership', {
            'fields': ('team', 'user', 'role', 'joined_date', 'is_active')
        }),
        ('Skills and Certifications', {
            'fields': ('skills', 'certifications')
        }),
        ('Availability', {
            'fields': ('availability_schedule', 'max_hours_per_week')
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )


# ==================== APPOINTMENT ADMIN ====================

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Admin for Appointment."""
    list_display = [
        'title', 'start_datetime', 'end_datetime', 'status',
        'priority', 'client_name', 'assigned_team', 'estimated_cost'
    ]
    list_filter = [
        'status', 'priority', 'is_virtual', 'is_recurring', 'is_billable',
        'start_datetime', 'created'
    ]
    search_fields = [
        'title', 'description', 'client_name', 'client_email', 'name'
    ]
    readonly_fields = [
        'created', 'modified', 'is_overdue', 'is_upcoming'
    ]
    filter_horizontal = ['assigned_users', 'required_resources']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description')
        }),
        ('Scheduling', {
            'fields': ('start_datetime', 'end_datetime', 'duration_minutes')
        }),
        ('Status and Priority', {
            'fields': ('status', 'priority')
        }),
        ('Client Information', {
            'fields': ('client_name', 'client_email', 'client_phone', 'client_notes')
        }),
        ('Assignment', {
            'fields': ('assigned_team', 'assigned_users', 'required_resources')
        }),
        ('Location', {
            'fields': ('location', 'is_virtual', 'meeting_url')
        }),
        ('Recurrence', {
            'fields': ('is_recurring', 'recurrence_rule', 'parent_appointment')
        }),
        ('Pricing and Billing', {
            'fields': ('estimated_cost', 'actual_cost', 'currency', 'is_billable')
        }),
        ('Reminders', {
            'fields': ('reminder_sent', 'reminder_datetime')
        }),
        ('Completion', {
            'fields': (
                'completion_notes', 'completion_rating', 'completion_feedback'
            )
        }),
        ('External References', {
            'fields': ('external_id', 'external_url')
        }),
        ('Status Indicators', {
            'fields': ('is_overdue', 'is_upcoming')
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )
    
    def is_overdue(self, obj):
        """Check if appointment is overdue."""
        now = timezone.now()
        return obj.end_datetime < now and obj.status not in ['completed', 'cancelled']
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue'
    
    def is_upcoming(self, obj):
        """Check if appointment is upcoming."""
        now = timezone.now()
        return obj.start_datetime > now and obj.status in ['scheduled', 'confirmed']
    is_upcoming.boolean = True
    is_upcoming.short_description = 'Upcoming'


# ==================== SCHEDULE CONFLICT ADMIN ====================

@admin.register(ScheduleConflict)
class ScheduleConflictAdmin(admin.ModelAdmin):
    """Admin for ScheduleConflict."""
    list_display = [
        'conflict_type', 'primary_appointment', 'conflicting_appointment',
        'status', 'impact_level', 'conflict_datetime', 'resolved_by', 'resolved_at'
    ]
    list_filter = [
        'conflict_type', 'status', 'impact_level', 'conflict_datetime', 'resolved_at'
    ]
    search_fields = [
        'conflict_description', 'primary_appointment__title', 'conflicting_appointment__title',
        'name'
    ]
    readonly_fields = ['created', 'modified']
    filter_horizontal = ['affected_resources', 'affected_users']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('conflict_type', 'status', 'impact_level')
        }),
        ('Conflicting Appointments', {
            'fields': ('primary_appointment', 'conflicting_appointment')
        }),
        ('Conflict Details', {
            'fields': ('conflict_description', 'conflict_datetime')
        }),
        ('Affected Resources and Users', {
            'fields': ('affected_resources', 'affected_users')
        }),
        ('Resolution', {
            'fields': ('resolution_notes', 'resolved_by', 'resolved_at')
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )


# ==================== SCHEDULE RULE ADMIN ====================

@admin.register(ScheduleRule)
class ScheduleRuleAdmin(admin.ModelAdmin):
    """Admin for ScheduleRule."""
    list_display = [
        'name', 'rule_type', 'is_active', 'is_global',
        'start_date', 'end_date', 'start_time', 'end_time'
    ]
    list_filter = [
        'rule_type', 'is_active', 'is_global', 'is_recurring', 'start_date', 'end_date'
    ]
    search_fields = ['name', 'description', 'name']
    readonly_fields = ['created', 'modified']
    filter_horizontal = ['applies_to_resources', 'applies_to_users', 'applies_to_teams']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'rule_type', 'description')
        }),
        ('Rule Settings', {
            'fields': ('is_active', 'is_global')
        }),
        ('Scope', {
            'fields': ('applies_to_resources', 'applies_to_users', 'applies_to_teams')
        }),
        ('Time Settings', {
            'fields': ('start_date', 'end_date', 'start_time', 'end_time')
        }),
        ('Recurrence', {
            'fields': ('is_recurring', 'recurrence_rule')
        }),
        ('Parameters', {
            'fields': ('parameters',)
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )


# ==================== SCHEDULE NOTIFICATION ADMIN ====================

@admin.register(ScheduleNotification)
class ScheduleNotificationAdmin(admin.ModelAdmin):
    """Admin for ScheduleNotification."""
    list_display = [
        'notification_type', 'subject', 'delivery_method',
        'status', 'scheduled_at', 'sent_at', 'created'
    ]
    list_filter = [
        'notification_type', 'delivery_method', 'status', 'scheduled_at', 'sent_at'
    ]
    search_fields = [
        'subject', 'message', 'name'
    ]
    readonly_fields = ['created', 'modified', 'sent_at']
    filter_horizontal = ['recipients']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('notification_type', 'delivery_method', 'status')
        }),
        ('Content', {
            'fields': ('subject', 'message')
        }),
        ('Recipients', {
            'fields': ('recipients',)
        }),
        ('Related Objects', {
            'fields': ('related_appointment', 'related_conflict')
        }),
        ('Delivery', {
            'fields': ('scheduled_at', 'sent_at', 'delivery_details', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )


# ==================== SCHEDULE ANALYTICS ADMIN ====================

@admin.register(ScheduleAnalytics)
class ScheduleAnalyticsAdmin(admin.ModelAdmin):
    """Admin for ScheduleAnalytics."""
    list_display = [
        'period_start', 'period_end', 'period_type',
        'total_appointments', 'completed_appointments', 'utilization_rate',
        'total_revenue', 'total_conflicts'
    ]
    list_filter = [
        'period_type', 'period_start', 'period_end', 'created'
    ]
    search_fields = ['name']
    readonly_fields = [
        'created', 'modified', 'total_appointments', 'completed_appointments',
        'cancelled_appointments', 'no_show_appointments', 'total_scheduled_hours',
        'total_available_hours', 'utilization_rate', 'resource_utilization',
        'team_utilization', 'total_conflicts', 'resolved_conflicts',
        'conflict_resolution_time', 'total_revenue', 'average_appointment_value'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('period_start', 'period_end', 'period_type')
        }),
        ('Appointment Statistics', {
            'fields': (
                'total_appointments', 'completed_appointments', 'cancelled_appointments',
                'no_show_appointments'
            )
        }),
        ('Utilization Metrics', {
            'fields': (
                'total_scheduled_hours', 'total_available_hours', 'utilization_rate',
                'resource_utilization', 'team_utilization'
            )
        }),
        ('Conflict Metrics', {
            'fields': (
                'total_conflicts', 'resolved_conflicts', 'conflict_resolution_time'
            )
        }),
        ('Revenue Metrics', {
            'fields': ('total_revenue', 'average_appointment_value')
        }),
        ('Additional Metrics', {
            'fields': ('metrics',)
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )


# ==================== SCHEDULE INTEGRATION ADMIN ====================

@admin.register(ScheduleIntegration)
class ScheduleIntegrationAdmin(admin.ModelAdmin):
    """Admin for ScheduleIntegration."""
    list_display = [
        'name', 'integration_type', 'provider_name',
        'is_active', 'sync_enabled', 'sync_status', 'last_sync'
    ]
    list_filter = [
        'integration_type', 'is_active', 'sync_enabled', 'sync_frequency',
        'sync_status', 'last_sync', 'created'
    ]
    search_fields = [
        'name', 'provider_name', 'name'
    ]
    readonly_fields = [
        'created', 'modified', 'last_sync', 'token_expires_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'integration_type', 'provider_name', 'provider_url')
        }),
        ('Configuration', {
            'fields': ('is_active', 'configuration')
        }),
        ('Authentication', {
            'fields': (
                'api_key', 'api_secret', 'access_token', 'refresh_token', 'token_expires_at'
            ),
            'classes': ('collapse',)
        }),
        ('Sync Settings', {
            'fields': ('sync_enabled', 'sync_frequency', 'last_sync', 'sync_status')
        }),
        ('Error Handling', {
            'fields': ('error_message', 'retry_count', 'max_retries')
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )


# ==================== ADMIN CUSTOMIZATIONS ====================

# Customize admin site
admin.site.site_header = "TidyGen ERP - Scheduling Management"
admin.site.site_title = "Scheduling Admin"
admin.site.index_title = "Scheduling Management System"

# Add custom admin actions
def activate_schedule_templates(modeladmin, request, queryset):
    """Activate selected schedule templates."""
    updated = queryset.update(is_active=True)
    modeladmin.message_user(request, f"{updated} schedule templates activated.")

def deactivate_schedule_templates(modeladmin, request, queryset):
    """Deactivate selected schedule templates."""
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f"{updated} schedule templates deactivated.")

def activate_resources(modeladmin, request, queryset):
    """Activate selected resources."""
    updated = queryset.update(is_active=True, is_available=True)
    modeladmin.message_user(request, f"{updated} resources activated.")

def deactivate_resources(modeladmin, request, queryset):
    """Deactivate selected resources."""
    updated = queryset.update(is_active=False, is_available=False)
    modeladmin.message_user(request, f"{updated} resources deactivated.")

def confirm_appointments(modeladmin, request, queryset):
    """Confirm selected appointments."""
    updated = queryset.filter(status='scheduled').update(status='confirmed')
    modeladmin.message_user(request, f"{updated} appointments confirmed.")

def cancel_appointments(modeladmin, request, queryset):
    """Cancel selected appointments."""
    updated = queryset.filter(status__in=['scheduled', 'confirmed']).update(status='cancelled')
    modeladmin.message_user(request, f"{updated} appointments cancelled.")

def resolve_conflicts(modeladmin, request, queryset):
    """Resolve selected conflicts."""
    from django.utils import timezone
    updated = queryset.filter(status='pending').update(
        status='resolved',
        resolved_by=request.user,
        resolved_at=timezone.now()
    )
    modeladmin.message_user(request, f"{updated} conflicts resolved.")

def send_notifications(modeladmin, request, queryset):
    """Send selected notifications."""
    from django.utils import timezone
    updated = queryset.filter(status='pending').update(
        status='sent',
        sent_at=timezone.now()
    )
    modeladmin.message_user(request, f"{updated} notifications sent.")

# Add actions to respective admins
ScheduleTemplateAdmin.actions = [activate_schedule_templates, deactivate_schedule_templates]
ResourceAdmin.actions = [activate_resources, deactivate_resources]
AppointmentAdmin.actions = [confirm_appointments, cancel_appointments]
ScheduleConflictAdmin.actions = [resolve_conflicts]
ScheduleNotificationAdmin.actions = [send_notifications]
