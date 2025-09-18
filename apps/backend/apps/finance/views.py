"""
Finance management views for TidyGen ERP platform.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from apps.core.permissions import IsOrganizationMember
from apps.finance.models import (
    Account, Customer, Vendor, Invoice, InvoiceItem, Payment, Expense,
    Budget, BudgetItem, FinancialReport, TaxRate, RecurringInvoice, RecurringInvoiceItem
)
from apps.finance.serializers import (
    AccountSerializer, CustomerSerializer, VendorSerializer, InvoiceSerializer,
    InvoiceItemSerializer, PaymentSerializer, ExpenseSerializer, BudgetSerializer,
    BudgetItemSerializer, FinancialReportSerializer, TaxRateSerializer,
    RecurringInvoiceSerializer, RecurringInvoiceItemSerializer,
    FinanceDashboardSerializer, InvoiceAnalyticsSerializer, ExpenseAnalyticsSerializer
)
from apps.finance.filters import (
    AccountFilter, CustomerFilter, VendorFilter, InvoiceFilter, PaymentFilter,
    ExpenseFilter, BudgetFilter, FinancialReportFilter, TaxRateFilter,
    RecurringInvoiceFilter, InvoiceAnalyticsFilter, ExpenseAnalyticsFilter
)


class AccountViewSet(viewsets.ModelViewSet):
    """ViewSet for Account model."""
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AccountFilter
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'account_type', 'balance']
    ordering = ['code']
    
    def get_queryset(self):
        return Account.objects.filter(organization=self.request.user.organization_memberships.first().organization)
    
    def perform_create(self, serializer):
        organization = self.request.user.organization_memberships.first().organization
        serializer.save(organization=organization)


class CustomerViewSet(viewsets.ModelViewSet):
    """ViewSet for Customer model."""
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CustomerFilter
    search_fields = ['name', 'email', 'phone', 'city', 'state', 'country']
    ordering_fields = ['name', 'email', 'created', 'credit_limit']
    ordering = ['name']
    
    def get_queryset(self):
        return Customer.objects.filter(organization=self.request.user.organization_memberships.first().organization)
    
    def perform_create(self, serializer):
        organization = self.request.user.organization_memberships.first().organization
        serializer.save(organization=organization)
    
    @action(detail=True, methods=['get'])
    def invoices(self, request, pk=None):
        """Get all invoices for a customer."""
        customer = self.get_object()
        invoices = customer.invoices.all()
        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """Get all payments for a customer."""
        customer = self.get_object()
        payments = customer.payments.all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class VendorViewSet(viewsets.ModelViewSet):
    """ViewSet for Vendor model."""
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = VendorFilter
    search_fields = ['name', 'contact_person', 'email', 'phone', 'city', 'state', 'country']
    ordering_fields = ['name', 'email', 'created']
    ordering = ['name']
    
    def get_queryset(self):
        return Vendor.objects.filter(organization=self.request.user.organization_memberships.first().organization)
    
    def perform_create(self, serializer):
        organization = self.request.user.organization_memberships.first().organization
        serializer.save(organization=organization)
    
    @action(detail=True, methods=['get'])
    def expenses(self, request, pk=None):
        """Get all expenses for a vendor."""
        vendor = self.get_object()
        expenses = vendor.expenses.all()
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data)


class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for Invoice model."""
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = InvoiceFilter
    search_fields = ['invoice_number', 'customer__name', 'notes']
    ordering_fields = ['invoice_number', 'issue_date', 'due_date', 'total_amount', 'status']
    ordering = ['-issue_date']
    
    def get_queryset(self):
        return Invoice.objects.filter(organization=self.request.user.organization_memberships.first().organization)
    
    def perform_create(self, serializer):
        organization = self.request.user.organization_memberships.first().organization
        serializer.save(organization=organization, created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send_invoice(self, request, pk=None):
        """Mark invoice as sent."""
        invoice = self.get_object()
        if invoice.status == 'draft':
            invoice.status = 'sent'
            invoice.sent_date = timezone.now().date()
            invoice.save()
            return Response({'status': 'Invoice sent successfully'})
        return Response({'error': 'Invoice cannot be sent'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark invoice as paid."""
        invoice = self.get_object()
        if invoice.status in ['sent', 'viewed']:
            invoice.status = 'paid'
            invoice.paid_date = timezone.now().date()
            invoice.paid_amount = invoice.total_amount
            invoice.save()
            return Response({'status': 'Invoice marked as paid'})
        return Response({'error': 'Invoice cannot be marked as paid'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancel_invoice(self, request, pk=None):
        """Cancel invoice."""
        invoice = self.get_object()
        if invoice.status in ['draft', 'sent', 'viewed']:
            invoice.status = 'cancelled'
            invoice.save()
            return Response({'status': 'Invoice cancelled'})
        return Response({'error': 'Invoice cannot be cancelled'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue invoices."""
        today = timezone.now().date()
        overdue_invoices = self.get_queryset().filter(
            due_date__lt=today,
            status__in=['sent', 'viewed']
        )
        serializer = self.get_serializer(overdue_invoices, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get invoice analytics."""
        filter_backend = InvoiceAnalyticsFilter()
        queryset = filter_backend.filter_queryset(request, self.get_queryset(), None)
        
        total_invoices = queryset.count()
        paid_invoices = queryset.filter(status='paid').count()
        overdue_invoices = queryset.filter(
            due_date__lt=timezone.now().date(),
            status__in=['sent', 'viewed']
        ).count()
        draft_invoices = queryset.filter(status='draft').count()
        
        total_revenue = queryset.filter(status='paid').aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        average_invoice_amount = queryset.aggregate(
            avg=Avg('total_amount')
        )['avg'] or Decimal('0')
        
        # Payment trends (last 12 months)
        payment_trends = []
        for i in range(12):
            month_start = timezone.now().date().replace(day=1) - timedelta(days=30 * i)
            month_end = month_start + timedelta(days=30)
            month_revenue = queryset.filter(
                status='paid',
                paid_date__gte=month_start,
                paid_date__lt=month_end
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
            
            payment_trends.append({
                'month': month_start.strftime('%Y-%m'),
                'revenue': float(month_revenue)
            })
        
        payment_trends.reverse()
        
        analytics_data = {
            'total_invoices': total_invoices,
            'paid_invoices': paid_invoices,
            'overdue_invoices': overdue_invoices,
            'draft_invoices': draft_invoices,
            'total_revenue': float(total_revenue),
            'average_invoice_amount': float(average_invoice_amount),
            'payment_trends': payment_trends
        }
        
        serializer = InvoiceAnalyticsSerializer(analytics_data)
        return Response(serializer.data)


class InvoiceItemViewSet(viewsets.ModelViewSet):
    """ViewSet for InvoiceItem model."""
    queryset = InvoiceItem.objects.all()
    serializer_class = InvoiceItemSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['description', 'quantity', 'unit_price', 'total_price']
    ordering = ['id']
    
    def get_queryset(self):
        invoice_id = self.request.query_params.get('invoice_id')
        if invoice_id:
            return InvoiceItem.objects.filter(invoice_id=invoice_id)
        return InvoiceItem.objects.none()


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for Payment model."""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PaymentFilter
    search_fields = ['payment_number', 'reference_number', 'notes']
    ordering_fields = ['payment_number', 'payment_date', 'amount']
    ordering = ['-payment_date']
    
    def get_queryset(self):
        return Payment.objects.filter(organization=self.request.user.organization_memberships.first().organization)
    
    def perform_create(self, serializer):
        organization = self.request.user.organization_memberships.first().organization
        serializer.save(organization=organization, received_by=self.request.user)


class ExpenseViewSet(viewsets.ModelViewSet):
    """ViewSet for Expense model."""
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ExpenseFilter
    search_fields = ['description', 'receipt_number']
    ordering_fields = ['description', 'expense_date', 'amount', 'status']
    ordering = ['-expense_date']
    
    def get_queryset(self):
        return Expense.objects.filter(organization=self.request.user.organization_memberships.first().organization)
    
    def perform_create(self, serializer):
        organization = self.request.user.organization_memberships.first().organization
        serializer.save(organization=organization, submitted_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve expense."""
        expense = self.get_object()
        if expense.status == 'pending':
            expense.status = 'approved'
            expense.approved_by = request.user
            expense.approved_at = timezone.now()
            expense.save()
            return Response({'status': 'Expense approved'})
        return Response({'error': 'Expense cannot be approved'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject expense."""
        expense = self.get_object()
        rejection_reason = request.data.get('rejection_reason', '')
        if expense.status == 'pending':
            expense.status = 'rejected'
            expense.approved_by = request.user
            expense.approved_at = timezone.now()
            expense.rejection_reason = rejection_reason
            expense.save()
            return Response({'status': 'Expense rejected'})
        return Response({'error': 'Expense cannot be rejected'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark expense as paid."""
        expense = self.get_object()
        if expense.status == 'approved':
            expense.status = 'paid'
            expense.save()
            return Response({'status': 'Expense marked as paid'})
        return Response({'error': 'Expense cannot be marked as paid'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get expense analytics."""
        filter_backend = ExpenseAnalyticsFilter()
        queryset = filter_backend.filter_queryset(request, self.get_queryset(), None)
        
        total_expenses = queryset.count()
        approved_expenses = queryset.filter(status='approved').count()
        pending_expenses = queryset.filter(status='pending').count()
        
        total_amount = queryset.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        average_expense_amount = queryset.aggregate(
            avg=Avg('total_amount')
        )['avg'] or Decimal('0')
        
        # Category breakdown
        category_breakdown = []
        for category, _ in Expense.CATEGORIES:
            category_total = queryset.filter(category=category).aggregate(
                total=Sum('total_amount')
            )['total'] or Decimal('0')
            category_count = queryset.filter(category=category).count()
            
            if category_total > 0:
                category_breakdown.append({
                    'category': category,
                    'amount': float(category_total),
                    'count': category_count
                })
        
        # Monthly trends (last 12 months)
        monthly_trends = []
        for i in range(12):
            month_start = timezone.now().date().replace(day=1) - timedelta(days=30 * i)
            month_end = month_start + timedelta(days=30)
            month_expenses = queryset.filter(
                expense_date__gte=month_start,
                expense_date__lt=month_end
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
            
            monthly_trends.append({
                'month': month_start.strftime('%Y-%m'),
                'amount': float(month_expenses)
            })
        
        monthly_trends.reverse()
        
        analytics_data = {
            'total_expenses': total_expenses,
            'approved_expenses': approved_expenses,
            'pending_expenses': pending_expenses,
            'total_amount': float(total_amount),
            'average_expense_amount': float(average_expense_amount),
            'category_breakdown': category_breakdown,
            'monthly_trends': monthly_trends
        }
        
        serializer = ExpenseAnalyticsSerializer(analytics_data)
        return Response(serializer.data)


class BudgetViewSet(viewsets.ModelViewSet):
    """ViewSet for Budget model."""
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BudgetFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'start_date', 'end_date', 'total_budget']
    ordering = ['-start_date']
    
    def get_queryset(self):
        return Budget.objects.filter(organization=self.request.user.organization_memberships.first().organization)
    
    def perform_create(self, serializer):
        organization = self.request.user.organization_memberships.first().organization
        serializer.save(organization=organization)


class BudgetItemViewSet(viewsets.ModelViewSet):
    """ViewSet for BudgetItem model."""
    queryset = BudgetItem.objects.all()
    serializer_class = BudgetItemSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['category', 'budgeted_amount', 'spent_amount']
    ordering = ['category']
    
    def get_queryset(self):
        budget_id = self.request.query_params.get('budget_id')
        if budget_id:
            return BudgetItem.objects.filter(budget_id=budget_id)
        return BudgetItem.objects.none()


class TaxRateViewSet(viewsets.ModelViewSet):
    """ViewSet for TaxRate model."""
    queryset = TaxRate.objects.all()
    serializer_class = TaxRateSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TaxRateFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'rate']
    ordering = ['name']
    
    def get_queryset(self):
        return TaxRate.objects.filter(organization=self.request.user.organization_memberships.first().organization)
    
    def perform_create(self, serializer):
        organization = self.request.user.organization_memberships.first().organization
        serializer.save(organization=organization)


class RecurringInvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for RecurringInvoice model."""
    queryset = RecurringInvoice.objects.all()
    serializer_class = RecurringInvoiceSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RecurringInvoiceFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'start_date', 'total_amount']
    ordering = ['name']
    
    def get_queryset(self):
        return RecurringInvoice.objects.filter(organization=self.request.user.organization_memberships.first().organization)
    
    def perform_create(self, serializer):
        organization = self.request.user.organization_memberships.first().organization
        serializer.save(organization=organization)
    
    @action(detail=True, methods=['post'])
    def generate_invoice(self, request, pk=None):
        """Generate invoice from recurring template."""
        recurring_invoice = self.get_object()
        
        # Create new invoice
        invoice = Invoice.objects.create(
            organization=recurring_invoice.organization,
            customer=recurring_invoice.customer,
            invoice_number=InvoiceSerializer()._generate_invoice_number(),
            issue_date=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=30),
            subtotal=recurring_invoice.subtotal,
            tax_rate=recurring_invoice.tax_rate,
            total_amount=recurring_invoice.total_amount,
            created_by=request.user
        )
        
        # Create invoice items
        for item in recurring_invoice.items.all():
            InvoiceItem.objects.create(
                invoice=invoice,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price
            )
        
        # Update recurring invoice
        recurring_invoice.last_generated = timezone.now().date()
        recurring_invoice.save()
        
        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data)


class RecurringInvoiceItemViewSet(viewsets.ModelViewSet):
    """ViewSet for RecurringInvoiceItem model."""
    queryset = RecurringInvoiceItem.objects.all()
    serializer_class = RecurringInvoiceItemSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['description', 'quantity', 'unit_price', 'total_price']
    ordering = ['id']
    
    def get_queryset(self):
        recurring_invoice_id = self.request.query_params.get('recurring_invoice_id')
        if recurring_invoice_id:
            return RecurringInvoiceItem.objects.filter(recurring_invoice_id=recurring_invoice_id)
        return RecurringInvoiceItem.objects.none()


class FinancialReportViewSet(viewsets.ModelViewSet):
    """ViewSet for FinancialReport model."""
    queryset = FinancialReport.objects.all()
    serializer_class = FinancialReportSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = FinancialReportFilter
    search_fields = ['name']
    ordering_fields = ['name', 'start_date', 'end_date', 'generated_at']
    ordering = ['-generated_at']
    
    def get_queryset(self):
        return FinancialReport.objects.filter(organization=self.request.user.organization_memberships.first().organization)
    
    def perform_create(self, serializer):
        organization = self.request.user.organization_memberships.first().organization
        serializer.save(organization=organization, generated_by=self.request.user)


class FinanceDashboardViewSet(viewsets.ViewSet):
    """ViewSet for finance dashboard data."""
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Get finance dashboard overview."""
        organization = request.user.organization_memberships.first().organization
        
        # Calculate totals
        total_revenue = Payment.objects.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        total_expenses = Expense.objects.filter(
            organization=organization,
            status__in=['approved', 'paid']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        net_profit = total_revenue - total_expenses
        
        outstanding_invoices = Invoice.objects.filter(
            organization=organization,
            status__in=['sent', 'viewed']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        overdue_invoices = Invoice.objects.filter(
            organization=organization,
            due_date__lt=timezone.now().date(),
            status__in=['sent', 'viewed']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        pending_expenses = Expense.objects.filter(
            organization=organization,
            status='pending'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        # Monthly revenue (last 12 months)
        monthly_revenue = []
        for i in range(12):
            month_start = timezone.now().date().replace(day=1) - timedelta(days=30 * i)
            month_end = month_start + timedelta(days=30)
            month_revenue_amount = Payment.objects.filter(
                organization=organization,
                payment_date__gte=month_start,
                payment_date__lt=month_end
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            monthly_revenue.append({
                'month': month_start.strftime('%Y-%m'),
                'revenue': float(month_revenue_amount)
            })
        
        monthly_revenue.reverse()
        
        # Monthly expenses (last 12 months)
        monthly_expenses = []
        for i in range(12):
            month_start = timezone.now().date().replace(day=1) - timedelta(days=30 * i)
            month_end = month_start + timedelta(days=30)
            month_expenses_amount = Expense.objects.filter(
                organization=organization,
                expense_date__gte=month_start,
                expense_date__lt=month_end,
                status__in=['approved', 'paid']
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
            
            monthly_expenses.append({
                'month': month_start.strftime('%Y-%m'),
                'expenses': float(month_expenses_amount)
            })
        
        monthly_expenses.reverse()
        
        # Top customers
        top_customers = Customer.objects.annotate(
            total_revenue=Sum('payments__amount')
        ).order_by('-total_revenue')[:5]
        
        top_customers_data = []
        for customer in top_customers:
            top_customers_data.append({
                'name': customer.name,
                'revenue': float(customer.total_revenue or Decimal('0'))
            })
        
        # Expense categories
        expense_categories = []
        for category, _ in Expense.CATEGORIES:
            category_total = Expense.objects.filter(
                organization=organization,
                category=category,
                status__in=['approved', 'paid']
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
            
            if category_total > 0:
                expense_categories.append({
                    'category': category,
                    'amount': float(category_total)
                })
        
        dashboard_data = {
            'total_revenue': float(total_revenue),
            'total_expenses': float(total_expenses),
            'net_profit': float(net_profit),
            'outstanding_invoices': float(outstanding_invoices),
            'overdue_invoices': float(overdue_invoices),
            'pending_expenses': float(pending_expenses),
            'monthly_revenue': monthly_revenue,
            'monthly_expenses': monthly_expenses,
            'top_customers': top_customers_data,
            'expense_categories': expense_categories
        }
        
        serializer = FinanceDashboardSerializer(dashboard_data)
        return Response(serializer.data)
