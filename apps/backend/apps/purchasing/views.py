"""
Purchasing Management Views

This module contains all the views for the purchasing management system,
providing API endpoints for purchase orders, suppliers, procurement, and analytics.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from drf_spectacular.utils import extend_schema

from apps.purchasing.models import (
    PurchaseOrder, PurchaseOrderItem, PurchaseReceipt, PurchaseReceiptItem,
    ProcurementRequest, ProcurementRequestItem, SupplierPerformance, PurchaseAnalytics
)
from apps.purchasing.serializers import (
    PurchaseOrderSerializer, PurchaseOrderCreateSerializer, PurchaseOrderSummarySerializer,
    PurchaseOrderItemSerializer, PurchaseReceiptSerializer, PurchaseReceiptCreateSerializer,
    PurchaseReceiptItemSerializer, ProcurementRequestSerializer, ProcurementRequestCreateSerializer,
    ProcurementRequestSummarySerializer, ProcurementRequestItemSerializer,
    SupplierPerformanceSerializer, SupplierPerformanceSummarySerializer,
    PurchaseAnalyticsSerializer, PurchaseOrderStatusUpdateSerializer,
    ProcurementRequestStatusUpdateSerializer
)
from apps.purchasing.filters import (
    PurchaseOrderFilter, PurchaseReceiptFilter, ProcurementRequestFilter,
    SupplierPerformanceFilter, PurchaseAnalyticsFilter
)
from apps.core.permissions import IsOrganizationMember


@extend_schema(tags=['Purchasing'])
class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing purchase orders.
    """
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend]
    filterset_class = PurchaseOrderFilter
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PurchaseOrderCreateSerializer
        elif self.action == 'list':
            return PurchaseOrderSummarySerializer
        elif self.action in ['update_status', 'partial_update']:
            return PurchaseOrderStatusUpdateSerializer
        return PurchaseOrderSerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'organization'):
            return self.queryset
        return self.queryset.none()
    
    def perform_create(self, serializer):
        serializer.save(
            requested_by=self.request.user,
            organization=self.request.user.organization
        )
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update purchase order status."""
        purchase_order = self.get_object()
        serializer = PurchaseOrderStatusUpdateSerializer(
            purchase_order, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a purchase order."""
        purchase_order = self.get_object()
        if purchase_order.status != 'pending_approval':
            return Response(
                {'error': 'Only pending approval orders can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        purchase_order.status = 'approved'
        purchase_order.approved_by = request.user
        purchase_order.approval_date = timezone.now()
        purchase_order.save()
        
        serializer = self.get_serializer(purchase_order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def send_to_supplier(self, request, pk=None):
        """Send purchase order to supplier."""
        purchase_order = self.get_object()
        if purchase_order.status != 'approved':
            return Response(
                {'error': 'Only approved orders can be sent to supplier'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        purchase_order.status = 'sent'
        purchase_order.save()
        
        serializer = self.get_serializer(purchase_order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a purchase order."""
        purchase_order = self.get_object()
        if purchase_order.status in ['fully_received', 'closed', 'cancelled']:
            return Response(
                {'error': 'Cannot cancel order in current status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        purchase_order.status = 'cancelled'
        purchase_order.save()
        
        serializer = self.get_serializer(purchase_order)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get purchase order analytics."""
        queryset = self.get_queryset()
        
        # Date range filtering
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(order_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(order_date__lte=end_date)
        
        analytics = {
            'total_orders': queryset.count(),
            'total_value': queryset.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00'),
            'average_order_value': queryset.aggregate(avg=Avg('total_amount'))['avg'] or Decimal('0.00'),
            'status_breakdown': dict(queryset.values('status').annotate(count=Count('id')).values_list('status', 'count')),
            'priority_breakdown': dict(queryset.values('priority').annotate(count=Count('id')).values_list('priority', 'count')),
            'monthly_trends': self._get_monthly_trends(queryset),
            'top_suppliers': self._get_top_suppliers(queryset),
        }
        
        return Response(analytics)
    
    def _get_monthly_trends(self, queryset):
        """Get monthly purchase trends."""
        from django.db.models.functions import TruncMonth
        
        trends = queryset.annotate(
            month=TruncMonth('order_date')
        ).values('month').annotate(
            count=Count('id'),
            total=Sum('total_amount')
        ).order_by('month')
        
        return list(trends)
    
    def _get_top_suppliers(self, queryset):
        """Get top suppliers by order value."""
        return list(queryset.values('supplier__name').annotate(
            order_count=Count('id'),
            total_value=Sum('total_amount')
        ).order_by('-total_value')[:10])


@extend_schema(tags=['Purchasing'])
class PurchaseOrderItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing purchase order items.
    """
    queryset = PurchaseOrderItem.objects.all()
    serializer_class = PurchaseOrderItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'organization'):
            return self.queryset.filter(purchase_order__organization=user.organization)
        return self.queryset.none()


@extend_schema(tags=['Purchasing'])
class PurchaseReceiptViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing purchase receipts.
    """
    queryset = PurchaseReceipt.objects.all()
    serializer_class = PurchaseReceiptSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend]
    filterset_class = PurchaseReceiptFilter
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PurchaseReceiptCreateSerializer
        return PurchaseReceiptSerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'organization'):
            return self.queryset.filter(purchase_order__organization=user.organization)
        return self.queryset.none()
    
    def perform_create(self, serializer):
        serializer.save(received_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_complete(self, request, pk=None):
        """Mark receipt as complete."""
        receipt = self.get_object()
        receipt.status = 'complete'
        receipt.save()
        
        # Update purchase order status
        receipt.update_purchase_order_status()
        
        serializer = self.get_serializer(receipt)
        return Response(serializer.data)


@extend_schema(tags=['Purchasing'])
class PurchaseReceiptItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing purchase receipt items.
    """
    queryset = PurchaseReceiptItem.objects.all()
    serializer_class = PurchaseReceiptItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'organization'):
            return self.queryset.filter(receipt__purchase_order__organization=user.organization)
        return self.queryset.none()


@extend_schema(tags=['Purchasing'])
class ProcurementRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing procurement requests.
    """
    queryset = ProcurementRequest.objects.all()
    serializer_class = ProcurementRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProcurementRequestFilter
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProcurementRequestCreateSerializer
        elif self.action == 'list':
            return ProcurementRequestSummarySerializer
        elif self.action in ['update_status', 'partial_update']:
            return ProcurementRequestStatusUpdateSerializer
        return ProcurementRequestSerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'organization'):
            return self.queryset
        return self.queryset.none()
    
    def perform_create(self, serializer):
        serializer.save(
            requested_by=self.request.user,
            organization=self.request.user.organization
        )
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update procurement request status."""
        request_obj = self.get_object()
        serializer = ProcurementRequestStatusUpdateSerializer(
            request_obj, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a procurement request."""
        request_obj = self.get_object()
        if request_obj.status != 'under_review':
            return Response(
                {'error': 'Only requests under review can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        request_obj.status = 'approved'
        request_obj.reviewed_by = request.user
        request_obj.review_date = timezone.now()
        request_obj.save()
        
        serializer = self.get_serializer(request_obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a procurement request."""
        request_obj = self.get_object()
        if request_obj.status != 'under_review':
            return Response(
                {'error': 'Only requests under review can be rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rejection_reason = request.data.get('rejection_reason', '')
        if not rejection_reason:
            return Response(
                {'error': 'Rejection reason is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        request_obj.status = 'rejected'
        request_obj.reviewed_by = request.user
        request_obj.review_date = timezone.now()
        request_obj.rejection_reason = rejection_reason
        request_obj.save()
        
        serializer = self.get_serializer(request_obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def convert_to_po(self, request, pk=None):
        """Convert approved procurement request to purchase order."""
        request_obj = self.get_object()
        if request_obj.status != 'approved':
            return Response(
                {'error': 'Only approved requests can be converted to purchase orders'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create purchase order from procurement request
        # This would need to be implemented based on business logic
        request_obj.status = 'converted'
        request_obj.save()
        
        serializer = self.get_serializer(request_obj)
        return Response(serializer.data)


@extend_schema(tags=['Purchasing'])
class ProcurementRequestItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing procurement request items.
    """
    queryset = ProcurementRequestItem.objects.all()
    serializer_class = ProcurementRequestItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'organization'):
            return self.queryset.filter(request__organization=user.organization)
        return self.queryset.none()


@extend_schema(tags=['Purchasing'])
class SupplierPerformanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing supplier performance records.
    """
    queryset = SupplierPerformance.objects.all()
    serializer_class = SupplierPerformanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend]
    filterset_class = SupplierPerformanceFilter
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SupplierPerformanceSummarySerializer
        return SupplierPerformanceSerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'organization'):
            return self.queryset
        return self.queryset.none()
    
    def perform_create(self, serializer):
        serializer.save(
            evaluated_by=self.request.user
        )
    
    @action(detail=False, methods=['get'])
    def top_performers(self, request):
        """Get top performing suppliers."""
        queryset = self.get_queryset().order_by('-overall_rating')[:10]
        serializer = SupplierPerformanceSummarySerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def performance_trends(self, request):
        """Get supplier performance trends."""
        queryset = self.get_queryset()
        
        # Group by supplier and get latest performance
        trends = queryset.values('supplier__name').annotate(
            latest_rating=Avg('overall_rating'),
            latest_delivery_rate=Avg('on_time_delivery_rate'),
            latest_quality=Avg('quality_rating'),
            evaluation_count=Count('id')
        ).order_by('-latest_rating')
        
        return Response(list(trends))


@extend_schema(tags=['Purchasing'])
class PurchaseAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing purchase analytics.
    """
    queryset = PurchaseAnalytics.objects.all()
    serializer_class = PurchaseAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend]
    filterset_class = PurchaseAnalyticsFilter
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'organization'):
            return self.queryset
        return self.queryset.none()
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get purchasing dashboard data."""
        queryset = self.get_queryset()
        
        # Get current period analytics
        current_period = queryset.filter(
            period_end__gte=timezone.now() - timedelta(days=30)
        ).first()
        
        # Get previous period for comparison
        previous_period = queryset.filter(
            period_end__gte=timezone.now() - timedelta(days=60),
            period_end__lt=timezone.now() - timedelta(days=30)
        ).first()
        
        dashboard_data = {
            'current_period': PurchaseAnalyticsSerializer(current_period).data if current_period else None,
            'previous_period': PurchaseAnalyticsSerializer(previous_period).data if previous_period else None,
            'trends': self._get_trends(queryset),
            'alerts': self._get_alerts(queryset),
        }
        
        return Response(dashboard_data)
    
    def _get_trends(self, queryset):
        """Get purchasing trends."""
        return {
            'monthly_spending': list(queryset.values('period_start', 'total_value').order_by('period_start')),
            'order_volume': list(queryset.values('period_start', 'total_orders').order_by('period_start')),
            'supplier_diversity': list(queryset.values('period_start', 'active_suppliers').order_by('period_start')),
        }
    
    def _get_alerts(self, queryset):
        """Get purchasing alerts."""
        alerts = []
        
        # Check for overdue orders
        from apps.purchasing.models import PurchaseOrder
        overdue_orders = PurchaseOrder.objects.filter(
            expected_delivery_date__lt=timezone.now(),
            status__in=['sent', 'partially_received']
        ).count()
        
        if overdue_orders > 0:
            alerts.append({
                'type': 'warning',
                'message': f'{overdue_orders} purchase orders are overdue',
                'count': overdue_orders
            })
        
        # Check for pending approvals
        pending_approvals = PurchaseOrder.objects.filter(
            status='pending_approval'
        ).count()
        
        if pending_approvals > 0:
            alerts.append({
                'type': 'info',
                'message': f'{pending_approvals} purchase orders pending approval',
                'count': pending_approvals
            })
        
        return alerts
