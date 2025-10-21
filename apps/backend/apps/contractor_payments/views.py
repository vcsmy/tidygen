"""
Views for contractor_payments app API.
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Sum
from apps.core.permissions import IsOwnerOrReadOnly
from drf_spectacular.utils import extend_schema
from .models import (
    PaymentMethod, ContractorPayment, EscrowAccount,
    PaymentSchedule, DisputeResolution
)
from .serializers import (
    PaymentMethodSerializer, ContractorPaymentListSerializer, ContractorPaymentDetailSerializer,
    EscrowAccountSerializer, PaymentScheduleSerializer, DisputeResolutionSerializer
)


@extend_schema(tags=['Contractor Payments'])
class PaymentMethodListView(generics.ListAPIView):
    """
    List all active payment methods.
    """
    queryset = PaymentMethod.objects.filter(is_active=True)
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(tags=['Contractor Payments'])
class ContractorPaymentListCreateView(generics.ListCreateAPIView):
    """
    List contractor payments or create a new one.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see payments related to their freelancer profile
        try:
            freelancer = self.request.user.freelancer_profile
            return ContractorPayment.objects.filter(freelancer=freelancer).select_related(
                'freelancer', 'job', 'payment_method'
            )
        except:
            return ContractorPayment.objects.none()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ContractorPaymentDetailSerializer
        return ContractorPaymentListSerializer
    
    def perform_create(self, serializer):
        # Set freelancer from current user's profile
        freelancer = self.request.user.freelancer_profile
        serializer.save(freelancer=freelancer, created_by=self.request.user)


@extend_schema(tags=['Contractor Payments'])
class ContractorPaymentDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update a contractor payment instance.
    """
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        try:
            freelancer = self.request.user.freelancer_profile
            return ContractorPayment.objects.filter(freelancer=freelancer)
        except:
            return ContractorPayment.objects.none()
    
    serializer_class = ContractorPaymentDetailSerializer


@extend_schema(tags=['Contractor Payments'])
class EscrowAccountListCreateView(generics.ListCreateAPIView):
    """
    List escrow accounts or create a new one.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can see escrow accounts where they are client or freelancer
        try:
            freelancer = self.request.user.freelancer_profile
            return EscrowAccount.objects.filter(
                Q(client=self.request.user) | Q(freelancer=freelancer)
            ).select_related('job', 'client', 'freelancer')
        except:
            return EscrowAccount.objects.filter(client=self.request.user).select_related(
                'job', 'client', 'freelancer'
            )
    
    serializer_class = EscrowAccountSerializer


@extend_schema(tags=['Contractor Payments'])
class PaymentScheduleView(generics.ListCreateAPIView):
    """
    List and manage payment schedules for freelancers.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        try:
            freelancer = self.request.user.freelancer_profile
            return PaymentSchedule.objects.filter(freelancer=freelancer).select_related(
                'freelancer', 'payment_method'
            )
        except:
            return PaymentSchedule.objects.none()
    
    serializer_class = PaymentScheduleSerializer


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def payment_statistics(request, freelancer_id):
    """
    Get payment statistics for a freelancer.
    """
    try:
        freelancer = request.user.freelancer_profile
    except:
        return Response(
            {'error': 'Freelancer profile not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    payments = ContractorPayment.objects.filter(freelancer=freelancer)
    
    total_paid = payments.filter(status='completed').aggregate(
        total=Sum('net_amount')
    )['total'] or 0
    
    pending_amount = payments.filter(status='pending').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    stats = {
        'freelancer_id': freelancer.freelancer_id,
        'total_payments': payments.count(),
        'completed_payments': payments.filter(status='completed').count(),
        'pending_payments': payments.filter(status='pending').count(),
        'total_paid': float(total_paid),
        'pending_amount': float(pending_amount),
        'average_payment': float(total_paid / payments.filter(status='completed').count()) if payments.filter(status='completed').exists() else 0
    }
    
    return Response(stats)
