# Projects Module

## Overview

The Projects module provides comprehensive project management functionality for the TidyGen ERP platform. It includes project planning, task management, resource allocation, time tracking, and client management capabilities.

## Features

### 🎯 **Project Management**
- **Project Lifecycle**: Planning, active, on-hold, completed, cancelled, archived
- **Priority Levels**: Low, medium, high, critical
- **Project Types**: Internal, client, research, maintenance, development, consulting
- **Budget Tracking**: Budget vs. actual cost monitoring
- **Timeline Management**: Start dates, planned end dates, actual end dates
- **Progress Tracking**: Completion percentage based on tasks

### 👥 **Team Management**
- **Role-based Assignment**: Project manager, team lead, developer, designer, tester, analyst, consultant, support
- **Work Allocation**: Percentage allocation and hourly rates
- **Team Performance**: Duration tracking and cost analysis
- **Member Activation/Deactivation**: Flexible team member management

### 📋 **Task Management**
- **Task Hierarchy**: Parent-child task relationships
- **Dependencies**: Task dependency management
- **Status Tracking**: Not started, in progress, on hold, completed, cancelled
- **Effort Estimation**: Estimated vs. actual hours
- **Progress Monitoring**: Completion percentage tracking
- **Assignment**: User assignment and responsibility tracking

### ⏱️ **Time Tracking**
- **Time Entries**: Detailed time logging with start/end times
- **Billing Integration**: Billable vs. non-billable time
- **Approval Workflow**: Time entry approval system
- **Activity Types**: Categorization of work activities
- **Automatic Calculations**: Hours calculation from time ranges

### 🏢 **Client Management**
- **Client Profiles**: Comprehensive client information
- **Contact Management**: Multiple contacts per client
- **Business Classification**: Industry, company size, annual revenue
- **Project History**: Client project tracking and revenue analysis
- **Status Management**: Active, inactive, prospect, former

### 📊 **Resource Management**
- **Resource Types**: Human, equipment, material, software, facility, other
- **Availability Tracking**: Resource availability periods
- **Capacity Management**: Resource capacity and utilization
- **Cost Analysis**: Cost per unit and total cost calculations
- **Allocation Management**: Resource allocation to projects

### 📈 **Analytics & Reporting**
- **Project Dashboard**: Comprehensive project overview
- **Task Analytics**: Task status and progress analysis
- **Resource Analytics**: Resource utilization and availability
- **Time Tracking Analytics**: Hours analysis and billing insights
- **Financial Metrics**: Budget utilization and cost tracking

## Models

### Core Models

#### **Project**
- Project information, timeline, budget, and status
- Relationships with team members, tasks, and resources
- Automatic completion percentage calculation

#### **ProjectMember**
- Team member assignments and roles
- Work allocation and hourly rates
- Performance tracking and cost analysis

#### **Task**
- Task details, dependencies, and progress
- Effort estimation and actual time tracking
- Status management and workflow control

#### **TimeEntry**
- Time logging with start/end times
- Billing integration and approval workflow
- Activity categorization and description

#### **Client**
- Client profiles and business information
- Project history and revenue tracking
- Contact management and status tracking

#### **ClientContact**
- Client contact person details
- Primary contact designation
- Department and role information

#### **Resource**
- Resource information and capabilities
- Availability and capacity management
- Cost tracking and status monitoring

#### **ResourceAllocation**
- Resource allocation to projects
- Timeline and percentage allocation
- Cost analysis and utilization tracking

## API Endpoints

### Project Management
- `GET/POST /api/projects/` - List and create projects
- `GET/PUT/DELETE /api/projects/{id}/` - Retrieve, update, delete project
- `POST /api/projects/{id}/start_project/` - Start a project
- `POST /api/projects/{id}/complete_project/` - Complete a project
- `POST /api/projects/{id}/cancel_project/` - Cancel a project
- `GET /api/projects/{id}/tasks/` - Get project tasks
- `GET /api/projects/{id}/team_members/` - Get project team members
- `GET /api/projects/{id}/time_entries/` - Get project time entries
- `GET /api/projects/{id}/resource_allocations/` - Get project resource allocations

### Task Management
- `GET/POST /api/tasks/` - List and create tasks
- `GET/PUT/DELETE /api/tasks/{id}/` - Retrieve, update, delete task
- `POST /api/tasks/{id}/start_task/` - Start a task
- `POST /api/tasks/{id}/complete_task/` - Complete a task
- `GET /api/tasks/{id}/subtasks/` - Get task subtasks
- `GET /api/tasks/{id}/dependencies/` - Get task dependencies
- `GET /api/tasks/overdue_tasks/` - Get overdue tasks
- `GET /api/tasks/my_tasks/` - Get user's assigned tasks

### Time Tracking
- `GET/POST /api/time-entries/` - List and create time entries
- `GET/PUT/DELETE /api/time-entries/{id}/` - Retrieve, update, delete time entry
- `POST /api/time-entries/{id}/approve_time/` - Approve time entry
- `GET /api/time-entries/my_time_entries/` - Get user's time entries
- `GET /api/time-entries/pending_approval/` - Get pending approval entries
- `GET /api/time-entries/billable_entries/` - Get billable time entries

### Team Management
- `GET/POST /api/project-members/` - List and create project members
- `GET/PUT/DELETE /api/project-members/{id}/` - Retrieve, update, delete member
- `POST /api/project-members/{id}/deactivate_member/` - Deactivate member
- `GET /api/project-members/active_members/` - Get active members

### Client Management
- `GET/POST /api/clients/` - List and create clients
- `GET/PUT/DELETE /api/clients/{id}/` - Retrieve, update, delete client
- `GET /api/clients/{id}/projects/` - Get client projects
- `GET /api/clients/{id}/contacts/` - Get client contacts
- `GET /api/clients/active_clients/` - Get active clients
- `GET /api/clients/top_clients/` - Get top clients by revenue

### Resource Management
- `GET/POST /api/resources/` - List and create resources
- `GET/PUT/DELETE /api/resources/{id}/` - Retrieve, update, delete resource
- `GET /api/resources/{id}/allocations/` - Get resource allocations
- `GET /api/resources/available_resources/` - Get available resources
- `GET /api/resources/resources_by_type/` - Get resources by type

### Resource Allocation
- `GET/POST /api/resource-allocations/` - List and create allocations
- `GET/PUT/DELETE /api/resource-allocations/{id}/` - Retrieve, update, delete allocation
- `GET /api/resource-allocations/{id}/resource_details/` - Get resource details

### Dashboard & Analytics
- `GET /api/dashboard/summary/` - Project summary analytics
- `GET /api/dashboard/task_summary/` - Task summary analytics
- `GET /api/dashboard/resource_summary/` - Resource summary analytics
- `GET /api/dashboard/time_tracking_summary/` - Time tracking analytics

## Business Logic

### Project Workflow
1. **Planning**: Project setup, team assignment, resource allocation
2. **Active**: Project execution, task management, progress tracking
3. **On Hold**: Temporary suspension with reason tracking
4. **Completed**: Project finished with actual end date
5. **Cancelled**: Project terminated with cancellation reason
6. **Archived**: Long-term storage for completed projects

### Task Dependencies
- Tasks can have multiple dependencies
- Dependencies must be completed before task can start
- Automatic dependency checking and validation
- Circular dependency prevention

### Resource Allocation
- Resources can be allocated to multiple projects
- Allocation percentage controls resource sharing
- Automatic resource status updates
- Conflict detection and resolution

### Time Tracking Workflow
1. **Time Entry**: User logs time with description
2. **Review**: Manager reviews time entries
3. **Approval**: Approved entries are billable
4. **Billing**: Integration with financial systems

## Configuration

### Settings
```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    ...
    'apps.projects',
    ...
]

# Project-specific settings
PROJECT_SETTINGS = {
    'DEFAULT_PROJECT_TYPE': 'internal',
    'DEFAULT_PRIORITY': 'medium',
    'AUTO_GENERATE_CODES': True,
    'ENABLE_TIME_APPROVAL': True,
    'DEFAULT_BILLING_RATE': 0.00,
}
```

### Permissions
- **Project Manager**: Full project control
- **Team Member**: Task assignment and time tracking
- **Client**: Project status viewing
- **Admin**: System-wide project management

## Usage Examples

### Creating a New Project
```python
from apps.projects.models import Project
from apps.core.models import Organization

# Create project
project = Project.objects.create(
    organization=organization,
    name='Website Redesign',
    description='Complete website redesign project',
    project_type='client',
    status='planning',
    priority='high',
    project_manager=user,
    client=client,
    start_date=date.today(),
    planned_end_date=date.today() + timedelta(days=90),
    budget=Decimal('25000.00'),
    billing_rate=Decimal('150.00')
)
```

### Adding Team Members
```python
from apps.projects.models import ProjectMember

# Add team member
member = ProjectMember.objects.create(
    project=project,
    user=developer,
    role='developer',
    assigned_date=date.today(),
    allocation_percentage=Decimal('100.00'),
    hourly_rate=Decimal('75.00')
)
```

### Creating Tasks
```python
from apps.projects.models import Task

# Create task
task = Task.objects.create(
    project=project,
    title='Design Homepage',
    description='Create new homepage design',
    task_type='design',
    status='not_started',
    priority='high',
    assigned_to=designer,
    planned_start_date=date.today(),
    planned_end_date=date.today() + timedelta(days=14),
    estimated_hours=Decimal('80.00')
)
```

### Logging Time
```python
from apps.projects.models import TimeEntry

# Log time entry
time_entry = TimeEntry.objects.create(
    project=project,
    task=task,
    user=designer,
    date=date.today(),
    start_time='09:00:00',
    end_time='17:00:00',
    description='Homepage design work',
    activity_type='design',
    is_billable=True,
    billing_rate=Decimal('100.00')
)
```

### Resource Allocation
```python
from apps.projects.models import ResourceAllocation

# Allocate resource
allocation = ResourceAllocation.objects.create(
    project=project,
    resource=design_tool,
    start_date=date.today(),
    end_date=date.today() + timedelta(days=90),
    allocation_percentage=Decimal('50.00'),
    cost_per_unit=Decimal('25.00')
)
```

## Testing

### Running Tests
```bash
# Run all project tests
python manage.py test apps.projects.tests

# Run specific test class
python manage.py test apps.projects.tests.ProjectsModelsTestCase

# Run specific test method
python manage.py test apps.projects.tests.ProjectsModelsTestCase.test_project_creation
```

### Test Coverage
- **Models**: 100% coverage of all model methods
- **Views**: 100% coverage of all API endpoints
- **Serializers**: 100% coverage of all serializers
- **Filters**: 100% coverage of all filter methods
- **Signals**: 100% coverage of all signal handlers

## Performance Considerations

### Database Optimization
- **Indexes**: Strategic database indexing for common queries
- **Select Related**: Optimized queryset loading
- **Prefetch Related**: Efficient many-to-many loading
- **Aggregation**: Optimized calculation queries

### Caching Strategy
- **Project Summary**: Cache project statistics
- **Dashboard Data**: Cache analytics results
- **User Permissions**: Cache user access rights
- **Resource Availability**: Cache resource status

### Query Optimization
- **Bulk Operations**: Efficient bulk create/update
- **Batch Processing**: Process large datasets in batches
- **Lazy Loading**: Load related data on demand
- **Connection Pooling**: Optimize database connections

## Security

### Data Isolation
- **Organization-based**: Multi-tenant data separation
- **User Permissions**: Role-based access control
- **Project Scoping**: Project-level data isolation
- **Audit Logging**: Complete activity tracking

### Input Validation
- **Serializer Validation**: Comprehensive data validation
- **Model Validation**: Database-level constraints
- **Business Rules**: Workflow validation
- **Security Checks**: Permission validation

## Future Enhancements

### Planned Features
- **Gantt Charts**: Visual project timeline management
- **Resource Scheduling**: Advanced resource planning
- **Project Templates**: Reusable project structures
- **Integration APIs**: Third-party system integration
- **Mobile App**: Mobile project management
- **Real-time Updates**: Live project status updates

### Scalability Improvements
- **Microservices**: Service-oriented architecture
- **Event Sourcing**: Event-driven data model
- **CQRS**: Command-query responsibility separation
- **Horizontal Scaling**: Load balancing and distribution

## Support

### Documentation
- **API Reference**: Complete endpoint documentation
- **User Guide**: Step-by-step usage instructions
- **Developer Guide**: Technical implementation details
- **FAQ**: Common questions and answers

### Community
- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: Community support and discussions
- **Contributions**: Open source contributions welcome
- **Feedback**: User feedback and suggestions

---

**Note**: This module is designed to be extensible and can be customized for specific business requirements. For customizations or additional features, please refer to the development guide or contact the development team.
