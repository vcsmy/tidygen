"""
Admin configuration for Field Operations models.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    FieldTeam, TeamMember, ServiceRoute, RouteStop, 
    FieldJob, JobEquipment, DispatchLog
)


@admin.register(FieldTeam)
class FieldTeamAdmin(admin.ModelAdmin):
    """Admin for field teams."""
    list_display = [
        'name', 'team_type', 'status', 'current_capacity', 
        'max_capacity', 'assigned_vehicle', 'total_jobs_completed', 'average_rating'
    ]
    list_filter = [
        'team_type', 'status', 'home_base', 'assigned_vehicle'
    ]
    search_fields = [
        'name', 'description'
    ]
    readonly_fields = ['created', 'modified']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'team_type', 'status', 'description')
        }),
        ('Capacity', {
            'fields': ('max_capacity', 'current_capacity')
        }),
        ('Assignment', {
            'fields': ('assigned_vehicle', 'home_base', 'current_location')
        }),
        ('Performance Metrics', {
            'fields': ('total_jobs_completed', 'average_rating', 'on_time_percentage')
        }),
        ('Web3 Integration', {
            'fields': ('blockchain_address', 'nft_token_id'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )
    ordering = ['name']


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    """Admin for team members."""
    list_display = [
        'employee', 'team', 'role', 'is_team_leader', 
        'is_active', 'individual_rating', 'jobs_completed'
    ]
    list_filter = [
        'role', 'is_team_leader', 'is_active', 'team', 'assigned_date'
    ]
    search_fields = [
        'employee__first_name', 'employee__last_name', 'team__name'
    ]
    readonly_fields = ['created', 'modified']
    fieldsets = (
        ('Basic Information', {
            'fields': ('employee', 'team', 'role', 'is_team_leader', 'is_active')
        }),
        ('Assignment Details', {
            'fields': ('assigned_date',)
        }),
        ('Performance', {
            'fields': ('individual_rating', 'jobs_completed')
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )
    ordering = ['team', 'role']


@admin.register(ServiceRoute)
class ServiceRouteAdmin(admin.ModelAdmin):
    """Admin for service routes."""
    list_display = [
        'name', 'route_type', 'status', 'scheduled_date', 
        'assigned_team', 'total_stops', 'completed_stops', 'efficiency_rating'
    ]
    list_filter = [
        'route_type', 'status', 'scheduled_date', 'assigned_team'
    ]
    search_fields = [
        'name', 'description'
    ]
    readonly_fields = ['created', 'modified']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'route_type', 'status', 'description')
        }),
        ('Route Details', {
            'fields': ('total_distance', 'estimated_duration', 'actual_duration')
        }),
        ('Scheduling', {
            'fields': ('scheduled_date', 'start_time', 'end_time')
        }),
        ('Assignment', {
            'fields': ('assigned_team',)
        }),
        ('Performance Metrics', {
            'fields': ('total_stops', 'completed_stops', 'efficiency_rating')
        }),
        ('Web3 Integration', {
            'fields': ('blockchain_transaction_hash',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )
    ordering = ['-scheduled_date', 'name']


@admin.register(RouteStop)
class RouteStopAdmin(admin.ModelAdmin):
    """Admin for route stops."""
    list_display = [
        'route', 'sequence_number', 'stop_type', 'status', 
        'client', 'estimated_arrival', 'actual_arrival'
    ]
    list_filter = [
        'stop_type', 'status', 'route', 'estimated_arrival'
    ]
    search_fields = [
        'address', 'client__name', 'route__name'
    ]
    readonly_fields = ['created', 'modified']
    fieldsets = (
        ('Basic Information', {
            'fields': ('route', 'sequence_number', 'stop_type', 'status')
        }),
        ('Location', {
            'fields': ('client', 'address', 'latitude', 'longitude')
        }),
        ('Timing', {
            'fields': (
                'estimated_arrival', 'actual_arrival', 
                'estimated_departure', 'actual_departure',
                'estimated_duration', 'actual_duration'
            )
        }),
        ('Service Details', {
            'fields': ('service_notes', 'completion_notes')
        }),
        ('Web3 Integration', {
            'fields': ('blockchain_transaction_hash',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )
    ordering = ['route', 'sequence_number']


@admin.register(FieldJob)
class FieldJobAdmin(admin.ModelAdmin):
    """Admin for field jobs."""
    list_display = [
        'job_number', 'title', 'job_type', 'priority', 'status', 
        'client', 'scheduled_date', 'assigned_team', 'payment_released'
    ]
    list_filter = [
        'job_type', 'priority', 'status', 'scheduled_date', 'assigned_team'
    ]
    search_fields = [
        'job_number', 'title', 'client__name', 'service_address'
    ]
    readonly_fields = ['created', 'modified']
    fieldsets = (
        ('Basic Information', {
            'fields': ('job_number', 'title', 'job_type', 'priority', 'status')
        }),
        ('Job Details', {
            'fields': ('description', 'special_instructions')
        }),
        ('Client Information', {
            'fields': ('client', 'contact_person', 'contact_phone')
        }),
        ('Location', {
            'fields': ('service_address', 'latitude', 'longitude')
        }),
        ('Scheduling', {
            'fields': (
                'scheduled_date', 'scheduled_start_time', 'scheduled_end_time',
                'estimated_duration', 'actual_duration'
            )
        }),
        ('Assignment', {
            'fields': ('assigned_team', 'assigned_route')
        }),
        ('Financial Information', {
            'fields': ('estimated_cost', 'actual_cost', 'client_rate')
        }),
        ('Completion', {
            'fields': (
                'completion_notes', 'client_satisfaction_rating', 
                'completion_photos', 'payment_released'
            )
        }),
        ('Web3 Integration', {
            'fields': ('smart_contract_address', 'blockchain_transaction_hash'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )
    ordering = ['-scheduled_date', 'scheduled_start_time']


@admin.register(JobEquipment)
class JobEquipmentAdmin(admin.ModelAdmin):
    """Admin for job equipment usage."""
    list_display = [
        'job', 'equipment', 'quantity_used', 'condition_before', 'condition_after'
    ]
    list_filter = [
        'condition_before', 'condition_after', 'job__job_type'
    ]
    search_fields = [
        'job__job_number', 'equipment__name'
    ]
    readonly_fields = ['created', 'modified']
    fieldsets = (
        ('Basic Information', {
            'fields': ('job', 'equipment', 'quantity_used')
        }),
        ('Usage Details', {
            'fields': ('usage_notes',)
        }),
        ('Condition', {
            'fields': ('condition_before', 'condition_after')
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )
    ordering = ['job', 'equipment']


@admin.register(DispatchLog)
class DispatchLogAdmin(admin.ModelAdmin):
    """Admin for dispatch logs."""
    list_display = [
        'log_type', 'job', 'team', 'message', 'timestamp', 'created_by'
    ]
    list_filter = [
        'log_type', 'timestamp', 'created_by'
    ]
    search_fields = [
        'message', 'job__job_number', 'team__name'
    ]
    readonly_fields = ['created', 'modified', 'timestamp']
    fieldsets = (
        ('Basic Information', {
            'fields': ('log_type', 'message', 'timestamp')
        }),
        ('Related Objects', {
            'fields': ('job', 'team')
        }),
        ('Personnel', {
            'fields': ('created_by',)
        }),
        ('Web3 Integration', {
            'fields': ('blockchain_transaction_hash',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )
    ordering = ['-timestamp']
