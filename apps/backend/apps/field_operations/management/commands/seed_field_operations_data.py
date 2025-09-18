"""
Management command to seed field operations data.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from apps.field_operations.models import (
    FieldTeam, TeamMember, ServiceRoute, RouteStop, 
    FieldJob, JobEquipment, DispatchLog
)
from apps.facility_management.models import Facility, Vehicle, Equipment
from apps.hr.models import Employee
from apps.sales.models import Client


class Command(BaseCommand):
    help = 'Seed field operations data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing field operations data...')
            self.clear_data()

        self.stdout.write('Starting to seed field operations data...')

        with transaction.atomic():
            # Create field teams
            teams = self.create_field_teams()
            
            # Create team members
            self.create_team_members(teams)
            
            # Create service routes
            routes = self.create_service_routes(teams)
            
            # Create route stops
            self.create_route_stops(routes)
            
            # Create field jobs
            jobs = self.create_field_jobs(teams, routes)
            
            # Create job equipment
            self.create_job_equipment(jobs)
            
            # Create dispatch logs
            self.create_dispatch_logs(jobs, teams)

        self.stdout.write(
            self.style.SUCCESS('Successfully seeded field operations data!')
        )

    def clear_data(self):
        """Clear existing data."""
        DispatchLog.objects.all().delete()
        JobEquipment.objects.all().delete()
        FieldJob.objects.all().delete()
        RouteStop.objects.all().delete()
        ServiceRoute.objects.all().delete()
        TeamMember.objects.all().delete()
        FieldTeam.objects.all().delete()

    def create_field_teams(self):
        """Create sample field teams."""
        # Get facilities and vehicles
        facilities = Facility.objects.all()
        vehicles = Vehicle.objects.all()
        
        teams_data = [
            {
                'name': 'Alpha Cleaning Team',
                'team_type': 'cleaning',
                'status': 'active',
                'description': 'Primary cleaning team for office buildings',
                'max_capacity': 5,
                'current_capacity': 4,
                'assigned_vehicle': vehicles[0] if vehicles else None,
                'home_base': facilities[0] if facilities else None,
                'current_location': 'Main Office & Warehouse',
                'total_jobs_completed': 45,
                'average_rating': Decimal('4.5'),
                'on_time_percentage': Decimal('92.5'),
            },
            {
                'name': 'Beta Maintenance Team',
                'team_type': 'maintenance',
                'status': 'active',
                'description': 'Specialized maintenance and repair team',
                'max_capacity': 3,
                'current_capacity': 3,
                'assigned_vehicle': vehicles[1] if len(vehicles) > 1 else None,
                'home_base': facilities[1] if len(facilities) > 1 else None,
                'current_location': 'Equipment Depot North',
                'total_jobs_completed': 28,
                'average_rating': Decimal('4.8'),
                'on_time_percentage': Decimal('95.0'),
            },
            {
                'name': 'Gamma Emergency Team',
                'team_type': 'emergency',
                'status': 'active',
                'description': 'Emergency response and urgent cleaning services',
                'max_capacity': 4,
                'current_capacity': 2,
                'assigned_vehicle': vehicles[2] if len(vehicles) > 2 else None,
                'home_base': facilities[0] if facilities else None,
                'current_location': 'Main Office & Warehouse',
                'total_jobs_completed': 15,
                'average_rating': Decimal('4.2'),
                'on_time_percentage': Decimal('88.0'),
            }
        ]

        teams = []
        for data in teams_data:
            team = FieldTeam.objects.create(**data)
            teams.append(team)
            self.stdout.write(f'Created field team: {team.name}')

        return teams

    def create_team_members(self, teams):
        """Create sample team members."""
        # Get employees
        employees = Employee.objects.all()
        
        if not employees:
            self.stdout.write('No employees found. Please create employees first.')
            return

        members_data = [
            {
                'team': teams[0],
                'employee': employees[0] if employees else None,
                'role': 'team_leader',
                'is_team_leader': True,
                'individual_rating': Decimal('4.7'),
                'jobs_completed': 25,
            },
            {
                'team': teams[0],
                'employee': employees[1] if len(employees) > 1 else None,
                'role': 'specialist',
                'is_team_leader': False,
                'individual_rating': Decimal('4.3'),
                'jobs_completed': 18,
            },
            {
                'team': teams[1],
                'employee': employees[2] if len(employees) > 2 else None,
                'role': 'team_leader',
                'is_team_leader': True,
                'individual_rating': Decimal('4.9'),
                'jobs_completed': 20,
            },
            {
                'team': teams[2],
                'employee': employees[0] if employees else None,
                'role': 'technician',
                'is_team_leader': False,
                'individual_rating': Decimal('4.1'),
                'jobs_completed': 12,
            }
        ]

        for data in members_data:
            if data['employee']:
                member = TeamMember.objects.create(**data)
                self.stdout.write(f'Created team member: {member.employee.get_full_name()} - {member.team.name}')

    def create_service_routes(self, teams):
        """Create sample service routes."""
        routes_data = [
            {
                'name': 'Downtown Office Route',
                'route_type': 'daily',
                'status': 'active',
                'description': 'Daily cleaning route for downtown office buildings',
                'total_distance': Decimal('25.5'),
                'estimated_duration': timedelta(hours=6),
                'scheduled_date': timezone.now().date(),
                'start_time': datetime.strptime('08:00', '%H:%M').time(),
                'end_time': datetime.strptime('14:00', '%H:%M').time(),
                'assigned_team': teams[0],
                'total_stops': 5,
                'completed_stops': 2,
                'efficiency_rating': Decimal('4.2'),
            },
            {
                'name': 'Maintenance Check Route',
                'route_type': 'weekly',
                'status': 'planned',
                'description': 'Weekly maintenance check for all facilities',
                'total_distance': Decimal('45.0'),
                'estimated_duration': timedelta(hours=8),
                'scheduled_date': timezone.now().date() + timedelta(days=1),
                'start_time': datetime.strptime('07:00', '%H:%M').time(),
                'end_time': datetime.strptime('15:00', '%H:%M').time(),
                'assigned_team': teams[1],
                'total_stops': 8,
                'completed_stops': 0,
                'efficiency_rating': Decimal('4.8'),
            },
            {
                'name': 'Emergency Response Route',
                'route_type': 'custom',
                'status': 'completed',
                'description': 'Emergency cleaning response for urgent situations',
                'total_distance': Decimal('15.0'),
                'estimated_duration': timedelta(hours=3),
                'actual_duration': timedelta(hours=2, minutes=45),
                'scheduled_date': timezone.now().date() - timedelta(days=1),
                'start_time': datetime.strptime('14:00', '%H:%M').time(),
                'end_time': datetime.strptime('17:00', '%H:%M').time(),
                'assigned_team': teams[2],
                'total_stops': 2,
                'completed_stops': 2,
                'efficiency_rating': Decimal('4.5'),
            }
        ]

        routes = []
        for data in routes_data:
            route = ServiceRoute.objects.create(**data)
            routes.append(route)
            self.stdout.write(f'Created service route: {route.name}')

        return routes

    def create_route_stops(self, routes):
        """Create sample route stops."""
        # Get clients
        clients = Client.objects.all()
        
        stops_data = [
            {
                'route': routes[0],
                'client': clients[0] if clients else None,
                'stop_type': 'service',
                'sequence_number': 1,
                'status': 'completed',
                'address': '123 Business Street, San Francisco, CA 94105',
                'latitude': Decimal('37.7749'),
                'longitude': Decimal('-122.4194'),
                'estimated_arrival': timezone.now() - timedelta(hours=2),
                'actual_arrival': timezone.now() - timedelta(hours=2, minutes=5),
                'estimated_departure': timezone.now() - timedelta(hours=1, minutes=30),
                'actual_departure': timezone.now() - timedelta(hours=1, minutes=25),
                'estimated_duration': timedelta(minutes=30),
                'actual_duration': timedelta(minutes=25),
                'service_notes': 'Regular office cleaning - all floors',
                'completion_notes': 'Completed successfully, client satisfied',
            },
            {
                'route': routes[0],
                'client': clients[1] if len(clients) > 1 else None,
                'stop_type': 'service',
                'sequence_number': 2,
                'status': 'in_progress',
                'address': '456 Corporate Plaza, San Francisco, CA 94107',
                'latitude': Decimal('37.7849'),
                'longitude': Decimal('-122.4094'),
                'estimated_arrival': timezone.now() - timedelta(minutes=30),
                'actual_arrival': timezone.now() - timedelta(minutes=25),
                'estimated_duration': timedelta(minutes=45),
                'service_notes': 'Deep cleaning - conference rooms and lobby',
            },
            {
                'route': routes[1],
                'client': clients[0] if clients else None,
                'stop_type': 'maintenance',
                'sequence_number': 1,
                'status': 'pending',
                'address': '789 Tech Center, San Jose, CA 95110',
                'latitude': Decimal('37.3382'),
                'longitude': Decimal('-121.8863'),
                'estimated_arrival': timezone.now() + timedelta(days=1, hours=2),
                'estimated_duration': timedelta(hours=1),
                'service_notes': 'Equipment maintenance check',
            }
        ]

        for data in stops_data:
            if data['client']:
                stop = RouteStop.objects.create(**data)
                self.stdout.write(f'Created route stop: {stop.route.name} - Stop {stop.sequence_number}')

    def create_field_jobs(self, teams, routes):
        """Create sample field jobs."""
        # Get clients
        clients = Client.objects.all()
        
        jobs_data = [
            {
                'job_number': 'JOB-2024-001',
                'title': 'Office Deep Cleaning',
                'job_type': 'cleaning',
                'priority': 'medium',
                'status': 'completed',
                'description': 'Complete deep cleaning of 5-story office building',
                'special_instructions': 'Focus on high-traffic areas and restrooms',
                'client': clients[0] if clients else None,
                'contact_person': 'John Smith',
                'contact_phone': '(555) 123-4567',
                'service_address': '123 Business Street, San Francisco, CA 94105',
                'latitude': Decimal('37.7749'),
                'longitude': Decimal('-122.4194'),
                'scheduled_date': timezone.now().date() - timedelta(days=1),
                'scheduled_start_time': datetime.strptime('09:00', '%H:%M').time(),
                'scheduled_end_time': datetime.strptime('17:00', '%H:%M').time(),
                'estimated_duration': timedelta(hours=8),
                'actual_duration': timedelta(hours=7, minutes=30),
                'assigned_team': teams[0],
                'assigned_route': routes[0],
                'estimated_cost': Decimal('800.00'),
                'actual_cost': Decimal('750.00'),
                'client_rate': Decimal('100.00'),
                'completion_notes': 'Job completed successfully, client very satisfied',
                'client_satisfaction_rating': 5,
                'payment_released': True,
            },
            {
                'job_number': 'JOB-2024-002',
                'title': 'Emergency Spill Cleanup',
                'job_type': 'emergency',
                'priority': 'urgent',
                'status': 'in_progress',
                'description': 'Urgent cleanup of chemical spill in warehouse',
                'special_instructions': 'Use appropriate safety equipment and procedures',
                'client': clients[1] if len(clients) > 1 else None,
                'contact_person': 'Sarah Johnson',
                'contact_phone': '(555) 234-5678',
                'service_address': '456 Industrial Blvd, Oakland, CA 94607',
                'latitude': Decimal('37.8044'),
                'longitude': Decimal('-122.2712'),
                'scheduled_date': timezone.now().date(),
                'scheduled_start_time': datetime.strptime('14:00', '%H:%M').time(),
                'scheduled_end_time': datetime.strptime('18:00', '%H:%M').time(),
                'estimated_duration': timedelta(hours=4),
                'assigned_team': teams[2],
                'estimated_cost': Decimal('500.00'),
                'client_rate': Decimal('125.00'),
            },
            {
                'job_number': 'JOB-2024-003',
                'title': 'Monthly Maintenance Check',
                'job_type': 'maintenance',
                'priority': 'low',
                'status': 'scheduled',
                'description': 'Monthly maintenance check for all equipment',
                'special_instructions': 'Check all equipment and update maintenance records',
                'client': clients[0] if clients else None,
                'contact_person': 'Mike Chen',
                'contact_phone': '(555) 345-6789',
                'service_address': '789 Innovation Way, San Jose, CA 95110',
                'latitude': Decimal('37.3382'),
                'longitude': Decimal('-121.8863'),
                'scheduled_date': timezone.now().date() + timedelta(days=3),
                'scheduled_start_time': datetime.strptime('10:00', '%H:%M').time(),
                'scheduled_end_time': datetime.strptime('16:00', '%H:%M').time(),
                'estimated_duration': timedelta(hours=6),
                'assigned_team': teams[1],
                'estimated_cost': Decimal('300.00'),
                'client_rate': Decimal('50.00'),
            }
        ]

        jobs = []
        for data in jobs_data:
            if data['client']:
                job = FieldJob.objects.create(**data)
                jobs.append(job)
                self.stdout.write(f'Created field job: {job.job_number} - {job.title}')

        return jobs

    def create_job_equipment(self, jobs):
        """Create sample job equipment records."""
        # Get equipment
        equipment = Equipment.objects.all()
        
        if not equipment or not jobs:
            return

        job_equipment_data = [
            {
                'job': jobs[0],
                'equipment': equipment[0],
                'quantity_used': 2,
                'usage_notes': 'Used for deep cleaning of carpets',
                'condition_before': 'excellent',
                'condition_after': 'excellent',
            },
            {
                'job': jobs[0],
                'equipment': equipment[1],
                'quantity_used': 1,
                'usage_notes': 'Floor scrubbing in lobby and common areas',
                'condition_before': 'good',
                'condition_after': 'good',
            },
            {
                'job': jobs[1],
                'equipment': equipment[2],
                'quantity_used': 1,
                'usage_notes': 'Emergency carpet cleaning for spill',
                'condition_before': 'good',
                'condition_after': 'good',
            }
        ]

        for data in job_equipment_data:
            job_equipment = JobEquipment.objects.create(**data)
            self.stdout.write(f'Created job equipment: {job_equipment.job.job_number} - {job_equipment.equipment.name}')

    def create_dispatch_logs(self, jobs, teams):
        """Create sample dispatch logs."""
        logs_data = [
            {
                'job': jobs[0],
                'team': teams[0],
                'log_type': 'assignment',
                'message': f'Job {jobs[0].job_number} assigned to {teams[0].name}',
                'timestamp': timezone.now() - timedelta(days=1, hours=2),
            },
            {
                'job': jobs[0],
                'team': teams[0],
                'log_type': 'update',
                'message': f'Job {jobs[0].job_number} started on time',
                'timestamp': timezone.now() - timedelta(days=1, hours=1),
            },
            {
                'job': jobs[0],
                'team': teams[0],
                'log_type': 'update',
                'message': f'Job {jobs[0].job_number} completed successfully',
                'timestamp': timezone.now() - timedelta(days=1, minutes=30),
            },
            {
                'job': jobs[1],
                'team': teams[2],
                'log_type': 'emergency',
                'message': f'Emergency job {jobs[1].job_number} dispatched to {teams[2].name}',
                'timestamp': timezone.now() - timedelta(hours=2),
            },
            {
                'team': teams[1],
                'log_type': 'communication',
                'message': f'Team {teams[1].name} ready for tomorrow\'s maintenance route',
                'timestamp': timezone.now() - timedelta(hours=1),
            }
        ]

        for data in logs_data:
            log = DispatchLog.objects.create(**data)
            self.stdout.write(f'Created dispatch log: {log.log_type} - {log.message[:50]}...')
