"""
Admin configuration for Facility Management models.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Facility, Vehicle, Equipment, MaintenanceRecord, Asset


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    """Admin for facilities."""
    list_display = [
        'name', 'facility_type', 'city', 'state', 'is_active', 
        'total_area', 'capacity', 'created'
    ]
    list_filter = [
        'facility_type', 'is_active', 'city', 'state', 'created'
    ]
    search_fields = [
        'name', 'address', 'city', 'state', 'contact_person', 'email'
    ]
    readonly_fields = ['created', 'modified']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'facility_type', 'is_active')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'postal_code', 'country')
        }),
        ('Contact Information', {
            'fields': ('contact_person', 'phone', 'email')
        }),
        ('Facility Details', {
            'fields': ('total_area', 'capacity')
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


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    """Admin for vehicles."""
    list_display = [
        'make', 'model', 'year', 'license_plate', 'vehicle_type', 
        'status', 'current_mileage', 'home_facility'
    ]
    list_filter = [
        'vehicle_type', 'fuel_type', 'status', 'year', 'home_facility'
    ]
    search_fields = [
        'make', 'model', 'license_plate', 'vin', 'color'
    ]
    readonly_fields = ['created', 'modified']
    fieldsets = (
        ('Basic Information', {
            'fields': ('make', 'model', 'year', 'license_plate', 'vin')
        }),
        ('Vehicle Details', {
            'fields': ('vehicle_type', 'fuel_type', 'color', 'status')
        }),
        ('Operational Information', {
            'fields': ('current_mileage', 'last_service_mileage', 'next_service_mileage')
        }),
        ('Financial Information', {
            'fields': ('purchase_price', 'current_value', 'insurance_policy')
        }),
        ('Location', {
            'fields': ('home_facility', 'current_location')
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
    ordering = ['make', 'model']


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    """Admin for equipment."""
    list_display = [
        'name', 'equipment_type', 'brand', 'model', 'status', 
        'condition', 'current_facility', 'assigned_to'
    ]
    list_filter = [
        'equipment_type', 'status', 'condition', 'current_facility', 'brand'
    ]
    search_fields = [
        'name', 'brand', 'model', 'serial_number'
    ]
    readonly_fields = ['created', 'modified']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'equipment_type', 'brand', 'model', 'serial_number')
        }),
        ('Equipment Details', {
            'fields': ('status', 'condition')
        }),
        ('Operational Information', {
            'fields': ('purchase_date', 'warranty_expiry', 'last_maintenance', 'next_maintenance')
        }),
        ('Financial Information', {
            'fields': ('purchase_price', 'current_value')
        }),
        ('Location & Assignment', {
            'fields': ('current_facility', 'assigned_to')
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


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    """Admin for maintenance records."""
    list_display = [
        'title', 'maintenance_type', 'vehicle', 'equipment', 
        'priority', 'status', 'scheduled_date', 'assigned_to'
    ]
    list_filter = [
        'maintenance_type', 'priority', 'status', 'scheduled_date', 'assigned_to'
    ]
    search_fields = [
        'title', 'description', 'vehicle__make', 'equipment__name'
    ]
    readonly_fields = ['created', 'modified']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'maintenance_type', 'priority', 'status')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Related Objects', {
            'fields': ('vehicle', 'equipment')
        }),
        ('Scheduling', {
            'fields': ('scheduled_date', 'completed_date', 'estimated_duration', 'actual_duration')
        }),
        ('Cost Information', {
            'fields': ('estimated_cost', 'actual_cost')
        }),
        ('Personnel', {
            'fields': ('assigned_to', 'performed_by')
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
    ordering = ['-scheduled_date']


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    """Admin for assets."""
    list_display = [
        'name', 'asset_type', 'manufacturer', 'serial_number', 
        'current_value', 'location', 'is_tokenized'
    ]
    list_filter = [
        'asset_type', 'location', 'is_tokenized', 'created'
    ]
    search_fields = [
        'name', 'serial_number', 'model_number', 'manufacturer'
    ]
    readonly_fields = ['created', 'modified']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'asset_type', 'description')
        }),
        ('Asset Details', {
            'fields': ('serial_number', 'model_number', 'manufacturer')
        }),
        ('Financial Information', {
            'fields': ('purchase_price', 'current_value', 'depreciation_rate')
        }),
        ('Location', {
            'fields': ('location',)
        }),
        ('Web3 Integration', {
            'fields': ('blockchain_address', 'nft_token_id', 'is_tokenized'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )
    ordering = ['name']
