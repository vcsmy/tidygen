"""
Comprehensive payroll management views.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q
from django.db import transaction
from decimal import Decimal
from datetime import date, timedelta

from .models import (
    PayrollConfiguration, PayrollComponent, EmployeePayrollProfile,
    PayrollRun, PayrollItem, PayrollAdjustment, TaxYear, EmployeeTaxInfo,
    PayrollReport, PayrollAnalytics, PayrollIntegration, PayrollWebhook,
    PayrollNotification
)
from .serializers import (
    PayrollConfigurationSerializer, PayrollComponentSerializer, EmployeePayrollProfileSerializer,
    PayrollRunSerializer, PayrollRunDetailSerializer, PayrollItemSerializer, PayrollAdjustmentSerializer,
    TaxYearSerializer, EmployeeTaxInfoSerializer, PayrollReportSerializer, PayrollAnalyticsSerializer,
    PayrollIntegrationSerializer, PayrollWebhookSerializer, PayrollNotificationSerializer,
    EnhancedPayrollSerializer, PayrollCalculationSerializer, PayrollProcessingSerializer,
    PayrollReportRequestSerializer, PayrollAnalyticsRequestSerializer
)
from apps.hr.models import Employee, PayrollPeriod, Payroll


# ==================== PAYROLL CONFIGURATION VIEWS ====================

class PayrollConfigurationViewSet(viewsets.ModelViewSet):
    """ViewSet for PayrollConfiguration management."""
    queryset = PayrollConfiguration.objects.all()
    serializer_class = PayrollConfigurationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['organization__name']
    ordering_fields = ['created_at', 'modified_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter configurations by user's organization."""
                return PayrollConfiguration.objects
    
    @action(detail=True, methods=['post'])
    def test_calculation(self, request, pk=None):
        """Test payroll calculation with sample data."""
        config = self.get_object()
        
        # Sample calculation test
        test_data = {
            'gross_pay': Decimal('5000.00'),
            'hours_worked': Decimal('40.00'),
            'overtime_hours': Decimal('5.00'),
            'federal_exemptions': 2,
            'state_exemptions': 2
        }
        
        # Calculate taxes
        federal_tax = test_data['gross_pay'] * config.federal_tax_rate
        state_tax = test_data['gross_pay'] * config.state_tax_rate
        local_tax = test_data['gross_pay'] * config.local_tax_rate
        social_security = min(test_data['gross_pay'], config.social_security_wage_base) * config.social_security_rate
        medicare = test_data['gross_pay'] * config.medicare_rate
        
        total_taxes = federal_tax + state_tax + local_tax + social_security + medicare
        net_pay = test_data['gross_pay'] - total_taxes
        
        return Response({
            'test_data': test_data,
            'calculations': {
                'federal_tax': float(federal_tax),
                'state_tax': float(state_tax),
                'local_tax': float(local_tax),
                'social_security': float(social_security),
                'medicare': float(medicare),
                'total_taxes': float(total_taxes),
                'net_pay': float(net_pay)
            }
        })


class PayrollComponentViewSet(viewsets.ModelViewSet):
    """ViewSet for PayrollComponent management."""
    queryset = PayrollComponent.objects.all()
    serializer_class = PayrollComponentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['component_type', 'calculation_type', 'is_active', 'is_mandatory']
    search_fields = ['name', 'description', 'category']
    ordering_fields = ['sort_order', 'name', 'created_at']
    ordering = ['sort_order', 'name']
    
    def get_queryset(self):
        """Filter components by user's organization."""
                return PayrollComponent.objects
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get components grouped by type."""
        components = self.get_queryset()
        grouped = {}
        for component in components:
            if component.component_type not in grouped:
                grouped[component.component_type] = []
            grouped[component.component_type].append(
                PayrollComponentSerializer(component).data
            )
        return Response(grouped)
    
    @action(detail=True, methods=['post'])
    def calculate_amount(self, request, pk=None):
        """Calculate component amount for given parameters."""
        component = self.get_object()
        gross_pay = Decimal(str(request.data.get('gross_pay', 0)))
        hours_worked = Decimal(str(request.data.get('hours_worked', 0)))
        
        if component.calculation_type == 'fixed':
            amount = component.amount
        elif component.calculation_type == 'percentage':
            amount = gross_pay * (component.percentage or 0)
        elif component.calculation_type == 'hourly':
            amount = hours_worked * component.amount
        elif component.calculation_type == 'daily':
            amount = (hours_worked / 8) * component.amount
        elif component.calculation_type == 'monthly':
            amount = component.amount
        elif component.calculation_type == 'annual':
            amount = component.amount / 12
        else:
            amount = 0
        
        return Response({
            'component': PayrollComponentSerializer(component).data,
            'parameters': {
                'gross_pay': float(gross_pay),
                'hours_worked': float(hours_worked)
            },
            'calculated_amount': float(amount)
        })


class EmployeePayrollProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for EmployeePayrollProfile management."""
    queryset = EmployeePayrollProfile.objects.all()
    serializer_class = EmployeePayrollProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['pay_type', 'is_active']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'employee__employee_id']
    ordering_fields = ['effective_date', 'created_at']
    ordering = ['-effective_date']
    
    def get_queryset(self):
        """Filter profiles by user's organization."""
                return EmployeePayrollProfile.objects.filter(employee__)
    
    @action(detail=True, methods=['post'])
    def calculate_pay(self, request, pk=None):
        """Calculate pay for employee based on profile."""
        profile = self.get_object()
        hours_worked = Decimal(str(request.data.get('hours_worked', 0)))
        overtime_hours = Decimal(str(request.data.get('overtime_hours', 0)))
        
        # Calculate base pay
        if profile.pay_type == 'salary':
            base_pay = profile.base_salary or 0
        elif profile.pay_type == 'hourly':
            base_pay = (profile.hourly_rate or 0) * hours_worked
        else:
            base_pay = 0
        
        # Calculate overtime
        overtime_pay = (profile.hourly_rate or 0) * overtime_hours * Decimal('1.5')
        
        # Calculate gross pay
        gross_pay = base_pay + overtime_pay
        
        # Calculate deductions
        health_insurance = profile.health_insurance_deduction or 0
        dental_insurance = profile.dental_insurance_deduction or 0
        vision_insurance = profile.vision_insurance_deduction or 0
        retirement = profile.retirement_contribution or 0
        
        total_deductions = health_insurance + dental_insurance + vision_insurance + retirement
        
        # Calculate net pay
        net_pay = gross_pay - total_deductions
        
        return Response({
            'profile': EmployeePayrollProfileSerializer(profile).data,
            'calculation': {
                'hours_worked': float(hours_worked),
                'overtime_hours': float(overtime_hours),
                'base_pay': float(base_pay),
                'overtime_pay': float(overtime_pay),
                'gross_pay': float(gross_pay),
                'total_deductions': float(total_deductions),
                'net_pay': float(net_pay)
            }
        })


# ==================== ENHANCED PAYROLL VIEWS ====================

class PayrollRunViewSet(viewsets.ModelViewSet):
    """ViewSet for PayrollRun management."""
    queryset = PayrollRun.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['run_type', 'status', 'payroll_period']
    search_fields = ['run_name', 'notes']
    ordering_fields = ['created_at', 'processed_at', 'total_net_pay']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter runs by user's organization."""
                return PayrollRun.objects
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'retrieve':
            return PayrollRunDetailSerializer
        return PayrollRunSerializer
    
    @action(detail=False, methods=['post'])
    def create_run(self, request):
        """Create a new payroll run."""
        serializer = PayrollRunSerializer(data=request.data)
        if serializer.is_valid():
            payroll_run = serializer.save()
            return Response(PayrollRunSerializer(payroll_run).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def process_payroll(self, request, pk=None):
        """Process payroll for the run."""
        payroll_run = self.get_object()
        
        if payroll_run.status != 'draft':
            return Response({'error': 'Payroll run must be in draft status to process.'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # Update status
                payroll_run.status = 'processing'
                payroll_run.processed_by = request.user
                payroll_run.processed_at = timezone.now()
                payroll_run.save()
                
                # Process each employee's payroll
                employees = Employee.objects.filter(
                    organization__in=request.user.organization_memberships.values_list('organization', flat=True),
                    employment_status='active'
                )
                
                total_employees = 0
                total_gross_pay = Decimal('0')
                total_deductions = Decimal('0')
                total_net_pay = Decimal('0')
                total_taxes = Decimal('0')
                
                for employee in employees:
                    # Create or update payroll record
                    payroll, created = Payroll.objects.get_or_create(
                        employee=employee,
                        payroll_period=payroll_run.payroll_period,
                        defaults={
                            'basic_salary': employee.salary or 0,
                            'hours_worked': 40,  # Default hours
                            'gross_pay': employee.salary or 0,
                            'total_deductions': 0,
                            'net_pay': employee.salary or 0,
                            'status': 'draft'
                        }
                    )
                    
                    # Calculate payroll amounts
                    payroll.gross_pay = payroll.basic_salary + payroll.allowances + payroll.bonuses
                    payroll.total_deductions = payroll.tax_deduction + payroll.social_security + payroll.health_insurance
                    payroll.net_pay = payroll.gross_pay - payroll.total_deductions
                    payroll.save()
                    
                    # Update totals
                    total_employees += 1
                    total_gross_pay += payroll.gross_pay
                    total_deductions += payroll.total_deductions
                    total_net_pay += payroll.net_pay
                    total_taxes += payroll.tax_deduction
                
                # Update payroll run totals
                payroll_run.total_employees = total_employees
                payroll_run.total_gross_pay = total_gross_pay
                payroll_run.total_deductions = total_deductions
                payroll_run.total_net_pay = total_net_pay
                payroll_run.total_taxes = total_taxes
                payroll_run.status = 'review'
                payroll_run.save()
                
                return Response({
                    'message': 'Payroll processed successfully.',
                    'totals': {
                        'total_employees': total_employees,
                        'total_gross_pay': float(total_gross_pay),
                        'total_deductions': float(total_deductions),
                        'total_net_pay': float(total_net_pay),
                        'total_taxes': float(total_taxes)
                    }
                })
                
        except Exception as e:
            payroll_run.status = 'draft'
            payroll_run.error_log.append(str(e))
            payroll_run.save()
            return Response({'error': f'Payroll processing failed: {str(e)}'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def approve_payroll(self, request, pk=None):
        """Approve payroll run."""
        payroll_run = self.get_object()
        
        if payroll_run.status != 'review':
            return Response({'error': 'Payroll run must be in review status to approve.'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        payroll_run.status = 'approved'
        payroll_run.approved_by = request.user
        payroll_run.approved_at = timezone.now()
        payroll_run.save()
        
        # Update individual payroll statuses
        Payroll.objects.filter(
            payroll_period=payroll_run.payroll_period
        ).update(status='approved')
        
        return Response({'message': 'Payroll approved successfully.'})
    
    @action(detail=True, methods=['post'])
    def pay_employees(self, request, pk=None):
        """Mark payroll as paid."""
        payroll_run = self.get_object()
        
        if payroll_run.status != 'approved':
            return Response({'error': 'Payroll run must be approved to pay.'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        payroll_run.status = 'paid'
        payroll_run.save()
        
        # Update individual payroll statuses
        Payroll.objects.filter(
            payroll_period=payroll_run.payroll_period
        ).update(status='paid')
        
        return Response({'message': 'Employees paid successfully.'})
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get payroll run summary."""
        runs = self.get_queryset()
        
        summary = {
            'total_runs': runs.count(),
            'draft_runs': runs.filter(status='draft').count(),
            'processing_runs': runs.filter(status='processing').count(),
            'review_runs': runs.filter(status='review').count(),
            'approved_runs': runs.filter(status='approved').count(),
            'paid_runs': runs.filter(status='paid').count(),
            'total_employees_paid': runs.aggregate(total=Sum('total_employees'))['total'] or 0,
            'total_gross_pay': float(runs.aggregate(total=Sum('total_gross_pay'))['total'] or 0),
            'total_net_pay': float(runs.aggregate(total=Sum('total_net_pay'))['total'] or 0),
        }
        
        return Response(summary)


class PayrollItemViewSet(viewsets.ModelViewSet):
    """ViewSet for PayrollItem management."""
    queryset = PayrollItem.objects.all()
    serializer_class = PayrollItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['item_type', 'component', 'is_taxable', 'is_pretax']
    search_fields = ['description', 'reference']
    ordering_fields = ['amount', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter items by user's organization."""
                return PayrollItem.objects.filter(
            payroll__employee__
        )


class PayrollAdjustmentViewSet(viewsets.ModelViewSet):
    """ViewSet for PayrollAdjustment management."""
    queryset = PayrollAdjustment.objects.all()
    serializer_class = PayrollAdjustmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['adjustment_type', 'is_positive', 'is_taxable', 'approved_by']
    search_fields = ['reason', 'reference_document']
    ordering_fields = ['amount', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter adjustments by user's organization."""
                return PayrollAdjustment.objects.filter(
            payroll__employee__
        )
    
    @action(detail=True, methods=['post'])
    def approve_adjustment(self, request, pk=None):
        """Approve payroll adjustment."""
        adjustment = self.get_object()
        
        if adjustment.approved_at:
            return Response({'error': 'Adjustment already approved.'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        adjustment.approved_by = request.user
        adjustment.approved_at = timezone.now()
        adjustment.save()
        
        # Update payroll totals
        payroll = adjustment.payroll
        if adjustment.is_positive:
            payroll.gross_pay += adjustment.amount
        else:
            payroll.total_deductions += adjustment.amount
        
        payroll.net_pay = payroll.gross_pay - payroll.total_deductions
        payroll.save()
        
        return Response({'message': 'Adjustment approved successfully.'})


# ==================== TAX AND COMPLIANCE VIEWS ====================

class TaxYearViewSet(viewsets.ModelViewSet):
    """ViewSet for TaxYear management."""
    queryset = TaxYear.objects.all()
    serializer_class = TaxYearSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['year', 'is_active']
    search_fields = ['organization__name']
    ordering_fields = ['year', 'created_at']
    ordering = ['-year']
    
    def get_queryset(self):
        """Filter tax years by user's organization."""
                return TaxYear.objects


class EmployeeTaxInfoViewSet(viewsets.ModelViewSet):
    """ViewSet for EmployeeTaxInfo management."""
    queryset = EmployeeTaxInfo.objects.all()
    serializer_class = EmployeeTaxInfoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['filing_status', 'tax_year']
    search_fields = ['employee__user__first_name', 'employee__user__last_name']
    ordering_fields = ['created_at', 'ytd_gross_wages']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter tax info by user's organization."""
                return EmployeeTaxInfo.objects.filter(employee__)


# ==================== PAYROLL REPORTS AND ANALYTICS VIEWS ====================

class PayrollReportViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for PayrollReport (read-only)."""
    queryset = PayrollReport.objects.all()
    serializer_class = PayrollReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['report_type', 'status']
    search_fields = ['report_name']
    ordering_fields = ['generated_at', 'start_date', 'end_date']
    ordering = ['-generated_at']
    
    def get_queryset(self):
        """Filter reports by user's organization."""
                return PayrollReport.objects
    
    @action(detail=False, methods=['post'])
    def generate_report(self, request):
        """Generate a new payroll report."""
        serializer = PayrollReportRequestSerializer(data=request.data)
        if serializer.is_valid():
            # Create report record
            report = PayrollReport.objects.create(
                organization=request.user.organization_memberships.first().organization,
                generated_by=request.user,
                **serializer.validated_data
            )
            
            # Generate report data (simplified)
            report_data = self._generate_report_data(report)
            report.report_data = report_data
            report.status = 'completed'
            report.save()
            
            return Response(PayrollReportSerializer(report).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _generate_report_data(self, report):
        """Generate report data based on type."""
        # Simplified report generation
        return {
            'summary': {
                'total_employees': 0,
                'total_gross_pay': 0,
                'total_net_pay': 0
            },
            'details': []
        }


class PayrollAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for PayrollAnalytics (read-only)."""
    queryset = PayrollAnalytics.objects.all()
    serializer_class = PayrollAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['period_type']
    search_fields = ['organization__name']
    ordering_fields = ['period_start', 'period_end', 'total_gross_pay']
    ordering = ['-period_start']
    
    def get_queryset(self):
        """Filter analytics by user's organization."""
                return PayrollAnalytics.objects
    
    @action(detail=False, methods=['post'])
    def generate_analytics(self, request):
        """Generate payroll analytics."""
        serializer = PayrollAnalyticsRequestSerializer(data=request.data)
        if serializer.is_valid():
            # Generate analytics data
            analytics_data = self._generate_analytics_data(serializer.validated_data)
            return Response(analytics_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _generate_analytics_data(self, data):
        """Generate analytics data."""
        # Simplified analytics generation
        return {
            'period': f"{data['start_date']} to {data['end_date']}",
            'metrics': {
                'total_employees': 0,
                'total_gross_pay': 0,
                'average_gross_pay': 0,
                'total_taxes': 0
            },
            'trends': {
                'gross_pay_trend': 0,
                'employee_count_trend': 0
            }
        }


# ==================== PAYROLL INTEGRATION VIEWS ====================

class PayrollIntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet for PayrollIntegration management."""
    queryset = PayrollIntegration.objects.all()
    serializer_class = PayrollIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['integration_type', 'is_active', 'sync_status']
    search_fields = ['integration_name', 'provider_name']
    ordering_fields = ['created_at', 'last_sync']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter integrations by user's organization."""
                return PayrollIntegration.objects
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test integration connection."""
        integration = self.get_object()
        
        # Simulate connection test
        integration.sync_status = 'success'
        integration.last_sync = timezone.now()
        integration.save()
        
        return Response({'message': 'Connection test successful.'})
    
    @action(detail=True, methods=['post'])
    def sync_data(self, request, pk=None):
        """Sync data with external system."""
        integration = self.get_object()
        
        # Simulate data sync
        integration.sync_status = 'success'
        integration.last_sync = timezone.now()
        integration.save()
        
        return Response({'message': 'Data sync completed successfully.'})


class PayrollWebhookViewSet(viewsets.ModelViewSet):
    """ViewSet for PayrollWebhook management."""
    queryset = PayrollWebhook.objects.all()
    serializer_class = PayrollWebhookSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['event_type', 'is_active']
    search_fields = ['webhook_url']
    ordering_fields = ['created_at', 'last_called']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter webhooks by user's organization."""
                return PayrollWebhook.objects


# ==================== PAYROLL NOTIFICATIONS VIEWS ====================

class PayrollNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for PayrollNotification (read-only)."""
    queryset = PayrollNotification.objects.all()
    serializer_class = PayrollNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['notification_type', 'status', 'delivery_method']
    search_fields = ['subject', 'message']
    ordering_fields = ['created_at', 'scheduled_at', 'sent_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter notifications by user's organization."""
                return PayrollNotification.objects


# ==================== PAYROLL CALCULATION VIEWS ====================

class PayrollCalculationView(APIView):
    """View for payroll calculations."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Calculate payroll for employee."""
        serializer = PayrollCalculationSerializer(data=request.data)
        if serializer.is_valid():
            # Get employee and payroll period
            employee = Employee.objects.get(id=serializer.validated_data['employee_id'])
            payroll_period = PayrollPeriod.objects.get(id=serializer.validated_data['payroll_period_id'])
            
            # Calculate payroll
            calculation = self._calculate_payroll(employee, payroll_period, serializer.validated_data)
            
            return Response(calculation, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _calculate_payroll(self, employee, payroll_period, data):
        """Calculate payroll for employee."""
        # Get employee payroll profile
        try:
            profile = employee.payroll_profile
        except EmployeePayrollProfile.DoesNotExist:
            profile = None
        
        # Calculate base pay
        if profile and profile.pay_type == 'salary':
            base_pay = profile.base_salary or 0
        elif profile and profile.pay_type == 'hourly':
            base_pay = (profile.hourly_rate or 0) * data['hours_worked']
        else:
            base_pay = employee.salary or 0
        
        # Calculate overtime
        overtime_pay = (profile.hourly_rate or 0) * data['overtime_hours'] * Decimal('1.5')
        
        # Calculate gross pay
        gross_pay = base_pay + overtime_pay + data['allowances'] + data['bonuses'] + data['commissions']
        
        # Calculate taxes (simplified)
        federal_tax = gross_pay * Decimal('0.22')  # 22%
        state_tax = gross_pay * Decimal('0.05')    # 5%
        social_security = min(gross_pay, Decimal('160200')) * Decimal('0.062')  # 6.2%
        medicare = gross_pay * Decimal('0.0145')   # 1.45%
        
        total_taxes = federal_tax + state_tax + social_security + medicare
        
        # Calculate deductions
        total_deductions = total_taxes
        if profile:
            total_deductions += profile.health_insurance_deduction or 0
            total_deductions += profile.dental_insurance_deduction or 0
            total_deductions += profile.vision_insurance_deduction or 0
            total_deductions += profile.retirement_contribution or 0
        
        # Calculate net pay
        net_pay = gross_pay - total_deductions
        
        return {
            'employee': {
                'id': employee.id,
                'name': employee.full_name,
                'employee_id': employee.employee_id
            },
            'payroll_period': {
                'id': payroll_period.id,
                'name': payroll_period.name,
                'start_date': payroll_period.start_date,
                'end_date': payroll_period.end_date
            },
            'calculation': {
                'base_pay': float(base_pay),
                'overtime_pay': float(overtime_pay),
                'allowances': float(data['allowances']),
                'bonuses': float(data['bonuses']),
                'commissions': float(data['commissions']),
                'gross_pay': float(gross_pay),
                'federal_tax': float(federal_tax),
                'state_tax': float(state_tax),
                'social_security': float(social_security),
                'medicare': float(medicare),
                'total_taxes': float(total_taxes),
                'total_deductions': float(total_deductions),
                'net_pay': float(net_pay)
            }
        }


class PayrollProcessingView(APIView):
    """View for payroll processing operations."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Process payroll operations."""
        serializer = PayrollProcessingSerializer(data=request.data)
        if serializer.is_valid():
            payroll_run = PayrollRun.objects.get(id=serializer.validated_data['payroll_run_id'])
            process_type = serializer.validated_data['process_type']
            
            if process_type == 'calculate':
                result = self._calculate_payroll_run(payroll_run)
            elif process_type == 'approve':
                result = self._approve_payroll_run(payroll_run, request.user)
            elif process_type == 'process':
                result = self._process_payroll_run(payroll_run, request.user)
            elif process_type == 'pay':
                result = self._pay_employees(payroll_run, request.user)
            else:
                return Response({'error': 'Invalid process type.'}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _calculate_payroll_run(self, payroll_run):
        """Calculate payroll for run."""
        # Simplified calculation
        return {'message': 'Payroll calculated successfully.'}
    
    def _approve_payroll_run(self, payroll_run, user):
        """Approve payroll run."""
        payroll_run.status = 'approved'
        payroll_run.approved_by = user
        payroll_run.approved_at = timezone.now()
        payroll_run.save()
        return {'message': 'Payroll approved successfully.'}
    
    def _process_payroll_run(self, payroll_run, user):
        """Process payroll run."""
        payroll_run.status = 'processing'
        payroll_run.processed_by = user
        payroll_run.processed_at = timezone.now()
        payroll_run.save()
        return {'message': 'Payroll processed successfully.'}
    
    def _pay_employees(self, payroll_run, user):
        """Pay employees."""
        payroll_run.status = 'paid'
        payroll_run.save()
        return {'message': 'Employees paid successfully.'}


# ==================== PAYROLL DASHBOARD VIEW ====================

class PayrollDashboardView(APIView):
    """Payroll dashboard overview."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get payroll dashboard data."""
                
        # Get current period
        current_date = date.today()
        current_period = PayrollPeriod.objects.filter(
            ,
            start_date__lte=current_date,
            end_date__gte=current_date
        ).first()
        
        # Get recent payroll runs
        recent_runs = PayrollRun.objects.filter(
            
        ).order_by('-created_at')[:5]
        
        # Get payroll statistics
        stats = {
            'total_employees': Employee.objects.count(),
            'current_period': PayrollPeriodSerializer(current_period).data if current_period else None,
            'recent_runs': PayrollRunSerializer(recent_runs, many=True).data,
            'total_payroll_runs': PayrollRun.objects.count(),
            'pending_approvals': PayrollRun.objects.count(),
            'total_paid_this_month': float(
                PayrollRun.objects.filter(
                    ,
                    status='paid',
                    created__month=current_date.month,
                    created__year=current_date.year
                ).aggregate(total=Sum('total_net_pay'))['total'] or 0
            ),
        }
        
        return Response(stats)
