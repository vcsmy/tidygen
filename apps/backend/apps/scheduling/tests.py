"""
Comprehensive scheduling management tests.
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.core.models import User
from .models import (
    ScheduleTemplate, Resource, Team, TeamMember, Appointment,
    ScheduleConflict, ScheduleRule, ScheduleNotification,
    ScheduleAnalytics, ScheduleIntegration
)

User = get_user_model()


class ScheduleTemplateModelTest(TestCase):
    """Test ScheduleTemplate model."""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.template = ScheduleTemplate.objects.create(
            organization=self.organization,
            name="Weekly Meeting Template",
            description="Template for weekly team meetings",
            schedule_type="weekly",
            start_time="09:00:00",
            end_time="10:00:00",
            duration_minutes=60,
            max_capacity=10,
            base_price=Decimal('100.00'),
            currency="USD"
        )
    
    def test_schedule_template_creation(self):
        """Test schedule template creation."""
        self.assertEqual(self.template.organization, self.organization)
        self.assertEqual(self.template.name, "Weekly Meeting Template")
        self.assertEqual(self.template.schedule_type, "weekly")
        self.assertEqual(self.template.start_time.strftime('%H:%M'), "09:00")
        self.assertEqual(self.template.end_time.strftime('%H:%M'), "10:00")
        self.assertEqual(self.template.duration_minutes, 60)
        self.assertEqual(self.template.max_capacity, 10)
        self.assertEqual(self.template.base_price, Decimal('100.00'))
        self.assertEqual(self.template.currency, "USD")
    
    def test_schedule_template_str(self):
        """Test schedule template string representation."""
        expected = f"Weekly Meeting Template - {self.organization.name}"
        self.assertEqual(str(self.template), expected)
    
    def test_schedule_template_validation(self):
        """Test schedule template validation."""
        # Test invalid time range
        with self.assertRaises(ValidationError):
            template = ScheduleTemplate(
                organization=self.organization,
                name="Invalid Template",
                schedule_type="daily",
                start_time="10:00:00",
                end_time="09:00:00",  # End before start
                duration_minutes=60
            )
            template.full_clean()


class ResourceModelTest(TestCase):
    """Test Resource model."""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.resource = Resource.objects.create(
            organization=self.organization,
            name="Conference Room A",
            resource_type="room",
            description="Large conference room with projector",
            location="Building 1, Floor 2",
            capacity=20,
            hourly_rate=Decimal('50.00'),
            daily_rate=Decimal('300.00'),
            currency="USD"
        )
    
    def test_resource_creation(self):
        """Test resource creation."""
        self.assertEqual(self.resource.organization, self.organization)
        self.assertEqual(self.resource.name, "Conference Room A")
        self.assertEqual(self.resource.resource_type, "room")
        self.assertEqual(self.resource.description, "Large conference room with projector")
        self.assertEqual(self.resource.location, "Building 1, Floor 2")
        self.assertEqual(self.resource.capacity, 20)
        self.assertEqual(self.resource.hourly_rate, Decimal('50.00'))
        self.assertEqual(self.resource.daily_rate, Decimal('300.00'))
        self.assertEqual(self.resource.currency, "USD")
    
    def test_resource_str(self):
        """Test resource string representation."""
        expected = f"Conference Room A (Room) - {self.organization.name}"
        self.assertEqual(str(self.resource), expected)


class TeamModelTest(TestCase):
    """Test Team model."""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="teamlead",
            email="lead@example.com",
            password="testpass123"
        )
        self.team = Team.objects.create(
            organization=self.organization,
            name="Development Team",
            description="Software development team",
            team_lead=self.user,
            max_members=8
        )
    
    def test_team_creation(self):
        """Test team creation."""
        self.assertEqual(self.team.organization, self.organization)
        self.assertEqual(self.team.name, "Development Team")
        self.assertEqual(self.team.description, "Software development team")
        self.assertEqual(self.team.team_lead, self.user)
        self.assertEqual(self.team.max_members, 8)
    
    def test_team_str(self):
        """Test team string representation."""
        expected = f"Development Team - {self.organization.name}"
        self.assertEqual(str(self.team), expected)


class TeamMemberModelTest(TestCase):
    """Test TeamMember model."""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="member",
            email="member@example.com",
            password="testpass123"
        )
        self.team = Team.objects.create(
            organization=self.organization,
            name="Development Team"
        )
        self.team_member = TeamMember.objects.create(
            team=self.team,
            user=self.user,
            role="member",
            max_hours_per_week=40
        )
    
    def test_team_member_creation(self):
        """Test team member creation."""
        self.assertEqual(self.team_member.team, self.team)
        self.assertEqual(self.team_member.user, self.user)
        self.assertEqual(self.team_member.role, "member")
        self.assertEqual(self.team_member.max_hours_per_week, 40)
    
    def test_team_member_str(self):
        """Test team member string representation."""
        expected = f"{self.user.get_full_name()} - Development Team (Member)"
        self.assertEqual(str(self.team_member), expected)


class AppointmentModelTest(TestCase):
    """Test Appointment model."""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="client",
            email="client@example.com",
            password="testpass123"
        )
        self.team = Team.objects.create(
            organization=self.organization,
            name="Support Team"
        )
        self.resource = Resource.objects.create(
            organization=self.organization,
            name="Meeting Room",
            resource_type="room",
            capacity=10
        )
        self.appointment = Appointment.objects.create(
            organization=self.organization,
            title="Client Meeting",
            description="Quarterly review meeting",
            start_datetime=timezone.now() + timezone.timedelta(days=1),
            end_datetime=timezone.now() + timezone.timedelta(days=1, hours=1),
            duration_minutes=60,
            status="scheduled",
            priority="normal",
            client_name="John Doe",
            client_email="john@example.com",
            assigned_team=self.team,
            location="Office",
            estimated_cost=Decimal('150.00'),
            currency="USD"
        )
    
    def test_appointment_creation(self):
        """Test appointment creation."""
        self.assertEqual(self.appointment.organization, self.organization)
        self.assertEqual(self.appointment.title, "Client Meeting")
        self.assertEqual(self.appointment.description, "Quarterly review meeting")
        self.assertEqual(self.appointment.status, "scheduled")
        self.assertEqual(self.appointment.priority, "normal")
        self.assertEqual(self.appointment.client_name, "John Doe")
        self.assertEqual(self.appointment.client_email, "john@example.com")
        self.assertEqual(self.appointment.assigned_team, self.team)
        self.assertEqual(self.appointment.location, "Office")
        self.assertEqual(self.appointment.estimated_cost, Decimal('150.00'))
        self.assertEqual(self.appointment.currency, "USD")
    
    def test_appointment_str(self):
        """Test appointment string representation."""
        expected = f"Client Meeting - {self.appointment.start_datetime.strftime('%Y-%m-%d %H:%M')}"
        self.assertEqual(str(self.appointment), expected)
    
    def test_appointment_validation(self):
        """Test appointment validation."""
        # Test invalid datetime range
        with self.assertRaises(ValidationError):
            appointment = Appointment(
                organization=self.organization,
                title="Invalid Appointment",
                start_datetime=timezone.now() + timezone.timedelta(days=1),
                end_datetime=timezone.now(),  # End before start
                duration_minutes=60
            )
            appointment.full_clean()


class ScheduleConflictModelTest(TestCase):
    """Test ScheduleConflict model."""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.appointment1 = Appointment.objects.create(
            organization=self.organization,
            title="Meeting 1",
            start_datetime=timezone.now() + timezone.timedelta(days=1),
            end_datetime=timezone.now() + timezone.timedelta(days=1, hours=1),
            duration_minutes=60,
            status="scheduled"
        )
        self.appointment2 = Appointment.objects.create(
            organization=self.organization,
            title="Meeting 2",
            start_datetime=timezone.now() + timezone.timedelta(days=1, minutes=30),
            end_datetime=timezone.now() + timezone.timedelta(days=1, hours=1, minutes=30),
            duration_minutes=60,
            status="scheduled"
        )
        self.conflict = ScheduleConflict.objects.create(
            organization=self.organization,
            conflict_type="time_conflict",
            status="pending",
            primary_appointment=self.appointment1,
            conflicting_appointment=self.appointment2,
            conflict_description="Time overlap between meetings",
            conflict_datetime=self.appointment1.start_datetime,
            impact_level="medium"
        )
    
    def test_schedule_conflict_creation(self):
        """Test schedule conflict creation."""
        self.assertEqual(self.conflict.organization, self.organization)
        self.assertEqual(self.conflict.conflict_type, "time_conflict")
        self.assertEqual(self.conflict.status, "pending")
        self.assertEqual(self.conflict.primary_appointment, self.appointment1)
        self.assertEqual(self.conflict.conflicting_appointment, self.appointment2)
        self.assertEqual(self.conflict.conflict_description, "Time overlap between meetings")
        self.assertEqual(self.conflict.impact_level, "medium")
    
    def test_schedule_conflict_str(self):
        """Test schedule conflict string representation."""
        expected = f"Time Conflict - {self.organization.name}"
        self.assertEqual(str(self.conflict), expected)


class ScheduleRuleModelTest(TestCase):
    """Test ScheduleRule model."""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.rule = ScheduleRule.objects.create(
            organization=self.organization,
            name="Business Hours",
            rule_type="working_hours",
            description="Standard business hours rule",
            is_active=True,
            is_global=True,
            start_time="09:00:00",
            end_time="17:00:00"
        )
    
    def test_schedule_rule_creation(self):
        """Test schedule rule creation."""
        self.assertEqual(self.rule.organization, self.organization)
        self.assertEqual(self.rule.name, "Business Hours")
        self.assertEqual(self.rule.rule_type, "working_hours")
        self.assertEqual(self.rule.description, "Standard business hours rule")
        self.assertTrue(self.rule.is_active)
        self.assertTrue(self.rule.is_global)
        self.assertEqual(self.rule.start_time.strftime('%H:%M'), "09:00")
        self.assertEqual(self.rule.end_time.strftime('%H:%M'), "17:00")
    
    def test_schedule_rule_str(self):
        """Test schedule rule string representation."""
        expected = f"Business Hours (Working Hours) - {self.organization.name}"
        self.assertEqual(str(self.rule), expected)


class ScheduleNotificationModelTest(TestCase):
    """Test ScheduleNotification model."""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="recipient",
            email="recipient@example.com",
            password="testpass123"
        )
        self.notification = ScheduleNotification.objects.create(
            organization=self.organization,
            notification_type="appointment_reminder",
            delivery_method="email",
            subject="Appointment Reminder",
            message="Your appointment is scheduled for tomorrow at 10:00 AM",
            status="pending"
        )
    
    def test_schedule_notification_creation(self):
        """Test schedule notification creation."""
        self.assertEqual(self.notification.organization, self.organization)
        self.assertEqual(self.notification.notification_type, "appointment_reminder")
        self.assertEqual(self.notification.delivery_method, "email")
        self.assertEqual(self.notification.subject, "Appointment Reminder")
        self.assertEqual(self.notification.message, "Your appointment is scheduled for tomorrow at 10:00 AM")
        self.assertEqual(self.notification.status, "pending")
    
    def test_schedule_notification_str(self):
        """Test schedule notification string representation."""
        expected = f"Appointment Reminder - {self.organization.name}"
        self.assertEqual(str(self.notification), expected)


class ScheduleAnalyticsModelTest(TestCase):
    """Test ScheduleAnalytics model."""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.analytics = ScheduleAnalytics.objects.create(
            organization=self.organization,
            period_start=timezone.now().date(),
            period_end=timezone.now().date() + timezone.timedelta(days=30),
            period_type="monthly",
            total_appointments=50,
            completed_appointments=45,
            cancelled_appointments=3,
            no_show_appointments=2,
            total_scheduled_hours=Decimal('200.00'),
            total_available_hours=Decimal('300.00'),
            utilization_rate=Decimal('66.67'),
            total_revenue=Decimal('7500.00'),
            average_appointment_value=Decimal('150.00')
        )
    
    def test_schedule_analytics_creation(self):
        """Test schedule analytics creation."""
        self.assertEqual(self.analytics.organization, self.organization)
        self.assertEqual(self.analytics.period_type, "monthly")
        self.assertEqual(self.analytics.total_appointments, 50)
        self.assertEqual(self.analytics.completed_appointments, 45)
        self.assertEqual(self.analytics.cancelled_appointments, 3)
        self.assertEqual(self.analytics.no_show_appointments, 2)
        self.assertEqual(self.analytics.total_scheduled_hours, Decimal('200.00'))
        self.assertEqual(self.analytics.total_available_hours, Decimal('300.00'))
        self.assertEqual(self.analytics.utilization_rate, Decimal('66.67'))
        self.assertEqual(self.analytics.total_revenue, Decimal('7500.00'))
        self.assertEqual(self.analytics.average_appointment_value, Decimal('150.00'))
    
    def test_schedule_analytics_str(self):
        """Test schedule analytics string representation."""
        expected = f"Analytics - {self.organization.name} (Monthly)"
        self.assertEqual(str(self.analytics), expected)


class ScheduleIntegrationModelTest(TestCase):
    """Test ScheduleIntegration model."""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.integration = ScheduleIntegration.objects.create(
            organization=self.organization,
            name="Google Calendar Integration",
            integration_type="calendar",
            provider_name="Google",
            provider_url="https://calendar.google.com",
            is_active=True,
            sync_enabled=True,
            sync_frequency="hourly",
            sync_status="connected"
        )
    
    def test_schedule_integration_creation(self):
        """Test schedule integration creation."""
        self.assertEqual(self.integration.organization, self.organization)
        self.assertEqual(self.integration.name, "Google Calendar Integration")
        self.assertEqual(self.integration.integration_type, "calendar")
        self.assertEqual(self.integration.provider_name, "Google")
        self.assertEqual(self.integration.provider_url, "https://calendar.google.com")
        self.assertTrue(self.integration.is_active)
        self.assertTrue(self.integration.sync_enabled)
        self.assertEqual(self.integration.sync_frequency, "hourly")
        self.assertEqual(self.integration.sync_status, "connected")
    
    def test_schedule_integration_str(self):
        """Test schedule integration string representation."""
        expected = f"Google Calendar Integration (Calendar) - {self.organization.name}"
        self.assertEqual(str(self.integration), expected)


class SchedulingModelIntegrationTest(TestCase):
    """Integration tests for scheduling models."""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.team = Team.objects.create(
            organization=self.organization,
            name="Test Team"
        )
        self.resource = Resource.objects.create(
            organization=self.organization,
            name="Test Resource",
            resource_type="room",
            capacity=10
        )
        self.template = ScheduleTemplate.objects.create(
            organization=self.organization,
            name="Test Template",
            schedule_type="daily",
            start_time="09:00:00",
            end_time="17:00:00",
            duration_minutes=480
        )
    
    def test_scheduling_workflow(self):
        """Test complete scheduling workflow."""
        # Create appointment
        appointment = Appointment.objects.create(
            organization=self.organization,
            title="Test Appointment",
            start_datetime=timezone.now() + timezone.timedelta(days=1),
            end_datetime=timezone.now() + timezone.timedelta(days=1, hours=1),
            duration_minutes=60,
            status="scheduled",
            client_name="Test Client",
            assigned_team=self.team,
            estimated_cost=Decimal('100.00')
        )
        
        # Add resource requirement
        appointment.required_resources.add(self.resource)
        
        # Add team member
        team_member = TeamMember.objects.create(
            team=self.team,
            user=self.user,
            role="member"
        )
        appointment.assigned_users.add(self.user)
        
        # Create conflict
        conflicting_appointment = Appointment.objects.create(
            organization=self.organization,
            title="Conflicting Appointment",
            start_datetime=timezone.now() + timezone.timedelta(days=1, minutes=30),
            end_datetime=timezone.now() + timezone.timedelta(days=1, hours=1, minutes=30),
            duration_minutes=60,
            status="scheduled"
        )
        
        conflict = ScheduleConflict.objects.create(
            organization=self.organization,
            conflict_type="time_conflict",
            primary_appointment=appointment,
            conflicting_appointment=conflicting_appointment,
            conflict_description="Time overlap",
            conflict_datetime=appointment.start_datetime
        )
        
        # Verify relationships
        self.assertEqual(appointment.assigned_team, self.team)
        self.assertEqual(appointment.required_resources.count(), 1)
        self.assertEqual(appointment.assigned_users.count(), 1)
        self.assertEqual(conflict.primary_appointment, appointment)
        self.assertEqual(conflict.conflicting_appointment, conflicting_appointment)
    
    def test_scheduling_calculations(self):
        """Test scheduling calculations."""
        # Create multiple appointments
        appointment1 = Appointment.objects.create(
            organization=self.organization,
            title="Appointment 1",
            start_datetime=timezone.now() + timezone.timedelta(days=1),
            end_datetime=timezone.now() + timezone.timedelta(days=1, hours=1),
            duration_minutes=60,
            status="completed",
            actual_cost=Decimal('100.00')
        )
        
        appointment2 = Appointment.objects.create(
            organization=self.organization,
            title="Appointment 2",
            start_datetime=timezone.now() + timezone.timedelta(days=2),
            end_datetime=timezone.now() + timezone.timedelta(days=2, hours=2),
            duration_minutes=120,
            status="completed",
            actual_cost=Decimal('200.00')
        )
        
        # Create analytics
        analytics = ScheduleAnalytics.objects.create(
            organization=self.organization,
            period_start=timezone.now().date(),
            period_end=timezone.now().date() + timezone.timedelta(days=30),
            period_type="monthly",
            total_appointments=2,
            completed_appointments=2,
            total_scheduled_hours=Decimal('3.00'),  # 60 + 120 minutes = 180 minutes = 3 hours
            total_available_hours=Decimal('8.00'),
            utilization_rate=Decimal('37.50'),  # 3/8 * 100
            total_revenue=Decimal('300.00'),
            average_appointment_value=Decimal('150.00')
        )
        
        # Verify calculations
        self.assertEqual(analytics.total_appointments, 2)
        self.assertEqual(analytics.completed_appointments, 2)
        self.assertEqual(analytics.total_scheduled_hours, Decimal('3.00'))
        self.assertEqual(analytics.total_revenue, Decimal('300.00'))
        self.assertEqual(analytics.average_appointment_value, Decimal('150.00'))
