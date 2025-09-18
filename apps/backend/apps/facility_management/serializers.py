"""
Serializers for Facility Management models.
"""

from rest_framework import serializers
from .models import Facility, Vehicle, Equipment, MaintenanceRecord, Asset


class FacilitySerializer(serializers.ModelSerializer):
    """Serializer for Facility model."""
    
    class Meta:
        model = Facility
        fields = [
            'id', 'name', 'facility_type', 'address', 'city', 'state', 
            'postal_code', 'country', 'contact_person', 'phone', 'email',
            'total_area', 'capacity', 'is_active', 'blockchain_address', 
            'nft_token_id', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class VehicleSerializer(serializers.ModelSerializer):
    """Serializer for Vehicle model."""
    
    home_facility_name = serializers.CharField(source='home_facility.name', read_only=True)
    
    class Meta:
        model = Vehicle
        fields = [
            'id', 'make', 'model', 'year', 'license_plate', 'vin',
            'vehicle_type', 'fuel_type', 'color', 'status', 'current_mileage',
            'last_service_mileage', 'next_service_mileage', 'purchase_price',
            'current_value', 'insurance_policy', 'home_facility', 'home_facility_name',
            'current_location', 'blockchain_address', 'nft_token_id', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class EquipmentSerializer(serializers.ModelSerializer):
    """Serializer for Equipment model."""
    
    current_facility_name = serializers.CharField(source='current_facility.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    
    class Meta:
        model = Equipment
        fields = [
            'id', 'name', 'equipment_type', 'brand', 'model', 'serial_number',
            'status', 'condition', 'purchase_date', 'warranty_expiry',
            'last_maintenance', 'next_maintenance', 'purchase_price', 'current_value',
            'current_facility', 'current_facility_name', 'assigned_to', 'assigned_to_name',
            'blockchain_address', 'nft_token_id', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class MaintenanceRecordSerializer(serializers.ModelSerializer):
    """Serializer for MaintenanceRecord model."""
    
    vehicle_name = serializers.CharField(source='vehicle.__str__', read_only=True)
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)
    
    class Meta:
        model = MaintenanceRecord
        fields = [
            'id', 'vehicle', 'equipment', 'vehicle_name', 'equipment_name',
            'maintenance_type', 'title', 'description', 'priority', 'status',
            'scheduled_date', 'completed_date', 'estimated_duration', 'actual_duration',
            'estimated_cost', 'actual_cost', 'assigned_to', 'assigned_to_name',
            'performed_by', 'performed_by_name', 'blockchain_transaction_hash',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class AssetSerializer(serializers.ModelSerializer):
    """Serializer for Asset model."""
    
    location_name = serializers.CharField(source='location.name', read_only=True)
    
    class Meta:
        model = Asset
        fields = [
            'id', 'name', 'asset_type', 'description', 'serial_number',
            'model_number', 'manufacturer', 'purchase_price', 'current_value',
            'depreciation_rate', 'location', 'location_name', 'blockchain_address',
            'nft_token_id', 'is_tokenized', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class FacilitySummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for facility summaries."""
    
    vehicle_count = serializers.SerializerMethodField()
    equipment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Facility
        fields = [
            'id', 'name', 'facility_type', 'city', 'state', 'is_active',
            'vehicle_count', 'equipment_count'
        ]
    
    def get_vehicle_count(self, obj):
        return obj.vehicles.count()
    
    def get_equipment_count(self, obj):
        return obj.equipment.count()


class VehicleSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for vehicle summaries."""
    
    home_facility_name = serializers.CharField(source='home_facility.name', read_only=True)
    maintenance_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Vehicle
        fields = [
            'id', 'make', 'model', 'year', 'license_plate', 'vehicle_type',
            'status', 'current_mileage', 'home_facility_name', 'maintenance_count'
        ]
    
    def get_maintenance_count(self, obj):
        return obj.maintenance_records.count()


class EquipmentSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for equipment summaries."""
    
    current_facility_name = serializers.CharField(source='current_facility.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    maintenance_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Equipment
        fields = [
            'id', 'name', 'equipment_type', 'brand', 'model', 'status',
            'condition', 'current_facility_name', 'assigned_to_name', 'maintenance_count'
        ]
    
    def get_maintenance_count(self, obj):
        return obj.maintenance_records.count()
