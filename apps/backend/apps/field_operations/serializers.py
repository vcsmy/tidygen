"""
Serializers for Field Operations models.
"""

from rest_framework import serializers
from .models import (
    FieldTeam, TeamMember, ServiceRoute, RouteStop, 
    FieldJob, JobEquipment, DispatchLog
)


class FieldTeamSerializer(serializers.ModelSerializer):
    """Serializer for FieldTeam model."""
    
    assigned_vehicle_name = serializers.CharField(source='assigned_vehicle.__str__', read_only=True)
    home_base_name = serializers.CharField(source='home_base.name', read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = FieldTeam
        fields = [
            'id', 'name', 'team_type', 'status', 'description', 'max_capacity',
            'current_capacity', 'assigned_vehicle', 'assigned_vehicle_name',
            'home_base', 'home_base_name', 'current_location', 'total_jobs_completed',
            'average_rating', 'on_time_percentage', 'member_count', 'blockchain_address',
            'nft_token_id', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']
    
    def get_member_count(self, obj):
        return obj.members.filter(is_active=True).count()


class TeamMemberSerializer(serializers.ModelSerializer):
    """Serializer for TeamMember model."""
    
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = TeamMember
        fields = [
            'id', 'team', 'team_name', 'employee', 'employee_name', 'role',
            'is_team_leader', 'is_active', 'assigned_date', 'individual_rating',
            'jobs_completed', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class ServiceRouteSerializer(serializers.ModelSerializer):
    """Serializer for ServiceRoute model."""
    
    assigned_team_name = serializers.CharField(source='assigned_team.name', read_only=True)
    stop_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceRoute
        fields = [
            'id', 'name', 'route_type', 'status', 'description', 'total_distance',
            'estimated_duration', 'actual_duration', 'scheduled_date', 'start_time',
            'end_time', 'assigned_team', 'assigned_team_name', 'total_stops',
            'completed_stops', 'efficiency_rating', 'stop_count', 'blockchain_transaction_hash',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']
    
    def get_stop_count(self, obj):
        return obj.stops.count()


class RouteStopSerializer(serializers.ModelSerializer):
    """Serializer for RouteStop model."""
    
    route_name = serializers.CharField(source='route.name', read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    
    class Meta:
        model = RouteStop
        fields = [
            'id', 'route', 'route_name', 'client', 'client_name', 'stop_type',
            'sequence_number', 'status', 'address', 'latitude', 'longitude',
            'estimated_arrival', 'actual_arrival', 'estimated_departure',
            'actual_departure', 'estimated_duration', 'actual_duration',
            'service_notes', 'completion_notes', 'blockchain_transaction_hash',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class FieldJobSerializer(serializers.ModelSerializer):
    """Serializer for FieldJob model."""
    
    client_name = serializers.CharField(source='client.name', read_only=True)
    assigned_team_name = serializers.CharField(source='assigned_team.name', read_only=True)
    assigned_route_name = serializers.CharField(source='assigned_route.name', read_only=True)
    equipment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = FieldJob
        fields = [
            'id', 'job_number', 'title', 'job_type', 'priority', 'status',
            'description', 'special_instructions', 'client', 'client_name',
            'contact_person', 'contact_phone', 'service_address', 'latitude',
            'longitude', 'scheduled_date', 'scheduled_start_time', 'scheduled_end_time',
            'estimated_duration', 'actual_duration', 'assigned_team', 'assigned_team_name',
            'assigned_route', 'assigned_route_name', 'estimated_cost', 'actual_cost',
            'client_rate', 'completion_notes', 'client_satisfaction_rating',
            'completion_photos', 'equipment_count', 'smart_contract_address',
            'blockchain_transaction_hash', 'payment_released', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']
    
    def get_equipment_count(self, obj):
        return obj.equipment_used.count()


class JobEquipmentSerializer(serializers.ModelSerializer):
    """Serializer for JobEquipment model."""
    
    job_number = serializers.CharField(source='job.job_number', read_only=True)
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    
    class Meta:
        model = JobEquipment
        fields = [
            'id', 'job', 'job_number', 'equipment', 'equipment_name',
            'quantity_used', 'usage_notes', 'condition_before', 'condition_after',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class DispatchLogSerializer(serializers.ModelSerializer):
    """Serializer for DispatchLog model."""
    
    job_number = serializers.CharField(source='job.job_number', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = DispatchLog
        fields = [
            'id', 'job', 'job_number', 'team', 'team_name', 'log_type',
            'message', 'timestamp', 'created_by', 'created_by_name',
            'blockchain_transaction_hash', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified', 'timestamp']


class FieldTeamSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for field team summaries."""
    
    assigned_vehicle_name = serializers.CharField(source='assigned_vehicle.__str__', read_only=True)
    active_member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = FieldTeam
        fields = [
            'id', 'name', 'team_type', 'status', 'max_capacity', 'current_capacity',
            'assigned_vehicle_name', 'total_jobs_completed', 'average_rating',
            'active_member_count'
        ]
    
    def get_active_member_count(self, obj):
        return obj.members.filter(is_active=True).count()


class FieldJobSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for field job summaries."""
    
    client_name = serializers.CharField(source='client.name', read_only=True)
    assigned_team_name = serializers.CharField(source='assigned_team.name', read_only=True)
    
    class Meta:
        model = FieldJob
        fields = [
            'id', 'job_number', 'title', 'job_type', 'priority', 'status',
            'client_name', 'assigned_team_name', 'scheduled_date', 'scheduled_start_time',
            'estimated_cost', 'payment_released'
        ]


class ServiceRouteSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for service route summaries."""
    
    assigned_team_name = serializers.CharField(source='assigned_team.name', read_only=True)
    stop_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceRoute
        fields = [
            'id', 'name', 'route_type', 'status', 'scheduled_date', 'start_time',
            'assigned_team_name', 'total_stops', 'completed_stops', 'efficiency_rating',
            'stop_count'
        ]
    
    def get_stop_count(self, obj):
        return obj.stops.count()
