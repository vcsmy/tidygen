"""
HR management views for iNEAT ERP platform.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, F, Sum, Avg, Max, Min
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from apps.core.permissions import IsOrganizationMember
from apps.hr.models import (
    Department, Position, Employee, Attendance, LeaveType, LeaveRequest,
    PayrollPeriod, Payroll, PerformanceReview, Training, TrainingEnrollment,
    Document, Policy, PolicyAcknowledgment
)
from apps.hr.serializers import (
    DepartmentSerializer, PositionSerializer, EmployeeSerializer, AttendanceSerializer,
    LeaveTypeSerializer, LeaveRequestSerializer, PayrollPeriodSerializer, PayrollSerializer,
    PerformanceReviewSerializer, TrainingSerializer, TrainingEnrollmentSerializer,
    DocumentSerializer, PolicySerializer, PolicyAcknowledgmentSerializer,
    HRDashboardSerializer, HRAnalyticsSerializer, AttendanceAnalyticsSerializer,
    PayrollAnalyticsSerializer, LeaveAnalyticsSerializer, PerformanceAnalyticsSerializer,
    TrainingAnalyticsSerializer
)
from apps.hr.filters import (
    DepartmentFilter, PositionFilter, EmployeeFilter, AttendanceFilter,
    LeaveTypeFilter, LeaveRequestFilter, PayrollPeriodFilter, PayrollFilter,
    PerformanceReviewFilter, TrainingFilter, TrainingEnrollmentFilter,
    DocumentFilter, PolicyFilter, PolicyAcknowledgmentFilter,
    HRAnalyticsFilter, AttendanceAnalyticsFilter
)


class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Department model."""
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DepartmentFilter
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created']
    ordering = ['name']
    
    def get_queryset(self):
        return Department.objects.all().organization
        ).select_related('manager', 'parent_department').prefetch_related('employees')
    
    def perform_create(self, serializer):
        organization = self.request.user.organization_memberships.first().organization
        serializer.save(organization=organization)


class PositionViewSet(viewsets.ModelViewSet):
    """ViewSet for Position model."""
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PositionFilter
    search_fields = ['title', 'code', 'description']
    ordering_fields = ['title', 'created']
    ordering = ['title']
    
    def get_queryset(self):
        return Position.objects.all().organization
        ).select_related('department', 'reports_to').prefetch_related('employees')
    
    def perform_create(self, serializer):
        organization = self.request.user.organization_memberships.first().organization
        serializer.save(organization=organization)


class EmployeeViewSet(viewsets.ModelViewSet):
    """ViewSet for Employee model."""
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EmployeeFilter
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'employee_id', 'badge_number']
    ordering_fields = ['user__last_name', 'user__first_name', 'hire_date', 'salary']
    ordering = ['user__last_name', 'user__first_name']
    
    def get_queryset(self):
        return Employee.objects.all().organization
        ).select_related('user', 'position', 'department', 'manager').prefetch_related(
            'attendances', 'leave_requests', 'payrolls', 'performance_reviews',
            'training_enrollments', 'documents'
        )
    
    def perform_create(self, serializer):
        organization = self.request.user.organization_memberships.first().organization
        serializer.save(organization=organization)
    
    @action(detail=True, methods=['post'])
    def record_attendance(self, request, pk=None):
        """Record attendance for an employee."""
        employee = self.get_object()
        serializer = AttendanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(employee=employee)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def request_leave(self, request, pk=None):
        """Create a leave request for an employee."""
        employee = self.get_object()
        serializer = LeaveRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(employee=employee, requested_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def upload_document(self, request, pk=None):
        """Upload a document for an employee."""
        employee = self.get_object()
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(employee=employee)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def conduct_review(self, request, pk=None):
        """Conduct a performance review for an employee."""
        employee = self.get_object()
        serializer = PerformanceReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(employee=employee, reviewer=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def enroll_training(self, request, pk=None):
        """Enroll an employee in training."""
        employee = self.get_object()
        training_id = request.data.get('training_id')
        if not training_id:
            return Response({'error': 'training_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            training = Training.objects.get(id=training_id)
            enrollment, created = TrainingEnrollment.objects.get_or_create(
                training=training,
                employee=employee,
                defaults={'enrolled_by': request.user}
            )
            if created:
                serializer = TrainingEnrollmentSerializer(enrollment)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Employee already enrolled in this training'}, status=status.HTTP_400_BAD_REQUEST)
        except Training.DoesNotExist:
            return Response({'error': 'Training not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Change employee employment status."""
        employee = self.get_object()
        new_status = request.data.get('status')
        if not new_status:
            return Response({'error': 'status is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if new_status not in [choice[0] for choice in Employee.EMPLOYMENT_STATUS_CHOICES]:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        old_status = employee.employment_status
        employee.employment_status = new_status
        if new_status in ['terminated', 'resigned']:
            employee.termination_date = timezone.now().date()
        employee.save()
        
        return Response({'status': f'Employment status changed to {new_status}'})


class AttendanceViewSet(viewsets.ModelViewSet):
    """ViewSet for Attendance model."""
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AttendanceFilter
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'notes']
    ordering_fields = ['date', 'check_in_time', 'total_hours']
    ordering = ['-date']
    
    def get_queryset(self):
        return Attendance.objects.filter(
            employee__organization=self.request.user.organization_memberships.first().organization
        ).select_related('employee__user', 'approved_by')
    
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve attendance record."""
        attendance = self.get_object()
        attendance.status = 'present'
        attendance.approved_by = request.user
        attendance.save()
        return Response({'status': 'Attendance approved'})
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get attendance analytics."""
        filter_backend = AttendanceAnalyticsFilter()
        queryset = filter_backend.filter_queryset(request, self.get_queryset(), None)
        
        # Basic counts
        total_records = queryset.count()
        
        # Attendance by status
        attendance_by_status = queryset.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Attendance trends (last 12 months)
        attendance_trends = []
        for i in range(12):
            month_start = timezone.now().date().replace(day=1) - timedelta(days=30 * i)
            month_end = month_start + timedelta(days=30)
            month_attendance = queryset.filter(
                date__gte=month_start,
                date__lt=month_end
            ).count()
            
            attendance_trends.append({
                'month': month_start.strftime('%Y-%m'),
                'attendance': month_attendance
            })
        
        attendance_trends.reverse()
        
        # Late arrivals and early departures
        late_arrivals = queryset.filter(status='late').count()
        early_departures = queryset.filter(
            check_out_time__isnull=False,
            total_hours__lt=8
        ).count()
        
        # Overtime hours
        overtime_hours = queryset.aggregate(
            total_overtime=Sum('overtime_hours')
        )['total_overtime'] or 0
        
        # Attendance by department
        attendance_by_department = queryset.values(
            'employee__department__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Average attendance rate
        total_working_days = queryset.values('date').distinct().count()
        present_days = queryset.filter(status='present').count()
        average_attendance_rate = (present_days / total_working_days * 100) if total_working_days > 0 else 0
        
        analytics_data = {
            'total_attendance_records': total_records,
            'average_attendance_rate': float(average_attendance_rate),
            'attendance_by_status': list(attendance_by_status),
            'attendance_trends': attendance_trends,
            'late_arrivals': late_arrivals,
            'early_departures': early_departures,
            'overtime_hours': float(overtime_hours),
            'attendance_by_department': list(attendance_by_department)
        }
        
        serializer = AttendanceAnalyticsSerializer(analytics_data)
        return Response(serializer.data)


class LeaveTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for LeaveType model."""
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = LeaveTypeFilter
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'max_days_per_year']
    ordering = ['name']
    
    def get_queryset(self):
        return LeaveType.objects.all().organization
        )
    
    def perform_create(self, serializer):
        organization = self.request.user.organization_memberships.first().organization
        serializer.save(organization=organization)


class LeaveRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for LeaveRequest model."""
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = LeaveRequestFilter
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'reason']
    ordering_fields = ['start_date', 'end_date', 'created']
    ordering = ['-created']
    
    def get_queryset(self):
        return LeaveRequest.objects.filter(
            employee__organization=self.request.user.organization_memberships.first().organization
        ).select_related('employee__user', 'leave_type', 'requested_by', 'approved_by')
    
    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a leave request."""
        leave_request = self.get_object()
        if leave_request.status != 'pending':
            return Response({'error': 'Leave request is not pending'}, status=status.HTTP_400_BAD_REQUEST)
        
        leave_request.status = 'approved'
        leave_request.approved_by = request.user
        leave_request.approved_at = timezone.now()
        leave_request.save()
        
        return Response({'status': 'Leave request approved'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a leave request."""
        leave_request = self.get_object()
        if leave_request.status != 'pending':
            return Response({'error': 'Leave request is not pending'}, status=status.HTTP_400_BAD_REQUEST)
        
        rejection_reason = request.data.get('rejection_reason', '')
        leave_request.status = 'rejected'
        leave_request.approved_by = request.user
        leave_request.approved_at = timezone.now()
        leave_request.rejection_reason = rejection_reason
        leave_request.save()
        
        return Response({'status': 'Leave request rejected'})
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get leave analytics."""
        queryset = self.get_queryset()
        
        # Basic counts
        total_requests = queryset.count()
        approved_requests = queryset.filter(status='approved').count()
        pending_requests = queryset.filter(status='pending').count()
        rejected_requests = queryset.filter(status='rejected').count()
        
        # Leave by type
        leave_by_type = queryset.values('leave_type__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Leave by department
        leave_by_department = queryset.values(
            'employee__department__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Average leave duration
        avg_duration = queryset.aggregate(
            avg_duration=Avg('total_days')
        )['avg_duration'] or 0
        
        # Leave trends (last 12 months)
        leave_trends = []
        for i in range(12):
            month_start = timezone.now().date().replace(day=1) - timedelta(days=30 * i)
            month_end = month_start + timedelta(days=30)
            month_leaves = queryset.filter(
                start_date__gte=month_start,
                start_date__lt=month_end
            ).count()
            
            leave_trends.append({
                'month': month_start.strftime('%Y-%m'),
                'leaves': month_leaves
            })
        
        leave_trends.reverse()
        
        # Upcoming leaves
        upcoming_leaves = queryset.filter(
            start_date__gte=timezone.now().date(),
            status='approved'
        ).order_by('start_date')[:10].values(
            'employee__user__first_name', 'employee__user__last_name',
            'leave_type__name', 'start_date', 'end_date'
        )
        
        analytics_data = {
            'total_leave_requests': total_requests,
            'approved_leave_requests': approved_requests,
            'pending_leave_requests': pending_requests,
            'rejected_leave_requests': rejected_requests,
            'leave_by_type': list(leave_by_type),
            'leave_by_department': list(leave_by_department),
            'average_leave_duration': float(avg_duration),
            'leave_trends': leave_trends,
            'upcoming_leaves': list(upcoming_leaves)
        }
        
        serializer = LeaveAnalyticsSerializer(analytics_data)
        return Response(serializer.data)


class PayrollPeriodViewSet(viewsets.ModelViewSet):
    """ViewSet for PayrollPeriod model."""
    serializer_class = PayrollPeriodSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PayrollPeriodFilter
    search_fields = ['name']
    ordering_fields = ['start_date', 'end_date', 'pay_date']
    ordering = ['-start_date']
    
    def get_queryset(self):
        return PayrollPeriod.objects.all().organization
        ).select_related('processed_by').prefetch_related('payrolls')
    
    def perform_create(self, serializer):
        organization = self.request.user.organization_memberships.first().organization
        serializer.save(organization=organization)
    
    @action(detail=True, methods=['post'])
    def process_payroll(self, request, pk=None):
        """Process payroll for the period."""
        payroll_period = self.get_object()
        if payroll_period.status != 'draft':
            return Response({'error': 'Payroll period is not in draft status'}, status=status.HTTP_400_BAD_REQUEST)
        
        # This would typically involve complex payroll calculations
        # For now, we'll just update the status
        payroll_period.status = 'processing'
        payroll_period.processed_by = request.user
        payroll_period.processed_at = timezone.now()
        payroll_period.save()
        
        return Response({'status': 'Payroll processing started'})


class PayrollViewSet(viewsets.ModelViewSet):
    """ViewSet for Payroll model."""
    serializer_class = PayrollSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PayrollFilter
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'notes']
    ordering_fields = ['payroll_period__start_date', 'gross_pay', 'net_pay']
    ordering = ['-payroll_period__start_date']
    
    def get_queryset(self):
        return Payroll.objects.filter(
            employee__organization=self.request.user.organization_memberships.first().organization
        ).select_related('employee__user', 'payroll_period')
    
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get payroll analytics."""
        queryset = self.get_queryset()
        
        # Basic calculations
        total_payroll = queryset.aggregate(
            total=Sum('net_pay')
        )['total'] or 0
        
        average_salary = queryset.aggregate(
            avg_salary=Avg('basic_salary')
        )['avg_salary'] or 0
        
        # Payroll by department
        payroll_by_department = queryset.values(
            'employee__department__name'
        ).annotate(
            total_payroll=Sum('net_pay'),
            count=Count('id')
        ).order_by('-total_payroll')
        
        # Salary distribution
        salary_ranges = [
            {'range': '0-30000', 'count': queryset.filter(basic_salary__lte=30000).count()},
            {'range': '30001-50000', 'count': queryset.filter(basic_salary__gte=30001, basic_salary__lte=50000).count()},
            {'range': '50001-75000', 'count': queryset.filter(basic_salary__gte=50001, basic_salary__lte=75000).count()},
            {'range': '75001-100000', 'count': queryset.filter(basic_salary__gte=75001, basic_salary__lte=100000).count()},
            {'range': '100000+', 'count': queryset.filter(basic_salary__gte=100001).count()},
        ]
        
        # Overtime and benefits costs
        overtime_costs = queryset.aggregate(
            total_overtime=Sum('overtime_pay')
        )['total_overtime'] or 0
        
        benefits_costs = queryset.aggregate(
            total_benefits=Sum('health_insurance') + Sum('social_security')
        )['total_benefits'] or 0
        
        tax_deductions = queryset.aggregate(
            total_tax=Sum('tax_deduction')
        )['total_tax'] or 0
        
        # Payroll trends (last 12 months)
        payroll_trends = []
        for i in range(12):
            month_start = timezone.now().date().replace(day=1) - timedelta(days=30 * i)
            month_end = month_start + timedelta(days=30)
            month_payroll = queryset.filter(
                payroll_period__start_date__gte=month_start,
                payroll_period__start_date__lt=month_end
            ).aggregate(total=Sum('net_pay'))['total'] or 0
            
            payroll_trends.append({
                'month': month_start.strftime('%Y-%m'),
                'payroll': float(month_payroll)
            })
        
        payroll_trends.reverse()
        
        analytics_data = {
            'total_payroll_amount': float(total_payroll),
            'average_salary': float(average_salary),
            'payroll_by_department': list(payroll_by_department),
            'salary_distribution': salary_ranges,
            'overtime_costs': float(overtime_costs),
            'benefits_costs': float(benefits_costs),
            'tax_deductions': float(tax_deductions),
            'payroll_trends': payroll_trends
        }
        
        serializer = PayrollAnalyticsSerializer(analytics_data)
        return Response(serializer.data)


class PerformanceReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for PerformanceReview model."""
    serializer_class = PerformanceReviewSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PerformanceReviewFilter
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'strengths', 'areas_for_improvement']
    ordering_fields = ['review_date', 'overall_rating']
    ordering = ['-review_date']
    
    def get_queryset(self):
        return PerformanceReview.objects.filter(
            employee__organization=self.request.user.organization_memberships.first().organization
        ).select_related('employee__user', 'reviewer')
    
    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge a performance review."""
        review = self.get_object()
        review.employee_acknowledged = True
        review.acknowledged_at = timezone.now()
        review.save()
        return Response({'status': 'Review acknowledged'})
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get performance analytics."""
        queryset = self.get_queryset()
        
        # Basic counts
        total_reviews = queryset.count()
        
        # Average ratings
        avg_overall = queryset.aggregate(
            avg_rating=Avg('overall_rating')
        )['avg_rating'] or 0
        
        # Performance by rating
        performance_by_rating = []
        for rating in range(1, 6):
            count = queryset.filter(overall_rating=rating).count()
            performance_by_rating.append({'rating': rating, 'count': count})
        
        # Performance by department
        performance_by_department = queryset.values(
            'employee__department__name'
        ).annotate(
            avg_rating=Avg('overall_rating'),
            count=Count('id')
        ).order_by('-avg_rating')
        
        # Top performers
        top_performers = queryset.filter(
            overall_rating__gte=4
        ).order_by('-overall_rating')[:10].values(
            'employee__user__first_name', 'employee__user__last_name',
            'overall_rating', 'review_date'
        )
        
        # Improvement areas
        improvement_areas = queryset.exclude(
            areas_for_improvement__isnull=True
        ).exclude(
            areas_for_improvement=''
        ).values('areas_for_improvement')[:10]
        
        # Review completion rate
        completed_reviews = queryset.filter(status='completed').count()
        review_completion_rate = (completed_reviews / total_reviews * 100) if total_reviews > 0 else 0
        
        # Performance trends (last 12 months)
        performance_trends = []
        for i in range(12):
            month_start = timezone.now().date().replace(day=1) - timedelta(days=30 * i)
            month_end = month_start + timedelta(days=30)
            month_avg = queryset.filter(
                review_date__gte=month_start,
                review_date__lt=month_end
            ).aggregate(avg_rating=Avg('overall_rating'))['avg_rating'] or 0
            
            performance_trends.append({
                'month': month_start.strftime('%Y-%m'),
                'average_rating': float(month_avg)
            })
        
        performance_trends.reverse()
        
        analytics_data = {
            'total_reviews': total_reviews,
            'average_overall_rating': float(avg_overall),
            'performance_by_rating': performance_by_rating,
            'performance_by_department': list(performance_by_department),
            'top_performers': list(top_performers),
            'improvement_areas': list(improvement_areas),
            'review_completion_rate': float(review_completion_rate),
            'performance_trends': performance_trends
        }
        
        serializer = PerformanceAnalyticsSerializer(analytics_data)
        return Response(serializer.data)


class TrainingViewSet(viewsets.ModelViewSet):
    """ViewSet for Training model."""
    serializer_class = TrainingSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TrainingFilter
    search_fields = ['title', 'description', 'instructor']
    ordering_fields = ['start_date', 'end_date', 'title']
    ordering = ['-start_date']
    
    def get_queryset(self):
        return Training.objects.all().organization
        ).prefetch_related('enrollments')
    
    def perform_create(self, serializer):
        organization = self.request.user.organization_memberships.first().organization
        serializer.save(organization=organization)


class TrainingEnrollmentViewSet(viewsets.ModelViewSet):
    """ViewSet for TrainingEnrollment model."""
    serializer_class = TrainingEnrollmentSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TrainingEnrollmentFilter
    search_fields = ['training__title', 'employee__user__first_name', 'employee__user__last_name']
    ordering_fields = ['enrolled_at', 'completion_date', 'score']
    ordering = ['-enrolled_at']
    
    def get_queryset(self):
        return TrainingEnrollment.objects.filter(
            training__organization=self.request.user.organization_memberships.first().organization
        ).select_related('training', 'employee__user', 'enrolled_by')
    
    def perform_create(self, serializer):
        serializer.save(enrolled_by=self.request.user)


class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for Document model."""
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DocumentFilter
    search_fields = ['title', 'description', 'employee__user__first_name', 'employee__user__last_name']
    ordering_fields = ['created', 'issue_date', 'expiry_date']
    ordering = ['-created']
    
    def get_queryset(self):
        return Document.objects.filter(
            employee__organization=self.request.user.organization_memberships.first().organization
        ).select_related('employee__user', 'verified_by')
    
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a document."""
        document = self.get_object()
        document.is_verified = True
        document.verified_by = request.user
        document.verified_at = timezone.now()
        document.save()
        return Response({'status': 'Document verified'})


class PolicyViewSet(viewsets.ModelViewSet):
    """ViewSet for Policy model."""
    serializer_class = PolicySerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PolicyFilter
    search_fields = ['title', 'content', 'summary']
    ordering_fields = ['effective_date', 'title']
    ordering = ['-effective_date']
    
    def get_queryset(self):
        return Policy.objects.all().organization
        ).select_related('approved_by').prefetch_related('acknowledgments')
    
    def perform_create(self, serializer):
        organization = self.request.user.organization_memberships.first().organization
        serializer.save(organization=organization)
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge a policy."""
        policy = self.get_object()
        employee = request.user.employee_profile
        
        acknowledgment, created = PolicyAcknowledgment.objects.get_or_create(
            policy=policy,
            employee=employee
        )
        
        if created:
            return Response({'status': 'Policy acknowledged'})
        else:
            return Response({'status': 'Policy already acknowledged'})


class PolicyAcknowledgmentViewSet(viewsets.ModelViewSet):
    """ViewSet for PolicyAcknowledgment model."""
    serializer_class = PolicyAcknowledgmentSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = PolicyAcknowledgmentFilter
    ordering_fields = ['acknowledged_at']
    ordering = ['-acknowledged_at']
    
    def get_queryset(self):
        return PolicyAcknowledgment.objects.filter(
            policy__organization=self.request.user.organization_memberships.first().organization
        ).select_related('policy', 'employee__user')


class HRDashboardViewSet(viewsets.ViewSet):
    """ViewSet for HR dashboard data."""
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Get HR dashboard overview."""
        organization = request.user.organization_memberships.first().organization
        employees = Employee.objects
        
        # Basic counts
        total_employees = employees.count()
        active_employees = employees.filter(employment_status='active').count()
        new_employees_this_month = employees.filter(
            hire_date__month=timezone.now().month,
            hire_date__year=timezone.now().year
        ).count()
        employees_on_leave = employees.filter(employment_status='on_leave').count()
        employees_on_probation = employees.filter(
            probation_end_date__gte=timezone.now().date()
        ).count()
        
        # Department and position counts
        total_departments = Department.objects.count()
        total_positions = Position.objects.count()
        
        # Employees by department
        employees_by_department = employees.values('department__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Employees by status
        employees_by_status = employees.values('employment_status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Recent employees (last 10)
        recent_employees = employees.order_by('-hire_date')[:10].values(
            'user__first_name', 'user__last_name', 'employee_id',
            'department__name', 'position__title', 'hire_date'
        )
        
        # Upcoming birthdays (next 30 days)
        today = timezone.now().date()
        upcoming_birthdays = employees.filter(
            date_of_birth__isnull=False
        ).extra(
            where=["EXTRACT(month FROM date_of_birth) = %s AND EXTRACT(day FROM date_of_birth) BETWEEN %s AND %s"],
            params=[today.month, today.day, (today + timedelta(days=30)).day]
        ).values(
            'user__first_name', 'user__last_name', 'date_of_birth'
        )[:10]
        
        # Pending leave requests
        pending_leave_requests = LeaveRequest.objects.filter(
            employee__organization=organization,
            status='pending'
        ).order_by('-created')[:10].values(
            'employee__user__first_name', 'employee__user__last_name',
            'leave_type__name', 'start_date', 'end_date'
        )
        
        # Attendance summary
        today_attendance = Attendance.objects.filter(
            employee__organization=organization,
            date=today
        )
        present_today = today_attendance.filter(status='present').count()
        absent_today = today_attendance.filter(status='absent').count()
        late_today = today_attendance.filter(status='late').count()
        
        attendance_summary = {
            'present': present_today,
            'absent': absent_today,
            'late': late_today,
            'total': today_attendance.count()
        }
        
        dashboard_data = {
            'total_employees': total_employees,
            'active_employees': active_employees,
            'new_employees_this_month': new_employees_this_month,
            'employees_on_leave': employees_on_leave,
            'employees_on_probation': employees_on_probation,
            'total_departments': total_departments,
            'total_positions': total_positions,
            'employees_by_department': list(employees_by_department),
            'employees_by_status': list(employees_by_status),
            'recent_employees': list(recent_employees),
            'upcoming_birthdays': list(upcoming_birthdays),
            'pending_leave_requests': list(pending_leave_requests),
            'attendance_summary': attendance_summary
        }
        
        serializer = HRDashboardSerializer(dashboard_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get HR analytics."""
        organization = request.user.organization_memberships.first().organization
        employees = Employee.objects
        
        # Basic counts
        total_employees = employees.count()
        
        # Employee growth rate (this month vs last month)
        this_month = employees.filter(
            hire_date__month=timezone.now().month,
            hire_date__year=timezone.now().year
        ).count()
        last_month = employees.filter(
            hire_date__month=timezone.now().month - 1 if timezone.now().month > 1 else 12,
            hire_date__year=timezone.now().year if timezone.now().month > 1 else timezone.now().year - 1
        ).count()
        growth_rate = ((this_month - last_month) / last_month * 100) if last_month > 0 else 0
        
        # Average tenure
        avg_tenure = employees.aggregate(
            avg_tenure=Avg(F('hire_date'))
        )['avg_tenure']
        
        # Turnover rate (terminated/resigned in last 12 months)
        terminated_last_year = employees.filter(
            employment_status__in=['terminated', 'resigned'],
            termination_date__gte=timezone.now().date() - timedelta(days=365)
        ).count()
        turnover_rate = (terminated_last_year / total_employees * 100) if total_employees > 0 else 0
        
        # Gender distribution
        gender_distribution = employees.values('gender').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Age distribution
        age_ranges = [
            {'range': '18-25', 'count': 0},
            {'range': '26-35', 'count': 0},
            {'range': '36-45', 'count': 0},
            {'range': '46-55', 'count': 0},
            {'range': '55+', 'count': 0},
        ]
        # This would need more complex age calculation logic
        
        # Department distribution
        department_distribution = employees.values('department__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Position distribution
        position_distribution = employees.values('position__title').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Salary distribution
        salary_ranges = [
            {'range': '0-30000', 'count': employees.filter(salary__lte=30000).count()},
            {'range': '30001-50000', 'count': employees.filter(salary__gte=30001, salary__lte=50000).count()},
            {'range': '50001-75000', 'count': employees.filter(salary__gte=50001, salary__lte=75000).count()},
            {'range': '75001-100000', 'count': employees.filter(salary__gte=75001, salary__lte=100000).count()},
            {'range': '100000+', 'count': employees.filter(salary__gte=100001).count()},
        ]
        
        # Performance trends (placeholder)
        performance_trends = []
        
        analytics_data = {
            'total_employees': total_employees,
            'employee_growth_rate': float(growth_rate),
            'average_tenure': 0,  # Would need proper calculation
            'turnover_rate': float(turnover_rate),
            'gender_distribution': list(gender_distribution),
            'age_distribution': age_ranges,
            'department_distribution': list(department_distribution),
            'position_distribution': list(position_distribution),
            'salary_distribution': salary_ranges,
            'performance_trends': performance_trends
        }
        
        serializer = HRAnalyticsSerializer(analytics_data)
        return Response(serializer.data)
