# HR Management Module

A comprehensive human resources management system for the iNEAT ERP platform that handles employee lifecycle, attendance tracking, leave management, payroll processing, performance reviews, training, and policy management.

## Features

### 👥 **Employee Management**
- **Employee Profiles**: Complete employee information with personal, professional, and contact details
- **Department Structure**: Hierarchical department organization with managers and budgets
- **Position Management**: Job positions with requirements, salary ranges, and reporting structure
- **Employee Lifecycle**: From hiring to termination with probation tracking
- **Document Management**: Employee document storage with expiry tracking and verification

### ⏰ **Attendance & Time Tracking**
- **Time Tracking**: Check-in/check-out with break time management
- **Overtime Calculation**: Automatic overtime hours calculation
- **Attendance Status**: Present, absent, late, half-day, on leave, holiday tracking
- **Approval Workflow**: Manager approval for attendance records
- **Analytics**: Attendance trends, late arrivals, overtime analysis

### 🏖️ **Leave Management**
- **Leave Types**: Configurable leave types (annual, sick, personal, etc.)
- **Leave Requests**: Employee leave request submission and approval workflow
- **Leave Balance**: Automatic leave balance calculation and carryover
- **Approval Process**: Multi-level approval with rejection reasons
- **Leave Analytics**: Leave trends, department-wise analysis, upcoming leaves

### 💰 **Payroll Management**
- **Payroll Periods**: Configurable payroll periods (weekly, bi-weekly, monthly)
- **Salary Components**: Basic salary, overtime, allowances, bonuses, commissions
- **Deductions**: Tax, social security, health insurance, other deductions
- **Automatic Calculations**: Gross pay, total deductions, net pay calculation
- **Payroll Processing**: Batch processing with status tracking

### 📊 **Performance Management**
- **Performance Reviews**: Annual, quarterly, probation, project-based reviews
- **Rating System**: 5-point scale for different performance criteria
- **Goal Setting**: Goals achieved and goals for next period
- **Review Workflow**: Reviewer assignment and employee acknowledgment
- **Performance Analytics**: Performance trends, top performers, improvement areas

### 🎓 **Training & Development**
- **Training Programs**: Internal, external, online, workshop, conference training
- **Enrollment Management**: Employee enrollment with status tracking
- **Completion Tracking**: Training completion with scores and certificates
- **Feedback System**: Training feedback and rating collection
- **Training Analytics**: Completion rates, popular programs, cost analysis

### 📋 **Policy Management**
- **Policy Creation**: HR policy creation with version control
- **Policy Types**: General, leave, attendance, code of conduct, safety policies
- **Acknowledgment System**: Employee policy acknowledgment tracking
- **Effective Dates**: Policy effective and expiry date management
- **Approval Workflow**: Policy approval process

## Models

### Core Models

#### Department
- Department hierarchy with parent-child relationships
- Manager assignment and budget management
- Cost center and status tracking
- Employee count and sub-department management

#### Position
- Job position with title, code, and description
- Department assignment and reporting structure
- Job level and employment type classification
- Salary ranges and requirements
- Skills, education, and experience requirements

#### Employee
- Complete employee profile extending User model
- Personal information (DOB, gender, marital status, nationality)
- Contact information and emergency contacts
- Employment details (position, department, manager)
- Compensation and benefits information
- Skills, certifications, and notes

#### Attendance
- Daily attendance tracking with check-in/check-out times
- Break time management
- Automatic hours and overtime calculation
- Status tracking (present, absent, late, etc.)
- Manager approval workflow

#### LeaveType
- Configurable leave types with rules
- Maximum days per year and carryover settings
- Paid/unpaid leave classification
- Approval requirements and advance notice
- Monthly accrual settings

#### LeaveRequest
- Employee leave request submission
- Approval workflow with rejection reasons
- Leave period and total days calculation
- Status tracking (pending, approved, rejected, cancelled)

#### PayrollPeriod
- Payroll period definition with start/end dates
- Period type (weekly, bi-weekly, monthly, quarterly)
- Processing status and pay date
- Batch processing capabilities

#### Payroll
- Individual employee payroll records
- Salary components and deductions
- Automatic total calculations
- Status tracking (draft, approved, paid, cancelled)

#### PerformanceReview
- Performance review with multiple rating criteria
- Review period and type classification
- Strengths, areas for improvement, and goals
- Employee acknowledgment system

#### Training
- Training program definition
- Scheduling and location management
- Cost tracking and participant limits
- Status management (planned, open, in progress, completed)

#### TrainingEnrollment
- Employee training enrollment
- Completion tracking with scores
- Certificate issuance
- Feedback and rating collection

#### Document
- Employee document storage
- Document type classification
- Expiry date tracking and verification
- Access control (public/private)

#### Policy
- HR policy management
- Version control and effective dates
- Approval workflow
- Acknowledgment requirements

#### PolicyAcknowledgment
- Employee policy acknowledgment tracking
- Timestamp and IP address logging
- Compliance monitoring

## API Endpoints

### Departments
- `GET /api/v1/hr/departments/` - List departments
- `POST /api/v1/hr/departments/` - Create department
- `GET /api/v1/hr/departments/{id}/` - Get department details
- `PUT /api/v1/hr/departments/{id}/` - Update department
- `DELETE /api/v1/hr/departments/{id}/` - Delete department

### Positions
- `GET /api/v1/hr/positions/` - List positions
- `POST /api/v1/hr/positions/` - Create position
- `GET /api/v1/hr/positions/{id}/` - Get position details
- `PUT /api/v1/hr/positions/{id}/` - Update position
- `DELETE /api/v1/hr/positions/{id}/` - Delete position

### Employees
- `GET /api/v1/hr/employees/` - List employees
- `POST /api/v1/hr/employees/` - Create employee
- `GET /api/v1/hr/employees/{id}/` - Get employee details
- `PUT /api/v1/hr/employees/{id}/` - Update employee
- `DELETE /api/v1/hr/employees/{id}/` - Delete employee
- `POST /api/v1/hr/employees/{id}/record_attendance/` - Record attendance
- `POST /api/v1/hr/employees/{id}/request_leave/` - Request leave
- `POST /api/v1/hr/employees/{id}/upload_document/` - Upload document
- `POST /api/v1/hr/employees/{id}/conduct_review/` - Conduct performance review
- `POST /api/v1/hr/employees/{id}/enroll_training/` - Enroll in training
- `POST /api/v1/hr/employees/{id}/change_status/` - Change employment status

### Attendance
- `GET /api/v1/hr/attendance/` - List attendance records
- `POST /api/v1/hr/attendance/` - Create attendance record
- `GET /api/v1/hr/attendance/{id}/` - Get attendance details
- `PUT /api/v1/hr/attendance/{id}/` - Update attendance record
- `DELETE /api/v1/hr/attendance/{id}/` - Delete attendance record
- `POST /api/v1/hr/attendance/{id}/approve/` - Approve attendance
- `GET /api/v1/hr/attendance/analytics/` - Get attendance analytics

### Leave Types
- `GET /api/v1/hr/leave-types/` - List leave types
- `POST /api/v1/hr/leave-types/` - Create leave type
- `GET /api/v1/hr/leave-types/{id}/` - Get leave type details
- `PUT /api/v1/hr/leave-types/{id}/` - Update leave type
- `DELETE /api/v1/hr/leave-types/{id}/` - Delete leave type

### Leave Requests
- `GET /api/v1/hr/leave-requests/` - List leave requests
- `POST /api/v1/hr/leave-requests/` - Create leave request
- `GET /api/v1/hr/leave-requests/{id}/` - Get leave request details
- `PUT /api/v1/hr/leave-requests/{id}/` - Update leave request
- `DELETE /api/v1/hr/leave-requests/{id}/` - Delete leave request
- `POST /api/v1/hr/leave-requests/{id}/approve/` - Approve leave request
- `POST /api/v1/hr/leave-requests/{id}/reject/` - Reject leave request
- `GET /api/v1/hr/leave-requests/analytics/` - Get leave analytics

### Payroll Periods
- `GET /api/v1/hr/payroll-periods/` - List payroll periods
- `POST /api/v1/hr/payroll-periods/` - Create payroll period
- `GET /api/v1/hr/payroll-periods/{id}/` - Get payroll period details
- `PUT /api/v1/hr/payroll-periods/{id}/` - Update payroll period
- `DELETE /api/v1/hr/payroll-periods/{id}/` - Delete payroll period
- `POST /api/v1/hr/payroll-periods/{id}/process_payroll/` - Process payroll

### Payrolls
- `GET /api/v1/hr/payrolls/` - List payrolls
- `POST /api/v1/hr/payrolls/` - Create payroll
- `GET /api/v1/hr/payrolls/{id}/` - Get payroll details
- `PUT /api/v1/hr/payrolls/{id}/` - Update payroll
- `DELETE /api/v1/hr/payrolls/{id}/` - Delete payroll
- `GET /api/v1/hr/payrolls/analytics/` - Get payroll analytics

### Performance Reviews
- `GET /api/v1/hr/performance-reviews/` - List performance reviews
- `POST /api/v1/hr/performance-reviews/` - Create performance review
- `GET /api/v1/hr/performance-reviews/{id}/` - Get performance review details
- `PUT /api/v1/hr/performance-reviews/{id}/` - Update performance review
- `DELETE /api/v1/hr/performance-reviews/{id}/` - Delete performance review
- `POST /api/v1/hr/performance-reviews/{id}/acknowledge/` - Acknowledge review
- `GET /api/v1/hr/performance-reviews/analytics/` - Get performance analytics

### Trainings
- `GET /api/v1/hr/trainings/` - List trainings
- `POST /api/v1/hr/trainings/` - Create training
- `GET /api/v1/hr/trainings/{id}/` - Get training details
- `PUT /api/v1/hr/trainings/{id}/` - Update training
- `DELETE /api/v1/hr/trainings/{id}/` - Delete training

### Training Enrollments
- `GET /api/v1/hr/training-enrollments/` - List training enrollments
- `POST /api/v1/hr/training-enrollments/` - Create training enrollment
- `GET /api/v1/hr/training-enrollments/{id}/` - Get training enrollment details
- `PUT /api/v1/hr/training-enrollments/{id}/` - Update training enrollment
- `DELETE /api/v1/hr/training-enrollments/{id}/` - Delete training enrollment

### Documents
- `GET /api/v1/hr/documents/` - List documents
- `POST /api/v1/hr/documents/` - Create document
- `GET /api/v1/hr/documents/{id}/` - Get document details
- `PUT /api/v1/hr/documents/{id}/` - Update document
- `DELETE /api/v1/hr/documents/{id}/` - Delete document
- `POST /api/v1/hr/documents/{id}/verify/` - Verify document

### Policies
- `GET /api/v1/hr/policies/` - List policies
- `POST /api/v1/hr/policies/` - Create policy
- `GET /api/v1/hr/policies/{id}/` - Get policy details
- `PUT /api/v1/hr/policies/{id}/` - Update policy
- `DELETE /api/v1/hr/policies/{id}/` - Delete policy
- `POST /api/v1/hr/policies/{id}/acknowledge/` - Acknowledge policy

### Policy Acknowledgments
- `GET /api/v1/hr/policy-acknowledgments/` - List policy acknowledgments
- `POST /api/v1/hr/policy-acknowledgments/` - Create policy acknowledgment
- `GET /api/v1/hr/policy-acknowledgments/{id}/` - Get policy acknowledgment details
- `PUT /api/v1/hr/policy-acknowledgments/{id}/` - Update policy acknowledgment
- `DELETE /api/v1/hr/policy-acknowledgments/{id}/` - Delete policy acknowledgment

### Dashboard
- `GET /api/v1/hr/dashboard/overview/` - Get HR dashboard overview
- `GET /api/v1/hr/dashboard/analytics/` - Get HR analytics

## Filters

The HR module includes comprehensive filtering capabilities:

### Employee Filters
- **Basic**: Employee ID, badge number, gender, marital status, employment status
- **Contact**: Personal email, personal phone, city, state, country
- **Employment**: Position, department, manager, hire date, termination date
- **Work Arrangement**: Work location, remote work, work schedule
- **Compensation**: Salary, hourly rate, currency ranges
- **Benefits**: Health insurance, dental insurance, vision insurance, retirement plan
- **Additional**: Nationality, skills, probation status

### Attendance Filters
- **Employee**: Employee selection
- **Date Ranges**: Date, check-in time, check-out time ranges
- **Status**: Present, absent, late, half-day, on leave, holiday
- **Hours**: Total hours, overtime hours ranges
- **Approval**: Approved by, approval status

### Leave Request Filters
- **Employee**: Employee selection
- **Leave Type**: Leave type selection
- **Status**: Pending, approved, rejected, cancelled
- **Date Ranges**: Start date, end date, approval date ranges
- **Approval**: Requested by, approved by

### Payroll Filters
- **Employee**: Employee selection
- **Payroll Period**: Payroll period selection
- **Status**: Draft, approved, paid, cancelled
- **Amount Ranges**: Basic salary, gross pay, net pay ranges
- **Hours**: Hours worked, overtime hours ranges

### Performance Review Filters
- **Employee**: Employee selection
- **Reviewer**: Reviewer selection
- **Review Type**: Annual, quarterly, probation, project, informal
- **Status**: Draft, in progress, completed, acknowledged
- **Date Ranges**: Review period, review date ranges
- **Ratings**: Overall rating, individual criteria ratings
- **Acknowledgment**: Employee acknowledgment status

### Training Filters
- **Basic**: Title, description, training type, status
- **Scheduling**: Start date, end date, duration ranges
- **Cost**: Cost per participant, total budget ranges
- **Location**: Location, instructor, online status
- **Participants**: Maximum participants ranges

### Advanced Analytics Filters
- **Date Range Presets**: Today, this week, this month, etc.
- **Custom Date Ranges**: Flexible date filtering
- **Department Filters**: Department-specific analytics
- **Status Filters**: Status-based analytics

## Signals

The HR module includes automated signals for:

### Employee Management
- Automatic probation end date setting (90 days from hire date)
- Employee data validation and uniqueness checks
- Employee status updates based on leave requests

### Attendance Management
- Automatic hours and overtime calculation
- Break time deduction from total hours
- Attendance data validation

### Leave Management
- Leave request validation (dates, past dates)
- Employee status updates when leave is approved
- Leave balance calculations

### Payroll Management
- Automatic gross pay, deductions, and net pay calculation
- Payroll data validation (negative amounts)
- Payroll period status updates

### Performance Management
- Automatic overall rating calculation from individual ratings
- Performance review data validation
- Review status updates

### Training Management
- Training enrollment status updates
- Training completion tracking
- Training status updates based on dates

### Document Management
- Document verification timestamp updates
- Document expiry tracking and notifications

### Policy Management
- Policy acknowledgment timestamp updates
- Policy status updates based on effective dates

## Permissions

The HR module uses the following permission system:

- **IsAuthenticated**: User must be logged in
- **IsOrganizationMember**: User must be a member of the organization
- **Organization-specific data**: All data is filtered by organization

## Testing

Comprehensive test coverage includes:

- **Model Tests**: Test model creation, validation, and relationships
- **API Tests**: Test all CRUD operations and custom endpoints
- **Signal Tests**: Test automated calculations and updates
- **Filter Tests**: Test filtering functionality
- **Permission Tests**: Test access control

Run tests with:
```bash
python manage.py test apps.hr
```

## Usage Examples

### Creating an Employee
```python
# Create employee
employee_data = {
    'user': user_id,
    'employee_id': 'EMP001',
    'position': position_id,
    'department': department_id,
    'hire_date': '2024-01-01',
    'salary': '75000.00'
}

response = requests.post('/api/v1/hr/employees/', json=employee_data)
```

### Recording Attendance
```python
# Record attendance
attendance_data = {
    'date': '2024-01-15',
    'check_in_time': '09:00:00',
    'check_out_time': '17:00:00',
    'status': 'present'
}

response = requests.post(f'/api/v1/hr/employees/{employee_id}/record_attendance/', json=attendance_data)
```

### Requesting Leave
```python
# Request leave
leave_data = {
    'leave_type': leave_type_id,
    'start_date': '2024-02-01',
    'end_date': '2024-02-05',
    'total_days': 5,
    'reason': 'Vacation'
}

response = requests.post(f'/api/v1/hr/employees/{employee_id}/request_leave/', json=leave_data)
```

### Approving Leave Request
```python
# Approve leave request
response = requests.post(f'/api/v1/hr/leave-requests/{leave_request_id}/approve/')
```

### Creating Payroll
```python
# Create payroll
payroll_data = {
    'employee': employee_id,
    'payroll_period': payroll_period_id,
    'basic_salary': '6250.00',
    'hours_worked': '160.00',
    'overtime_hours': '10.00',
    'overtime_pay': '500.00',
    'allowances': '200.00',
    'tax_deduction': '800.00',
    'social_security': '300.00',
    'health_insurance': '200.00'
}

response = requests.post('/api/v1/hr/payrolls/', json=payroll_data)
```

### Conducting Performance Review
```python
# Conduct performance review
review_data = {
    'review_period_start': '2024-01-01',
    'review_period_end': '2024-12-31',
    'review_date': '2024-12-15',
    'review_type': 'annual',
    'overall_rating': 4,
    'quality_rating': 4,
    'productivity_rating': 5,
    'teamwork_rating': 4,
    'communication_rating': 4,
    'strengths': 'Excellent technical skills and team collaboration',
    'areas_for_improvement': 'Could improve time management',
    'goals_achieved': 'Completed all assigned projects on time',
    'goals_for_next_period': 'Lead a new project initiative'
}

response = requests.post(f'/api/v1/hr/employees/{employee_id}/conduct_review/', json=review_data)
```

## Integration

The HR module integrates with:

- **Organizations**: Self-hosted support
- **Users**: User authentication and permissions
- **Core**: Base models and permissions
- **Finance**: Payroll integration
- **Sales**: Employee-client relationships

## Future Enhancements

Planned features include:

- **Recruitment Management**: Job postings, applications, interviews
- **Employee Self-Service**: Employee portal for self-service functions
- **Advanced Reporting**: Custom reports and dashboards
- **Mobile App**: Mobile HR management
- **Integration APIs**: Third-party system integrations
- **Workflow Automation**: Automated HR workflows
- **Compliance Management**: Regulatory compliance tracking
- **Benefits Administration**: Comprehensive benefits management
- **Succession Planning**: Career development and succession planning
- **Employee Engagement**: Surveys and feedback systems
