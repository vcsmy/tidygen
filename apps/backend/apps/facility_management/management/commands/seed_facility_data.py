"""
Management command to seed facility management data.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from apps.facility_management.models import Facility, Vehicle, Equipment, MaintenanceRecord, Asset
from apps.hr.models import Employee
from apps.sales.models import Client


class Command(BaseCommand):
    help = 'Seed facility management data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing facility management data...')
            self.clear_data()

        self.stdout.write('Starting to seed facility management data...')

        with transaction.atomic():
            # Create facilities
            facilities = self.create_facilities()
            
            # Create vehicles
            vehicles = self.create_vehicles(facilities)
            
            # Create equipment
            equipment = self.create_equipment(facilities)
            
            # Create maintenance records
            self.create_maintenance_records(vehicles, equipment)
            
            # Create assets
            self.create_assets(facilities)

        self.stdout.write(
            self.style.SUCCESS('Successfully seeded facility management data!')
        )

    def clear_data(self):
        """Clear existing data."""
        Asset.objects.all().delete()
        MaintenanceRecord.objects.all().delete()
        Equipment.objects.all().delete()
        Vehicle.objects.all().delete()
        Facility.objects.all().delete()

    def create_facilities(self):
        """Create sample facilities."""
        facilities_data = [
            {
                'name': 'Main Office & Warehouse',
                'facility_type': 'warehouse',
                'address': '123 Business Park Drive',
                'city': 'San Francisco',
                'state': 'CA',
                'postal_code': '94105',
                'contact_person': 'John Smith',
                'phone': '(555) 123-4567',
                'email': 'warehouse@tidygen.com',
                'total_area': Decimal('5000.00'),
                'capacity': 50,
            },
            {
                'name': 'Equipment Depot North',
                'facility_type': 'depot',
                'address': '456 Industrial Blvd',
                'city': 'Oakland',
                'state': 'CA',
                'postal_code': '94607',
                'contact_person': 'Sarah Johnson',
                'phone': '(555) 234-5678',
                'email': 'depot@tidygen.com',
                'total_area': Decimal('3000.00'),
                'capacity': 30,
            },
            {
                'name': 'Client Site - Tech Corp',
                'facility_type': 'client_site',
                'address': '789 Innovation Way',
                'city': 'San Jose',
                'state': 'CA',
                'postal_code': '95110',
                'contact_person': 'Mike Chen',
                'phone': '(555) 345-6789',
                'email': 'facilities@techcorp.com',
                'total_area': Decimal('10000.00'),
                'capacity': 200,
            },
            {
                'name': 'Maintenance Center',
                'facility_type': 'maintenance',
                'address': '321 Service Road',
                'city': 'Fremont',
                'state': 'CA',
                'postal_code': '94538',
                'contact_person': 'David Wilson',
                'phone': '(555) 456-7890',
                'email': 'maintenance@tidygen.com',
                'total_area': Decimal('2000.00'),
                'capacity': 20,
            }
        ]

        facilities = []
        for data in facilities_data:
            facility = Facility.objects.create(**data)
            facilities.append(facility)
            self.stdout.write(f'Created facility: {facility.name}')

        return facilities

    def create_vehicles(self, facilities):
        """Create sample vehicles."""
        vehicles_data = [
            {
                'make': 'Ford',
                'model': 'Transit',
                'year': 2022,
                'license_plate': 'TG001',
                'vin': '1FTBW2CM5NKA12345',
                'vehicle_type': 'van',
                'fuel_type': 'gasoline',
                'color': 'White',
                'current_mileage': 25000,
                'last_service_mileage': 20000,
                'next_service_mileage': 30000,
                'purchase_price': Decimal('35000.00'),
                'current_value': Decimal('28000.00'),
                'insurance_policy': 'POL-001-2024',
                'home_facility': facilities[0],
                'current_location': 'Main Office & Warehouse',
            },
            {
                'make': 'Chevrolet',
                'model': 'Express',
                'year': 2021,
                'license_plate': 'TG002',
                'vin': '1GC1YVEG5MZ123456',
                'vehicle_type': 'van',
                'fuel_type': 'gasoline',
                'color': 'Blue',
                'current_mileage': 35000,
                'last_service_mileage': 30000,
                'next_service_mileage': 40000,
                'purchase_price': Decimal('32000.00'),
                'current_value': Decimal('25000.00'),
                'insurance_policy': 'POL-002-2024',
                'home_facility': facilities[1],
                'current_location': 'Equipment Depot North',
            },
            {
                'make': 'Toyota',
                'model': 'Prius',
                'year': 2023,
                'license_plate': 'TG003',
                'vin': 'JTDKARFP3N3123456',
                'vehicle_type': 'car',
                'fuel_type': 'hybrid',
                'color': 'Silver',
                'current_mileage': 15000,
                'last_service_mileage': 10000,
                'next_service_mileage': 20000,
                'purchase_price': Decimal('28000.00'),
                'current_value': Decimal('24000.00'),
                'insurance_policy': 'POL-003-2024',
                'home_facility': facilities[0],
                'current_location': 'Main Office & Warehouse',
            }
        ]

        vehicles = []
        for data in vehicles_data:
            vehicle = Vehicle.objects.create(**data)
            vehicles.append(vehicle)
            self.stdout.write(f'Created vehicle: {vehicle.year} {vehicle.make} {vehicle.model}')

        return vehicles

    def create_equipment(self, facilities):
        """Create sample equipment."""
        equipment_data = [
            {
                'name': 'Industrial Vacuum Cleaner',
                'equipment_type': 'vacuum',
                'brand': 'Shark',
                'model': 'NV752',
                'serial_number': 'VAC-001-2024',
                'status': 'active',
                'condition': 'excellent',
                'purchase_date': datetime(2023, 1, 15).date(),
                'warranty_expiry': datetime(2025, 1, 15).date(),
                'last_maintenance': datetime(2024, 8, 1).date(),
                'next_maintenance': datetime(2024, 11, 1).date(),
                'purchase_price': Decimal('800.00'),
                'current_value': Decimal('600.00'),
                'current_facility': facilities[0],
            },
            {
                'name': 'Floor Scrubber',
                'equipment_type': 'floor_scrubber',
                'brand': 'Karcher',
                'model': 'BR 40/25 C',
                'serial_number': 'FS-002-2024',
                'status': 'active',
                'condition': 'good',
                'purchase_date': datetime(2022, 6, 10).date(),
                'warranty_expiry': datetime(2024, 6, 10).date(),
                'last_maintenance': datetime(2024, 7, 15).date(),
                'next_maintenance': datetime(2024, 10, 15).date(),
                'purchase_price': Decimal('2500.00'),
                'current_value': Decimal('1800.00'),
                'current_facility': facilities[1],
            },
            {
                'name': 'Carpet Cleaner',
                'equipment_type': 'carpet_cleaner',
                'brand': 'Bissell',
                'model': 'Big Green',
                'serial_number': 'CC-003-2024',
                'status': 'active',
                'condition': 'good',
                'purchase_date': datetime(2023, 3, 20).date(),
                'warranty_expiry': datetime(2025, 3, 20).date(),
                'last_maintenance': datetime(2024, 9, 1).date(),
                'next_maintenance': datetime(2024, 12, 1).date(),
                'purchase_price': Decimal('1200.00'),
                'current_value': Decimal('900.00'),
                'current_facility': facilities[0],
            },
            {
                'name': 'Pressure Washer',
                'equipment_type': 'pressure_washer',
                'brand': 'Karcher',
                'model': 'K5 Premium',
                'serial_number': 'PW-004-2024',
                'status': 'maintenance',
                'condition': 'fair',
                'purchase_date': datetime(2021, 8, 5).date(),
                'warranty_expiry': datetime(2023, 8, 5).date(),
                'last_maintenance': datetime(2024, 8, 20).date(),
                'next_maintenance': datetime(2024, 9, 20).date(),
                'purchase_price': Decimal('600.00'),
                'current_value': Decimal('300.00'),
                'current_facility': facilities[3],
            }
        ]

        equipment = []
        for data in equipment_data:
            equipment_item = Equipment.objects.create(**data)
            equipment.append(equipment_item)
            self.stdout.write(f'Created equipment: {equipment_item.name}')

        return equipment

    def create_maintenance_records(self, vehicles, equipment):
        """Create sample maintenance records."""
        maintenance_data = [
            {
                'vehicle': vehicles[0],
                'maintenance_type': 'routine',
                'title': 'Oil Change and Filter Replacement',
                'description': 'Regular oil change and air filter replacement',
                'priority': 'medium',
                'status': 'completed',
                'scheduled_date': timezone.now() - timedelta(days=5),
                'completed_date': timezone.now() - timedelta(days=5),
                'estimated_duration': timedelta(hours=1),
                'actual_duration': timedelta(hours=1, minutes=15),
                'estimated_cost': Decimal('150.00'),
                'actual_cost': Decimal('165.00'),
            },
            {
                'equipment': equipment[3],
                'maintenance_type': 'repair',
                'title': 'Pressure Washer Pump Repair',
                'description': 'Replace worn pump seals and check pressure settings',
                'priority': 'high',
                'status': 'in_progress',
                'scheduled_date': timezone.now() - timedelta(days=2),
                'estimated_duration': timedelta(hours=3),
                'estimated_cost': Decimal('200.00'),
            },
            {
                'vehicle': vehicles[1],
                'maintenance_type': 'inspection',
                'title': 'Annual Safety Inspection',
                'description': 'Complete annual safety inspection and certification',
                'priority': 'high',
                'status': 'scheduled',
                'scheduled_date': timezone.now() + timedelta(days=7),
                'estimated_duration': timedelta(hours=2),
                'estimated_cost': Decimal('100.00'),
            }
        ]

        for data in maintenance_data:
            maintenance = MaintenanceRecord.objects.create(**data)
            self.stdout.write(f'Created maintenance record: {maintenance.title}')

    def create_assets(self, facilities):
        """Create sample assets."""
        assets_data = [
            {
                'name': 'Office Furniture Set',
                'asset_type': 'furniture',
                'description': 'Complete office furniture set for main office',
                'serial_number': 'FURN-001-2024',
                'model_number': 'OF-2024-SET',
                'manufacturer': 'IKEA',
                'purchase_price': Decimal('5000.00'),
                'current_value': Decimal('3500.00'),
                'depreciation_rate': Decimal('20.00'),
                'location': facilities[0],
                'is_tokenized': False,
            },
            {
                'name': 'Computer Workstation',
                'asset_type': 'technology',
                'description': 'High-performance workstation for design work',
                'serial_number': 'TECH-002-2024',
                'model_number': 'WS-2024-PRO',
                'manufacturer': 'Dell',
                'purchase_price': Decimal('3000.00'),
                'current_value': Decimal('2200.00'),
                'depreciation_rate': Decimal('25.00'),
                'location': facilities[0],
                'is_tokenized': True,
                'nft_token_id': 'TGA-TECH-002-20240917',
            },
            {
                'name': 'Warehouse Storage Racks',
                'asset_type': 'furniture',
                'description': 'Heavy-duty storage rack system',
                'serial_number': 'RACK-003-2024',
                'model_number': 'SR-2024-HD',
                'manufacturer': 'Steelcase',
                'purchase_price': Decimal('8000.00'),
                'current_value': Decimal('6000.00'),
                'depreciation_rate': Decimal('15.00'),
                'location': facilities[0],
                'is_tokenized': False,
            }
        ]

        for data in assets_data:
            asset = Asset.objects.create(**data)
            self.stdout.write(f'Created asset: {asset.name}')
