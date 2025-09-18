"""
Facility Management models for TidyGen ERP.
Handles facilities, assets, equipment, vehicles, and maintenance.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel
from decimal import Decimal


class Facility(BaseModel):
    """
    Represents a physical facility or location.
    """
    FACILITY_TYPES = [
        ('office', 'Office Building'),
        ('warehouse', 'Warehouse'),
        ('depot', 'Equipment Depot'),
        ('client_site', 'Client Site'),
        ('storage', 'Storage Facility'),
        ('maintenance', 'Maintenance Center'),
    ]
    
    name = models.CharField(_('facility name'), max_length=200)
    facility_type = models.CharField(_('facility type'), max_length=20, choices=FACILITY_TYPES)
    address = models.TextField(_('address'))
    city = models.CharField(_('city'), max_length=100)
    state = models.CharField(_('state'), max_length=100)
    postal_code = models.CharField(_('postal code'), max_length=20)
    country = models.CharField(_('country'), max_length=100, default='US')
    
    # Contact Information
    contact_person = models.CharField(_('contact person'), max_length=100, blank=True)
    phone = models.CharField(_('phone'), max_length=20, blank=True)
    email = models.EmailField(_('email'), blank=True)
    
    # Facility Details
    total_area = models.DecimalField(_('total area (sq ft)'), max_digits=10, decimal_places=2, null=True, blank=True)
    capacity = models.IntegerField(_('capacity'), null=True, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    
    # Web3 Integration
    blockchain_address = models.CharField(_('blockchain address'), max_length=42, blank=True)
    nft_token_id = models.CharField(_('NFT token ID'), max_length=100, blank=True)
    
    class Meta:
        verbose_name = _('Facility')
        verbose_name_plural = _('Facilities')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_facility_type_display()})"


class Vehicle(BaseModel):
    """
    Represents a vehicle in the fleet.
    """
    VEHICLE_TYPES = [
        ('van', 'Cleaning Van'),
        ('truck', 'Truck'),
        ('car', 'Car'),
        ('motorcycle', 'Motorcycle'),
        ('other', 'Other'),
    ]
    
    FUEL_TYPES = [
        ('gasoline', 'Gasoline'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
        ('lpg', 'LPG'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('maintenance', 'In Maintenance'),
        ('retired', 'Retired'),
        ('sold', 'Sold'),
    ]
    
    # Basic Information
    make = models.CharField(_('make'), max_length=50)
    model = models.CharField(_('model'), max_length=50)
    year = models.IntegerField(_('year'), validators=[MinValueValidator(1900), MaxValueValidator(2030)])
    license_plate = models.CharField(_('license plate'), max_length=20, unique=True)
    vin = models.CharField(_('VIN'), max_length=17, unique=True, blank=True)
    
    # Vehicle Details
    vehicle_type = models.CharField(_('vehicle type'), max_length=20, choices=VEHICLE_TYPES)
    fuel_type = models.CharField(_('fuel type'), max_length=20, choices=FUEL_TYPES)
    color = models.CharField(_('color'), max_length=30, blank=True)
    
    # Operational Information
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='active')
    current_mileage = models.IntegerField(_('current mileage'), default=0)
    last_service_mileage = models.IntegerField(_('last service mileage'), default=0)
    next_service_mileage = models.IntegerField(_('next service mileage'), null=True, blank=True)
    
    # Financial Information
    purchase_price = models.DecimalField(_('purchase price'), max_digits=12, decimal_places=2, null=True, blank=True)
    current_value = models.DecimalField(_('current value'), max_digits=12, decimal_places=2, null=True, blank=True)
    insurance_policy = models.CharField(_('insurance policy'), max_length=100, blank=True)
    
    # Location
    home_facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicles')
    current_location = models.CharField(_('current location'), max_length=200, blank=True)
    
    # Web3 Integration
    blockchain_address = models.CharField(_('blockchain address'), max_length=42, blank=True)
    nft_token_id = models.CharField(_('NFT token ID'), max_length=100, blank=True)
    
    class Meta:
        verbose_name = _('Vehicle')
        verbose_name_plural = _('Vehicles')
        ordering = ['make', 'model']
    
    def __str__(self):
        return f"{self.year} {self.make} {self.model} ({self.license_plate})"


class Equipment(BaseModel):
    """
    Represents cleaning equipment and tools.
    """
    EQUIPMENT_TYPES = [
        ('vacuum', 'Vacuum Cleaner'),
        ('floor_scrubber', 'Floor Scrubber'),
        ('carpet_cleaner', 'Carpet Cleaner'),
        ('pressure_washer', 'Pressure Washer'),
        ('window_cleaner', 'Window Cleaning Equipment'),
        ('chemical_dispenser', 'Chemical Dispenser'),
        ('tool', 'Hand Tool'),
        ('safety', 'Safety Equipment'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('maintenance', 'In Maintenance'),
        ('retired', 'Retired'),
        ('lost', 'Lost'),
        ('stolen', 'Stolen'),
    ]
    
    # Basic Information
    name = models.CharField(_('equipment name'), max_length=200)
    equipment_type = models.CharField(_('equipment type'), max_length=30, choices=EQUIPMENT_TYPES)
    brand = models.CharField(_('brand'), max_length=100, blank=True)
    model = models.CharField(_('model'), max_length=100, blank=True)
    serial_number = models.CharField(_('serial number'), max_length=100, unique=True, blank=True)
    
    # Equipment Details
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='active')
    condition = models.CharField(_('condition'), max_length=20, choices=[
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ], default='good')
    
    # Operational Information
    purchase_date = models.DateField(_('purchase date'), null=True, blank=True)
    warranty_expiry = models.DateField(_('warranty expiry'), null=True, blank=True)
    last_maintenance = models.DateField(_('last maintenance'), null=True, blank=True)
    next_maintenance = models.DateField(_('next maintenance'), null=True, blank=True)
    
    # Financial Information
    purchase_price = models.DecimalField(_('purchase price'), max_digits=10, decimal_places=2, null=True, blank=True)
    current_value = models.DecimalField(_('current value'), max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Location
    current_facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipment')
    assigned_to = models.ForeignKey('hr.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_equipment')
    
    # Web3 Integration
    blockchain_address = models.CharField(_('blockchain address'), max_length=42, blank=True)
    nft_token_id = models.CharField(_('NFT token ID'), max_length=100, blank=True)
    
    class Meta:
        verbose_name = _('Equipment')
        verbose_name_plural = _('Equipment')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_equipment_type_display()})"


class MaintenanceRecord(BaseModel):
    """
    Records maintenance activities for vehicles and equipment.
    """
    MAINTENANCE_TYPES = [
        ('routine', 'Routine Maintenance'),
        ('repair', 'Repair'),
        ('inspection', 'Inspection'),
        ('cleaning', 'Cleaning'),
        ('calibration', 'Calibration'),
        ('replacement', 'Part Replacement'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Related Objects
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, null=True, blank=True, related_name='maintenance_records')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, null=True, blank=True, related_name='maintenance_records')
    
    # Maintenance Details
    maintenance_type = models.CharField(_('maintenance type'), max_length=20, choices=MAINTENANCE_TYPES)
    title = models.CharField(_('title'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    priority = models.CharField(_('priority'), max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Scheduling
    scheduled_date = models.DateTimeField(_('scheduled date'), null=True, blank=True)
    completed_date = models.DateTimeField(_('completed date'), null=True, blank=True)
    estimated_duration = models.DurationField(_('estimated duration'), null=True, blank=True)
    actual_duration = models.DurationField(_('actual duration'), null=True, blank=True)
    
    # Cost Information
    estimated_cost = models.DecimalField(_('estimated cost'), max_digits=10, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(_('actual cost'), max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Personnel
    assigned_to = models.ForeignKey('hr.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenance_assignments')
    performed_by = models.ForeignKey('hr.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenance_performed')
    
    # Status
    status = models.CharField(_('status'), max_length=20, choices=[
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='scheduled')
    
    # Web3 Integration
    blockchain_transaction_hash = models.CharField(_('blockchain transaction hash'), max_length=66, blank=True)
    
    class Meta:
        verbose_name = _('Maintenance Record')
        verbose_name_plural = _('Maintenance Records')
        ordering = ['-scheduled_date']
    
    def __str__(self):
        asset = self.vehicle or self.equipment
        return f"{self.title} - {asset}"


class Asset(BaseModel):
    """
    Generic asset model for tracking all company assets.
    """
    ASSET_TYPES = [
        ('vehicle', 'Vehicle'),
        ('equipment', 'Equipment'),
        ('furniture', 'Furniture'),
        ('technology', 'Technology'),
        ('real_estate', 'Real Estate'),
        ('other', 'Other'),
    ]
    
    # Basic Information
    name = models.CharField(_('asset name'), max_length=200)
    asset_type = models.CharField(_('asset type'), max_length=20, choices=ASSET_TYPES)
    description = models.TextField(_('description'), blank=True)
    
    # Asset Details
    serial_number = models.CharField(_('serial number'), max_length=100, blank=True)
    model_number = models.CharField(_('model number'), max_length=100, blank=True)
    manufacturer = models.CharField(_('manufacturer'), max_length=100, blank=True)
    
    # Financial Information
    purchase_price = models.DecimalField(_('purchase price'), max_digits=12, decimal_places=2, null=True, blank=True)
    current_value = models.DecimalField(_('current value'), max_digits=12, decimal_places=2, null=True, blank=True)
    depreciation_rate = models.DecimalField(_('depreciation rate (%)'), max_digits=5, decimal_places=2, default=0)
    
    # Location
    location = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets')
    
    # Web3 Integration
    blockchain_address = models.CharField(_('blockchain address'), max_length=42, blank=True)
    nft_token_id = models.CharField(_('NFT token ID'), max_length=100, blank=True)
    is_tokenized = models.BooleanField(_('is tokenized'), default=False)
    
    class Meta:
        verbose_name = _('Asset')
        verbose_name_plural = _('Assets')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_asset_type_display()})"
