"""
Comprehensive tests for HR management functionality.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta

from apps.hr.models import (
    Department, Position, Employee, Attendance, LeaveType, LeaveRequest,
    PayrollPeriod, Payroll, PerformanceReview, Training, TrainingEnrollment,
    Document, Policy, PolicyAcknowledgment
)

User = get_user_model()


class HRModelTests(TestCase):
    """Test HR models."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.organization.members.create(
            user=self.user,
            role='admin'
        )
    
    def test_department_creation(self):
        """Test department creation."""
        department = Department.objects.create(
            organization=self.organization,
            name="Engineering",
            code="ENG",
            description="Software Engineering Department",
            manager=self.user
        )
        
        self.assertEqual(department.name, "Engineering")
        self.assertEqual(department.code, "ENG")
        self.assertEqual(department.manager, self.user)
        self.assertTrue(department.is_active)
    
    def test_position_creation(self):
        """Test position creation."""
        department = Department.objects.create(
            organization=self.organization,
            name="Engineering",
            manager=self.user
        )
        
        position = Position.objects.create(
            organization=self.organization,
            title="Senior Software Engineer",
            code="SSE",
            department=department,
            job_level="senior",
            employment_type="full_time",
            min_salary=Decimal('80000.00'),
            max_salary=Decimal('120000.00')
        )
        
        self.assertEqual(position.title, "Senior Software Engineer")
        self.assertEqual(position.department, department)
        self.assertEqual(position.job_level, "senior")
        self.assertEqual(position.employment_type, "full_time")
    
    def test_employee_creation(self):
        """Test employee creation."""
        department = Department.objects.create(
            organization=self.organization,
            name="Engineering"
        )
        
        position = Position.objects.create(
            organization=self.organization,
            title="Software Engineer",
            department=department
        )
        
        employee = Employee.objects.create(
            user=self.user,
            organization=self.organization,
            employee_id="EMP001",
            position=position,
            department=department,
            hire_date=date.today(),
            salary=Decimal('75000.00')
        )
        
        self.assertEqual(employee.user, self.user)
        self.assertEqual(employee.employee_id, "EMP001")
        self.assertEqual(employee.position, position)
        self.assertEqual(employee.department, department)
        self.assertEqual(employee.employment_status, "active")
    
    def test_attendance_creation(self):
        """Test attendance creation."""
        employee = Employee.objects.create(
            user=self.user,
            organization=self.organization,
            employee_id="EMP001",
            hire_date=date.today()
        )
        
        attendance = Attendance.objects.create(
            employee=employee,
            date=date.today(),
            check_in_time="09:00:00",
            check_out_time="17:00:00",
            status="present"
        )
        
        self.assertEqual(attendance.employee, employee)
        self.assertEqual(attendance.date, date.today())
        self.assertEqual(attendance.status, "present")
    
    def test_leave_type_creation(self):
        """Test leave type creation."""
        leave_type = LeaveType.objects.create(
            organization=self.organization,
            name="Annual Leave",
            code="AL",
            max_days_per_year=25,
            is_paid=True,
            requires_approval=True
        )
        
        self.assertEqual(leave_type.name, "Annual Leave")
        self.assertEqual(leave_type.max_days_per_year, 25)
        self.assertTrue(leave_type.is_paid)
        self.assertTrue(leave_type.requires_approval)
    
    def test_leave_request_creation(self):
        """Test leave request creation."""
        employee = Employee.objects.create(
            user=self.user,
            organization=self.organization,
            employee_id="EMP001",
            hire_date=date.today()
        )
        
        leave_type = LeaveType.objects.create(
            organization=self.organization,
            name="Annual Leave"
        )
        
        leave_request = LeaveRequest.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=5),
            total_days=5,
            reason="Vacation",
            requested_by=self.user
        )
        
        self.assertEqual(leave_request.employee, employee)
        self.assertEqual(leave_request.leave_type, leave_type)
        self.assertEqual(leave_request.total_days, 5)
        self.assertEqual(leave_request.status, "pending")
    
    def test_payroll_creation(self):
        """Test payroll creation."""
        employee = Employee.objects.create(
            user=self.user,
            organization=self.organization,
            employee_id="EMP001",
            hire_date=date.today(),
            salary=Decimal('75000.00')
        )
        
        payroll_period = PayrollPeriod.objects.create(
            organization=self.organization,
            name="January 2024",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            pay_date=date(2024, 2, 1)
        )
        
        payroll = Payroll.objects.create(
            employee=employee,
            payroll_period=payroll_period,
            basic_salary=Decimal('6250.00'),
            hours_worked=Decimal('160.00'),
            gross_pay=Decimal('6250.00'),
            total_deductions=Decimal('1500.00'),
            net_pay=Decimal('4750.00')
        )
        
        self.assertEqual(payroll.employee, employee)
        self.assertEqual(payroll.payroll_period, payroll_period)
        self.assertEqual(payroll.basic_salary, Decimal('6250.00'))
        self.assertEqual(payroll.net_pay, Decimal('4750.00'))


class HRAPITests(APITestCase):
    """Test HR API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.organization.members.create(
            user=self.user,
            role='admin'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_department_create(self):
        """Test department creation via API."""
        url = reverse('department-list')
        data = {
            'name': 'Engineering',
            'code': 'ENG',
            'description': 'Software Engineering Department'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Department.objects.count(), 1)
        self.assertEqual(Department.objects.get().name, 'Engineering')
    
    def test_position_create(self):
        """Test position creation via API."""
        department = Department.objects.create(
            organization=self.organization,
            name="Engineering"
        )
        
        url = reverse('position-list')
        data = {
            'title': 'Senior Software Engineer',
            'code': 'SSE',
            'department': department.id,
            'job_level': 'senior',
            'employment_type': 'full_time',
            'min_salary': '80000.00',
            'max_salary': '120000.00'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Position.objects.count(), 1)
        self.assertEqual(Position.objects.get().title, 'Senior Software Engineer')
    
    def test_employee_create(self):
        """Test employee creation via API."""
        department = Department.objects.create(
            organization=self.organization,
            name="Engineering"
        )
        
        position = Position.objects.create(
            organization=self.organization,
            title="Software Engineer",
            department=department
        )
        
        url = reverse('employee-list')
        data = {
            'user': self.user.id,
            'employee_id': 'EMP001',
            'position': position.id,
            'department': department.id,
            'hire_date': date.today().isoformat(),
            'salary': '75000.00'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Employee.objects.count(), 1)
        self.assertEqual(Employee.objects.get().employee_id, 'EMP001')
    
    def test_attendance_record(self):
        """Test attendance recording via API."""
        employee = Employee.objects.create(
            user=self.user,
            organization=self.organization,
            employee_id="EMP001",
            hire_date=date.today()
        )
        
        url = reverse('employee-record-attendance', kwargs={'pk': employee.pk})
        data = {
            'date': date.today().isoformat(),
            'check_in_time': '09:00:00',
            'check_out_time': '17:00:00',
            'status': 'present'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Attendance.objects.count(), 1)
    
    def test_leave_request_create(self):
        """Test leave request creation via API."""
        employee = Employee.objects.create(
            user=self.user,
            organization=self.organization,
            employee_id="EMP001",
            hire_date=date.today()
        )
        
        leave_type = LeaveType.objects.create(
            organization=self.organization,
            name="Annual Leave"
        )
        
        url = reverse('employee-request-leave', kwargs={'pk': employee.pk})
        data = {
            'leave_type': leave_type.id,
            'start_date': (date.today() + timedelta(days=1)).isoformat(),
            'end_date': (date.today() + timedelta(days=5)).isoformat(),
            'total_days': 5,
            'reason': 'Vacation'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LeaveRequest.objects.count(), 1)
    
    def test_leave_request_approve(self):
        """Test leave request approval via API."""
        employee = Employee.objects.create(
            user=self.user,
            organization=self.organization,
            employee_id="EMP001",
            hire_date=date.today()
        )
        
        leave_type = LeaveType.objects.create(
            organization=self.organization,
            name="Annual Leave"
        )
        
        leave_request = LeaveRequest.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=5),
            total_days=5,
            reason="Vacation",
            requested_by=self.user
        )
        
        url = reverse('leaverequest-approve', kwargs={'pk': leave_request.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        leave_request.refresh_from_db()
        self.assertEqual(leave_request.status, 'approved')
        self.assertEqual(leave_request.approved_by, self.user)
    
    def test_employee_status_change(self):
        """Test employee status change via API."""
        employee = Employee.objects.create(
            user=self.user,
            organization=self.organization,
            employee_id="EMP001",
            hire_date=date.today()
        )
        
        url = reverse('employee-change-status', kwargs={'pk': employee.pk})
        data = {'status': 'on_leave'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        employee.refresh_from_db()
        self.assertEqual(employee.employment_status, 'on_leave')
    
    def test_hr_dashboard(self):
        """Test HR dashboard endpoint."""
        # Create test data
        department = Department.objects.create(
            organization=self.organization,
            name="Engineering"
        )
        
        employee = Employee.objects.create(
            user=self.user,
            organization=self.organization,
            employee_id="EMP001",
            department=department,
            hire_date=date.today()
        )
        
        url = reverse('hr-dashboard-overview')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_employees', response.data)
        self.assertIn('active_employees', response.data)
        self.assertIn('employees_by_department', response.data)
    
    def test_hr_analytics(self):
        """Test HR analytics endpoint."""
        # Create test data
        employee = Employee.objects.create(
            user=self.user,
            organization=self.organization,
            employee_id="EMP001",
            hire_date=date.today()
        )
        
        url = reverse('hr-dashboard-analytics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_employees', response.data)
        self.assertIn('employee_growth_rate', response.data)
        self.assertIn('gender_distribution', response.data)


class HRSignalTests(TestCase):
    """Test HR signals."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.organization.members.create(
            user=self.user,
            role='admin'
        )
    
    def test_employee_probation_end_date(self):
        """Test automatic probation end date setting."""
        employee = Employee.objects.create(
            user=self.user,
            organization=self.organization,
            employee_id="EMP001",
            hire_date=date.today()
        )
        
        # Check that probation end date was set (90 days from hire date)
        expected_probation_end = employee.hire_date + timedelta(days=90)
        self.assertEqual(employee.probation_end_date, expected_probation_end)
    
    def test_attendance_hours_calculation(self):
        """Test automatic attendance hours calculation."""
        employee = Employee.objects.create(
            user=self.user,
            organization=self.organization,
            employee_id="EMP001",
            hire_date=date.today()
        )
        
        attendance = Attendance.objects.create(
            employee=employee,
            date=date.today(),
            check_in_time="09:00:00",
            check_out_time="17:00:00"
        )
        
        # Check that total hours were calculated (8 hours)
        self.assertEqual(attendance.total_hours, 8.0)
        self.assertEqual(attendance.overtime_hours, 0.0)
    
    def test_attendance_overtime_calculation(self):
        """Test overtime calculation for attendance."""
        employee = Employee.objects.create(
            user=self.user,
            organization=self.organization,
            employee_id="EMP001",
            hire_date=date.today()
        )
        
        attendance = Attendance.objects.create(
            employee=employee,
            date=date.today(),
            check_in_time="09:00:00",
            check_out_time="19:00:00"  # 10 hours
        )
        
        # Check that overtime was calculated (2 hours)
        self.assertEqual(attendance.total_hours, 10.0)
        self.assertEqual(attendance.overtime_hours, 2.0)
    
    def test_payroll_totals_calculation(self):
        """Test automatic payroll totals calculation."""
        employee = Employee.objects.create(
            user=self.user,
            organization=self.organization,
            employee_id="EMP001",
            hire_date=date.today()
        )
        
        payroll_period = PayrollPeriod.objects.create(
            organization=self.organization,
            name="January 2024",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            pay_date=date(2024, 2, 1)
        )
        
        payroll = Payroll.objects.create(
            employee=employee,
            payroll_period=payroll_period,
            basic_salary=Decimal('5000.00'),
            overtime_pay=Decimal('500.00'),
            allowances=Decimal('200.00'),
            bonuses=Decimal('300.00'),
            tax_deduction=Decimal('800.00'),
            social_security=Decimal('300.00'),
            health_insurance=Decimal('200.00')
        )
        
        # Check that totals were calculated
        self.assertEqual(payroll.gross_pay, Decimal('6000.00'))  # 5000 + 500 + 200 + 300
        self.assertEqual(payroll.total_deductions, Decimal('1300.00'))  # 800 + 300 + 200
        self.assertEqual(payroll.net_pay, Decimal('4700.00'))  # 6000 - 1300
    
    def test_leave_request_employee_status_update(self):
        """Test employee status update when leave is approved."""
        employee = Employee.objects.create(
            user=self.user,
            organization=self.organization,
            employee_id="EMP001",
            hire_date=date.today()
        )
        
        leave_type = LeaveType.objects.create(
            organization=self.organization,
            name="Annual Leave"
        )
        
        leave_request = LeaveRequest.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            total_days=5,
            reason="Vacation",
            requested_by=self.user
        )
        
        # Approve the leave request
        leave_request.status = 'approved'
        leave_request.approved_by = self.user
        leave_request.approved_at = timezone.now()
        leave_request.save()
        
        # Check that employee status was updated to on_leave
        employee.refresh_from_db()
        self.assertEqual(employee.employment_status, 'on_leave')


class HRFilterTests(TestCase):
    """Test HR filters."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.organization.members.create(
            user=self.user,
            role='admin'
        )
    
    def test_employee_status_filter(self):
        """Test employee status filtering."""
        employee1 = Employee.objects.create(
            user=self.user,
            organization=self.organization,
            employee_id="EMP001",
            employment_status='active',
            hire_date=date.today()
        )
        
        employee2 = Employee.objects.create(
            user=self.user,
            organization=self.organization,
            employee_id="EMP002",
            employment_status='on_leave',
            hire_date=date.today()
        )
        
        from apps.hr.filters import EmployeeFilter
        
        # Test active filter
        filter_data = {'employment_status': 'active'}
        filtered_employees = EmployeeFilter(filter_data, queryset=Employee.objects.all()).qs
        self.assertEqual(filtered_employees.count(), 1)
        self.assertEqual(filtered_employees.first(), employee1)
        
        # Test on_leave filter
        filter_data = {'employment_status': 'on_leave'}
        filtered_employees = EmployeeFilter(filter_data, queryset=Employee.objects.all()).qs
        self.assertEqual(filtered_employees.count(), 1)
        self.assertEqual(filtered_employees.first(), employee2)
    
    def test_employee_department_filter(self):
        """Test employee department filtering."""
        department1 = Department.objects.create(
            organization=self.organization,
            name="Engineering"
        )
        
        department2 = Department.objects.create(
            organization=self.organization,
            name="Marketing"
        )
        
        employee1 = Employee.objects.create(
            user=self.user,
            organization=self.organization,
            employee_id="EMP001",
            department=department1,
            hire_date=date.today()
        )
        
        employee2 = Employee.objects.create(
            user=self.user,
            organization=self.organization,
            employee_id="EMP002",
            department=department2,
            hire_date=date.today()
        )
        
        from apps.hr.filters import EmployeeFilter
        
        # Test department filter
        filter_data = {'department': department1.id}
        filtered_employees = EmployeeFilter(filter_data, queryset=Employee.objects.all()).qs
        self.assertEqual(filtered_employees.count(), 1)
        self.assertEqual(filtered_employees.first(), employee1)
    
    def test_attendance_status_filter(self):
        """Test attendance status filtering."""
        employee = Employee.objects.create(
            user=self.user,
            organization=self.organization,
            employee_id="EMP001",
            hire_date=date.today()
        )
        
        attendance1 = Attendance.objects.create(
            employee=employee,
            date=date.today(),
            status='present'
        )
        
        attendance2 = Attendance.objects.create(
            employee=employee,
            date=date.today() - timedelta(days=1),
            status='absent'
        )
        
        from apps.hr.filters import AttendanceFilter
        
        # Test present filter
        filter_data = {'status': 'present'}
        filtered_attendance = AttendanceFilter(filter_data, queryset=Attendance.objects.all()).qs
        self.assertEqual(filtered_attendance.count(), 1)
        self.assertEqual(filtered_attendance.first(), attendance1)
        
        # Test absent filter
        filter_data = {'status': 'absent'}
        filtered_attendance = AttendanceFilter(filter_data, queryset=Attendance.objects.all()).qs
        self.assertEqual(filtered_attendance.count(), 1)
        self.assertEqual(filtered_attendance.first(), attendance2)
    
    def test_leave_request_status_filter(self):
        """Test leave request status filtering."""
        employee = Employee.objects.create(
            user=self.user,
            organization=self.organization,
            employee_id="EMP001",
            hire_date=date.today()
        )
        
        leave_type = LeaveType.objects.create(
            organization=self.organization,
            name="Annual Leave"
        )
        
        leave_request1 = LeaveRequest.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=5),
            total_days=5,
            reason="Vacation",
            requested_by=self.user,
            status='pending'
        )
        
        leave_request2 = LeaveRequest.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=15),
            total_days=5,
            reason="Sick leave",
            requested_by=self.user,
            status='approved'
        )
        
        from apps.hr.filters import LeaveRequestFilter
        
        # Test pending filter
        filter_data = {'status': 'pending'}
        filtered_requests = LeaveRequestFilter(filter_data, queryset=LeaveRequest.objects.all()).qs
        self.assertEqual(filtered_requests.count(), 1)
        self.assertEqual(filtered_requests.first(), leave_request1)
        
        # Test approved filter
        filter_data = {'status': 'approved'}
        filtered_requests = LeaveRequestFilter(filter_data, queryset=LeaveRequest.objects.all()).qs
        self.assertEqual(filtered_requests.count(), 1)
        self.assertEqual(filtered_requests.first(), leave_request2)
