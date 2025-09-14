# Scheduling Management System

A comprehensive scheduling management system for the TidyGen ERP platform, providing complete appointment scheduling, resource management, team coordination, and conflict resolution capabilities.

## Features

### Core Scheduling Management
- **Schedule Templates**: Reusable templates for creating recurring schedules
- **Resource Management**: Manage rooms, equipment, vehicles, and other schedulable resources
- **Team Management**: Organize teams with members, roles, and availability
- **Appointment Scheduling**: Complete appointment lifecycle management
- **Conflict Detection**: Automatic detection and resolution of scheduling conflicts
- **Business Rules**: Configurable scheduling rules and constraints

### Advanced Features
- **Recurring Appointments**: Support for recurring appointment patterns
- **Resource Availability**: Real-time resource availability tracking
- **Team Coordination**: Multi-user appointment assignments and coordination
- **Notification System**: Multi-channel notifications for scheduling events
- **Analytics & Reporting**: Comprehensive scheduling analytics and insights
- **Integration Support**: Connect with external calendar and booking systems

### Automation & Intelligence
- **Conflict Resolution**: Automated conflict detection and resolution workflows
- **Smart Scheduling**: Intelligent scheduling suggestions and optimizations
- **Reminder System**: Automated appointment reminders and notifications
- **Maintenance Scheduling**: Resource maintenance and availability management
- **Performance Analytics**: Utilization tracking and performance metrics

## Models

### ScheduleTemplate
Template for creating recurring schedules with predefined settings.

**Key Fields:**
- `organization`: Organization reference
- `name`: Template name
- `description`: Template description
- `schedule_type`: Type (daily, weekly, monthly, yearly, custom)
- `recurrence_interval`: Interval for recurrence
- `recurrence_days`: Days of week for weekly schedules
- `recurrence_dates`: Specific dates for custom schedules
- `start_time`: Template start time
- `end_time`: Template end time
- `duration_minutes`: Appointment duration
- `break_duration_minutes`: Break duration
- `break_start_time`: Break start time
- `max_capacity`: Maximum capacity
- `min_advance_booking_hours`: Minimum advance booking time
- `max_advance_booking_days`: Maximum advance booking time
- `base_price`: Base price for appointments
- `currency`: Currency code
- `is_active`: Whether template is active
- `is_default`: Whether template is default

### Resource
Resources that can be scheduled (rooms, equipment, vehicles, etc.).

**Key Fields:**
- `organization`: Organization reference
- `name`: Resource name
- `resource_type`: Type (room, equipment, vehicle, person, service, other)
- `description`: Resource description
- `location`: Resource location
- `capacity`: Resource capacity
- `specifications`: Technical specifications (JSON)
- `is_active`: Whether resource is active
- `is_available`: Whether resource is available
- `maintenance_schedule`: Maintenance schedule (JSON)
- `last_maintenance`: Last maintenance date
- `next_maintenance`: Next maintenance date
- `hourly_rate`: Hourly rate
- `daily_rate`: Daily rate
- `currency`: Currency code
- `image_url`: Resource image URL
- `documents`: Resource documents (JSON)

### Team
Teams that can be assigned to appointments or tasks.

**Key Fields:**
- `organization`: Organization reference
- `name`: Team name
- `description`: Team description
- `is_active`: Whether team is active
- `max_members`: Maximum team members
- `team_lead`: Team lead user
- `skills`: Team skills (JSON)
- `specializations`: Team specializations (JSON)
- `availability_schedule`: Team availability schedule (JSON)

### TeamMember
Members of teams with their roles and availability.

**Key Fields:**
- `team`: Team reference
- `user`: User reference
- `role`: Member role (member, lead, specialist, trainee, consultant)
- `joined_date`: Date joined team
- `is_active`: Whether member is active
- `skills`: Member skills (JSON)
- `certifications`: Member certifications (JSON)
- `availability_schedule`: Member availability schedule (JSON)
- `max_hours_per_week`: Maximum hours per week

### Appointment
Scheduled appointments with clients, teams, and resources.

**Key Fields:**
- `organization`: Organization reference
- `title`: Appointment title
- `description`: Appointment description
- `start_datetime`: Start date and time
- `end_datetime`: End date and time
- `duration_minutes`: Duration in minutes
- `status`: Status (scheduled, confirmed, in_progress, completed, cancelled, no_show, rescheduled)
- `priority`: Priority (low, normal, high, urgent)
- `client_name`: Client name
- `client_email`: Client email
- `client_phone`: Client phone
- `client_notes`: Client notes
- `assigned_team`: Assigned team
- `assigned_users`: Assigned users (M2M)
- `required_resources`: Required resources (M2M)
- `location`: Appointment location
- `is_virtual`: Whether appointment is virtual
- `meeting_url`: Meeting URL for virtual appointments
- `is_recurring`: Whether appointment is recurring
- `recurrence_rule`: Recurrence rule (JSON)
- `parent_appointment`: Parent appointment for recurring instances
- `estimated_cost`: Estimated cost
- `actual_cost`: Actual cost
- `currency`: Currency code
- `is_billable`: Whether appointment is billable
- `reminder_sent`: Whether reminder was sent
- `reminder_datetime`: Reminder date and time
- `completion_notes`: Completion notes
- `completion_rating`: Completion rating (1-5)
- `completion_feedback`: Completion feedback
- `external_id`: External system ID
- `external_url`: External system URL

### ScheduleConflict
Tracks scheduling conflicts and resolutions.

**Key Fields:**
- `organization`: Organization reference
- `conflict_type`: Type (double_booking, resource_conflict, team_conflict, time_conflict, location_conflict, capacity_exceeded)
- `status`: Resolution status (pending, resolved, ignored, escalated)
- `primary_appointment`: Primary conflicting appointment
- `conflicting_appointment`: Conflicting appointment
- `conflict_description`: Conflict description
- `conflict_datetime`: Conflict date and time
- `affected_resources`: Affected resources (M2M)
- `affected_users`: Affected users (M2M)
- `resolution_notes`: Resolution notes
- `resolved_by`: User who resolved conflict
- `resolved_at`: Resolution date and time
- `impact_level`: Impact level (low, medium, high, critical)

### ScheduleRule
Business rules for scheduling (working hours, holidays, etc.).

**Key Fields:**
- `organization`: Organization reference
- `name`: Rule name
- `rule_type`: Type (working_hours, holiday, break_time, maintenance, blackout, capacity_limit, advance_booking, cancellation)
- `description`: Rule description
- `is_active`: Whether rule is active
- `is_global`: Whether rule applies globally
- `applies_to_resources`: Resources rule applies to (M2M)
- `applies_to_users`: Users rule applies to (M2M)
- `applies_to_teams`: Teams rule applies to (M2M)
- `start_date`: Rule start date
- `end_date`: Rule end date
- `start_time`: Rule start time
- `end_time`: Rule end time
- `is_recurring`: Whether rule is recurring
- `recurrence_rule`: Recurrence rule (JSON)
- `parameters`: Rule parameters (JSON)

### ScheduleNotification
Notifications related to scheduling events.

**Key Fields:**
- `organization`: Organization reference
- `notification_type`: Type (appointment_created, appointment_updated, appointment_cancelled, appointment_reminder, conflict_detected, resource_unavailable, team_member_unavailable, schedule_change)
- `delivery_method`: Delivery method (email, sms, push, in_app)
- `recipients`: Notification recipients (M2M)
- `subject`: Notification subject
- `message`: Notification message
- `related_appointment`: Related appointment
- `related_conflict`: Related conflict
- `scheduled_at`: Scheduled delivery time
- `sent_at`: Sent timestamp
- `status`: Notification status (pending, sent, failed, cancelled)
- `delivery_details`: Delivery details (JSON)
- `error_message`: Error message if failed

### ScheduleAnalytics
Analytics and reporting for scheduling data.

**Key Fields:**
- `organization`: Organization reference
- `period_start`: Period start date
- `period_end`: Period end date
- `period_type`: Period type (daily, weekly, monthly, quarterly, yearly)
- `total_appointments`: Total appointments
- `completed_appointments`: Completed appointments
- `cancelled_appointments`: Cancelled appointments
- `no_show_appointments`: No-show appointments
- `total_scheduled_hours`: Total scheduled hours
- `total_available_hours`: Total available hours
- `utilization_rate`: Utilization rate
- `resource_utilization`: Resource utilization data (JSON)
- `team_utilization`: Team utilization data (JSON)
- `total_conflicts`: Total conflicts
- `resolved_conflicts`: Resolved conflicts
- `conflict_resolution_time`: Average conflict resolution time
- `total_revenue`: Total revenue
- `average_appointment_value`: Average appointment value
- `metrics`: Additional metrics (JSON)

### ScheduleIntegration
Integration with external scheduling systems.

**Key Fields:**
- `organization`: Organization reference
- `name`: Integration name
- `integration_type`: Type (calendar, booking, crm, erp, communication, payment)
- `provider_name`: Provider name
- `provider_url`: Provider URL
- `is_active`: Whether integration is active
- `configuration`: Integration configuration (JSON)
- `api_key`: API key
- `api_secret`: API secret
- `access_token`: Access token
- `refresh_token`: Refresh token
- `token_expires_at`: Token expiration
- `sync_enabled`: Whether sync is enabled
- `sync_frequency`: Sync frequency (realtime, hourly, daily, weekly)
- `last_sync`: Last sync timestamp
- `sync_status`: Sync status (connected, disconnected, error, syncing)
- `error_message`: Error message
- `retry_count`: Retry count
- `max_retries`: Maximum retries

## API Endpoints

### Schedule Templates
- `GET /api/scheduling/schedule-templates/` - List schedule templates
- `POST /api/scheduling/schedule-templates/` - Create schedule template
- `GET /api/scheduling/schedule-templates/{id}/` - Get schedule template
- `PUT /api/scheduling/schedule-templates/{id}/` - Update schedule template
- `DELETE /api/scheduling/schedule-templates/{id}/` - Delete schedule template
- `POST /api/scheduling/schedule-templates/{id}/duplicate/` - Duplicate template
- `GET /api/scheduling/schedule-templates/active/` - Get active templates

### Resources
- `GET /api/scheduling/resources/` - List resources
- `POST /api/scheduling/resources/` - Create resource
- `GET /api/scheduling/resources/{id}/` - Get resource
- `PUT /api/scheduling/resources/{id}/` - Update resource
- `DELETE /api/scheduling/resources/{id}/` - Delete resource
- `POST /api/scheduling/resources/{id}/set-availability/` - Set availability
- `POST /api/scheduling/resources/{id}/schedule-maintenance/` - Schedule maintenance
- `GET /api/scheduling/resources/available/` - Get available resources
- `GET /api/scheduling/resources/by-type/` - Get resources by type

### Teams
- `GET /api/scheduling/teams/` - List teams
- `POST /api/scheduling/teams/` - Create team
- `GET /api/scheduling/teams/{id}/` - Get team
- `PUT /api/scheduling/teams/{id}/` - Update team
- `DELETE /api/scheduling/teams/{id}/` - Delete team
- `POST /api/scheduling/teams/{id}/add-member/` - Add team member
- `POST /api/scheduling/teams/{id}/remove-member/` - Remove team member
- `GET /api/scheduling/teams/{id}/members/` - Get team members
- `GET /api/scheduling/teams/{id}/availability/` - Get team availability

### Team Members
- `GET /api/scheduling/team-members/` - List team members
- `POST /api/scheduling/team-members/` - Create team member
- `GET /api/scheduling/team-members/{id}/` - Get team member
- `PUT /api/scheduling/team-members/{id}/` - Update team member
- `DELETE /api/scheduling/team-members/{id}/` - Delete team member

### Appointments
- `GET /api/scheduling/appointments/` - List appointments
- `POST /api/scheduling/appointments/` - Create appointment
- `GET /api/scheduling/appointments/{id}/` - Get appointment
- `PUT /api/scheduling/appointments/{id}/` - Update appointment
- `DELETE /api/scheduling/appointments/{id}/` - Delete appointment
- `POST /api/scheduling/appointments/{id}/confirm/` - Confirm appointment
- `POST /api/scheduling/appointments/{id}/cancel/` - Cancel appointment
- `POST /api/scheduling/appointments/{id}/reschedule/` - Reschedule appointment
- `POST /api/scheduling/appointments/{id}/complete/` - Complete appointment
- `GET /api/scheduling/appointments/upcoming/` - Get upcoming appointments
- `GET /api/scheduling/appointments/overdue/` - Get overdue appointments
- `GET /api/scheduling/appointments/today/` - Get today's appointments
- `GET /api/scheduling/appointments/conflicts/` - Check for conflicts

### Schedule Conflicts
- `GET /api/scheduling/conflicts/` - List conflicts
- `POST /api/scheduling/conflicts/` - Create conflict
- `GET /api/scheduling/conflicts/{id}/` - Get conflict
- `PUT /api/scheduling/conflicts/{id}/` - Update conflict
- `DELETE /api/scheduling/conflicts/{id}/` - Delete conflict
- `POST /api/scheduling/conflicts/{id}/resolve/` - Resolve conflict
- `POST /api/scheduling/conflicts/{id}/escalate/` - Escalate conflict
- `GET /api/scheduling/conflicts/unresolved/` - Get unresolved conflicts

### Schedule Rules
- `GET /api/scheduling/rules/` - List schedule rules
- `POST /api/scheduling/rules/` - Create schedule rule
- `GET /api/scheduling/rules/{id}/` - Get schedule rule
- `PUT /api/scheduling/rules/{id}/` - Update schedule rule
- `DELETE /api/scheduling/rules/{id}/` - Delete schedule rule
- `GET /api/scheduling/rules/active/` - Get active rules

### Schedule Notifications
- `GET /api/scheduling/notifications/` - List notifications
- `POST /api/scheduling/notifications/` - Create notification
- `GET /api/scheduling/notifications/{id}/` - Get notification
- `PUT /api/scheduling/notifications/{id}/` - Update notification
- `DELETE /api/scheduling/notifications/{id}/` - Delete notification
- `POST /api/scheduling/notifications/{id}/send/` - Send notification
- `GET /api/scheduling/notifications/pending/` - Get pending notifications

### Schedule Analytics
- `GET /api/scheduling/analytics/` - List analytics
- `POST /api/scheduling/analytics/` - Create analytics
- `GET /api/scheduling/analytics/{id}/` - Get analytics
- `PUT /api/scheduling/analytics/{id}/` - Update analytics
- `DELETE /api/scheduling/analytics/{id}/` - Delete analytics

### Schedule Integrations
- `GET /api/scheduling/integrations/` - List integrations
- `POST /api/scheduling/integrations/` - Create integration
- `GET /api/scheduling/integrations/{id}/` - Get integration
- `PUT /api/scheduling/integrations/{id}/` - Update integration
- `DELETE /api/scheduling/integrations/{id}/` - Delete integration
- `POST /api/scheduling/integrations/{id}/test-connection/` - Test connection
- `POST /api/scheduling/integrations/{id}/sync/` - Sync integration
- `GET /api/scheduling/integrations/active/` - Get active integrations

### Dashboard and Summary
- `GET /api/scheduling/dashboard/` - Get scheduling dashboard data
- `GET /api/scheduling/summary/` - Get scheduling summary data

## Usage Examples

### Creating a Schedule Template

```python
from apps.scheduling.models import ScheduleTemplate
from apps.organizations.models import Organization

organization = Organization.objects.get(name="My Company")
template = ScheduleTemplate.objects.create(
    organization=organization,
    name="Weekly Team Meeting",
    description="Weekly team standup meeting",
    schedule_type="weekly",
    recurrence_interval=1,
    recurrence_days=[1, 2, 3, 4, 5],  # Monday to Friday
    start_time="09:00:00",
    end_time="10:00:00",
    duration_minutes=60,
    max_capacity=15,
    base_price=Decimal('0.00'),
    currency="USD",
    is_active=True
)
```

### Creating a Resource

```python
from apps.scheduling.models import Resource

resource = Resource.objects.create(
    organization=organization,
    name="Conference Room A",
    resource_type="room",
    description="Large conference room with projector and whiteboard",
    location="Building 1, Floor 2, Room 201",
    capacity=20,
    specifications={
        "features": ["projector", "whiteboard", "video_conferencing"],
        "amenities": ["coffee_machine", "water_dispenser"],
        "notes": "Wheelchair accessible"
    },
    hourly_rate=Decimal('50.00'),
    daily_rate=Decimal('300.00'),
    currency="USD",
    is_active=True,
    is_available=True
)
```

### Creating a Team

```python
from apps.scheduling.models import Team, TeamMember
from apps.core.models import User

# Create team
team = Team.objects.create(
    organization=organization,
    name="Development Team",
    description="Software development team",
    team_lead=User.objects.get(username="team_lead"),
    max_members=8,
    skills=["python", "django", "react", "postgresql"],
    specializations=["web_development", "api_development"],
    availability_schedule={
        "monday": {"start": "09:00", "end": "17:00"},
        "tuesday": {"start": "09:00", "end": "17:00"},
        "wednesday": {"start": "09:00", "end": "17:00"},
        "thursday": {"start": "09:00", "end": "17:00"},
        "friday": {"start": "09:00", "end": "17:00"},
        "saturday": {"start": "10:00", "end": "14:00"},
        "sunday": {"start": "10:00", "end": "14:00"}
    }
)

# Add team member
team_member = TeamMember.objects.create(
    team=team,
    user=User.objects.get(username="developer1"),
    role="member",
    skills=["python", "django"],
    certifications=["aws_certified", "python_certified"],
    max_hours_per_week=40
)
```

### Scheduling an Appointment

```python
from apps.scheduling.models import Appointment
from datetime import datetime, timedelta

appointment = Appointment.objects.create(
    organization=organization,
    title="Client Meeting",
    description="Quarterly review meeting with client",
    start_datetime=datetime.now() + timedelta(days=1, hours=10),
    end_datetime=datetime.now() + timedelta(days=1, hours=11),
    duration_minutes=60,
    status="scheduled",
    priority="normal",
    client_name="John Doe",
    client_email="john@example.com",
    client_phone="+1-555-0123",
    client_notes="Prefers morning meetings",
    assigned_team=team,
    location="Conference Room A",
    is_virtual=False,
    estimated_cost=Decimal('150.00'),
    currency="USD",
    is_billable=True
)

# Assign users and resources
appointment.assigned_users.add(User.objects.get(username="developer1"))
appointment.required_resources.add(resource)
```

### Creating a Schedule Rule

```python
from apps.scheduling.models import ScheduleRule

rule = ScheduleRule.objects.create(
    organization=organization,
    name="Business Hours",
    rule_type="working_hours",
    description="Standard business hours rule",
    is_active=True,
    is_global=True,
    start_time="09:00:00",
    end_time="17:00:00",
    is_recurring=True,
    recurrence_rule={
        "frequency": "weekly",
        "days": [1, 2, 3, 4, 5]  # Monday to Friday
    }
)
```

### Checking for Conflicts

```python
from apps.scheduling.models import ScheduleConflict

# Check for time conflicts
conflicting_appointments = Appointment.objects.filter(
    organization=organization,
    start_datetime__lt=appointment.end_datetime,
    end_datetime__gt=appointment.start_datetime,
    status__in=['scheduled', 'confirmed', 'in_progress']
).exclude(id=appointment.id)

if conflicting_appointments.exists():
    # Create conflict record
    conflict = ScheduleConflict.objects.create(
        organization=organization,
        conflict_type="time_conflict",
        primary_appointment=appointment,
        conflicting_appointment=conflicting_appointments.first(),
        conflict_description="Time overlap detected",
        conflict_datetime=appointment.start_datetime,
        impact_level="medium"
    )
```

### Generating Analytics

```python
from apps.scheduling.models import ScheduleAnalytics
from django.db.models import Count, Sum, Avg

# Calculate analytics for current month
appointments = Appointment.objects.filter(
    organization=organization,
    start_datetime__date__range=[start_date, end_date]
)

analytics = ScheduleAnalytics.objects.create(
    organization=organization,
    period_start=start_date,
    period_end=end_date,
    period_type="monthly",
    total_appointments=appointments.count(),
    completed_appointments=appointments.filter(status='completed').count(),
    cancelled_appointments=appointments.filter(status='cancelled').count(),
    no_show_appointments=appointments.filter(status='no_show').count(),
    total_scheduled_hours=Decimal(str(appointments.aggregate(
        total=Sum('duration_minutes')
    )['total'] or 0) / 60),
    total_revenue=appointments.filter(
        status='completed'
    ).aggregate(
        total=Sum('actual_cost')
    )['total'] or Decimal('0.00')
)
```

## Signals

The scheduling system includes comprehensive signals for automated operations:

### ScheduleTemplate Signals
- `post_save`: Creates default settings and manages default template
- `pre_save`: Validates time settings and calculates duration

### Resource Signals
- `post_save`: Sets default specifications and availability
- `pre_save`: Validates capacity and checks maintenance schedule

### Team Signals
- `post_save`: Sets default availability schedule
- `TeamMember.post_save`: Sets default availability from team

### Appointment Signals
- `post_save`: Checks for conflicts, sets reminders, sends notifications
- `pre_save`: Calculates duration and validates datetime range
- `post_save` (update): Checks for conflicts and sends update notifications

### ScheduleConflict Signals
- `post_save`: Sends notifications for high-impact conflicts
- `pre_save`: Sets resolution timestamp

### ScheduleRule Signals
- `post_save`: Applies rules to existing appointments

### ScheduleNotification Signals
- `post_save`: Sends immediate notifications

### ScheduleAnalytics Signals
- `post_save`: Calculates additional metrics

### ScheduleIntegration Signals
- `post_save`: Tests integration connection

## Admin Interface

The scheduling system includes a comprehensive Django admin interface with:

- **List Views**: Optimized list displays with filtering and search
- **Detail Views**: Organized field sets for easy editing
- **Inline Editing**: Related objects can be edited inline
- **Custom Actions**: Bulk operations for common tasks
- **Read-only Fields**: Automatic timestamp and calculated fields
- **Validation**: Form validation and error handling

## Testing

The scheduling system includes comprehensive tests covering:

- **Model Tests**: All model creation, validation, and relationships
- **Integration Tests**: Complete scheduling workflows
- **Calculation Tests**: Scheduling calculations and analytics
- **Signal Tests**: Automated signal operations
- **API Tests**: REST API endpoints and responses

## Security

The scheduling system implements several security measures:

- **Data Validation**: Comprehensive input validation and sanitization
- **Access Control**: Role-based permissions for scheduling operations
- **Audit Logging**: Complete audit trail for all scheduling changes
- **Conflict Resolution**: Secure conflict resolution workflows
- **Integration Security**: Secure API key and token management

## Performance

The scheduling system is optimized for performance with:

- **Database Indexing**: Strategic indexes on frequently queried fields
- **Query Optimization**: Efficient queries with select_related and prefetch_related
- **Caching**: Strategic caching of frequently accessed data
- **Background Processing**: Asynchronous processing for large operations
- **Pagination**: Efficient pagination for large datasets

## Maintenance

Regular maintenance tasks include:

- **Data Cleanup**: Archiving old scheduling data
- **Conflict Resolution**: Monitoring and resolving scheduling conflicts
- **Integration Monitoring**: Monitoring external system integrations
- **Performance Monitoring**: Tracking system performance
- **Backup Verification**: Ensuring data backup integrity

## Support

For support and questions:

- **Documentation**: Comprehensive API and user documentation
- **Logging**: Detailed logging for troubleshooting
- **Error Handling**: Graceful error handling and recovery
- **Monitoring**: System health monitoring and alerts
- **Updates**: Regular updates and bug fixes
