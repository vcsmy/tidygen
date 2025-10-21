"""
Smart Contract Ledger Views

This module defines the REST API views for the Smart Contract Ledger functionality,
providing endpoints for transaction management, verification, and audit trails.
"""

import logging
from typing import Dict, Any
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema

from .models import LedgerTransaction, LedgerEvent, LedgerBatch, LedgerConfiguration
from .serializers import (
    LedgerTransactionSerializer,
    LedgerTransactionCreateSerializer,
    LedgerTransactionUpdateSerializer,
    LedgerEventSerializer,
    LedgerBatchSerializer,
    LedgerBatchCreateSerializer,
    LedgerConfigurationSerializer,
    LedgerTransactionVerifySerializer,
    LedgerTransactionVerifyResponseSerializer,
    LedgerAuditTrailSerializer,
    LedgerAuditTrailResponseSerializer,
    LedgerStatsSerializer
)
from .services import TransactionService

logger = logging.getLogger(__name__)


@extend_schema(tags=['Ledger'])
class LedgerTransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing ledger transactions.
    
    Provides CRUD operations for ledger transactions and additional
    actions for blockchain submission and verification.
    """
    
    queryset = LedgerTransaction.objects.all()
    serializer_class = LedgerTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['transaction_type', 'status', 'source_module']
    search_fields = ['source_id', 'hash', 'blockchain_hash']
    ordering_fields = ['created_at', 'confirmed_at', 'amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter queryset by organization."""
        queryset = super().get_queryset()
        
        # Filter by organization if user is authenticated
        if self.request.user.is_authenticated and hasattr(self.request.user, 'organization'):
            queryset = queryset.filter(organization=self.request.user.organization)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return LedgerTransactionCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return LedgerTransactionUpdateSerializer
        return LedgerTransactionSerializer
    
    def perform_create(self, serializer):
        """Create a new ledger transaction."""
        try:
            # Create transaction using service
            transaction_service = TransactionService(
                organization_id=str(self.request.user.organization.id)
            )
            
            ledger_transaction = transaction_service.create_transaction(
                transaction_type=serializer.validated_data['transaction_type'],
                source_module=serializer.validated_data['source_module'],
                source_id=serializer.validated_data['source_id'],
                transaction_data=serializer.validated_data['transaction_data'],
                organization_id=str(self.request.user.organization.id),
                created_by_id=str(self.request.user.id)
            )
            
            # Set the created instance for the response
            serializer.instance = ledger_transaction
            
        except Exception as e:
            logger.error(f"Failed to create ledger transaction: {e}")
            raise ValidationError(str(e))
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        Submit a transaction to the blockchain.
        
        POST /api/ledger/transactions/{id}/submit/
        """
        try:
            ledger_transaction = self.get_object()
            
            # Initialize transaction service
            transaction_service = TransactionService(
                organization_id=str(ledger_transaction.organization.id)
            )
            
            # Submit transaction
            success = transaction_service.submit_transaction(ledger_transaction)
            
            if success:
                # Refresh the transaction
                ledger_transaction.refresh_from_db()
                
                return Response({
                    'message': 'Transaction submitted successfully',
                    'transaction': LedgerTransactionSerializer(ledger_transaction).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Failed to submit transaction to blockchain'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Failed to submit transaction {pk}: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        Confirm a transaction on the blockchain.
        
        POST /api/ledger/transactions/{id}/confirm/
        """
        try:
            ledger_transaction = self.get_object()
            
            # Initialize transaction service
            transaction_service = TransactionService(
                organization_id=str(ledger_transaction.organization.id)
            )
            
            # Get confirmation data from request
            block_number = request.data.get('block_number')
            transaction_index = request.data.get('transaction_index')
            gas_used = request.data.get('gas_used')
            gas_price = request.data.get('gas_price')
            
            # Confirm transaction
            success = transaction_service.confirm_transaction(
                ledger_transaction=ledger_transaction,
                block_number=block_number,
                transaction_index=transaction_index,
                gas_used=gas_used,
                gas_price=gas_price
            )
            
            if success:
                # Refresh the transaction
                ledger_transaction.refresh_from_db()
                
                return Response({
                    'message': 'Transaction confirmed successfully',
                    'transaction': LedgerTransactionSerializer(ledger_transaction).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Failed to confirm transaction on blockchain'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Failed to confirm transaction {pk}: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """
        Verify a transaction's integrity.
        
        POST /api/ledger/transactions/{id}/verify/
        """
        try:
            ledger_transaction = self.get_object()
            
            # Initialize transaction service
            transaction_service = TransactionService(
                organization_id=str(ledger_transaction.organization.id)
            )
            
            # Get verification options from request
            verify_hash = request.data.get('verify_hash', True)
            verify_blockchain = request.data.get('verify_blockchain', True)
            
            # Verify transaction
            verification_result = transaction_service.verify_transaction(
                ledger_transaction=ledger_transaction,
                verify_hash=verify_hash,
                verify_blockchain=verify_blockchain
            )
            
            return Response(verification_result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to verify transaction {pk}: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get transaction statistics.
        
        GET /api/ledger/transactions/stats/
        """
        try:
            # Initialize transaction service
            transaction_service = TransactionService(
                organization_id=str(request.user.organization.id)
            )
            
            # Get statistics
            stats = transaction_service.get_transaction_stats()
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to get transaction stats: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LedgerPushView(APIView):
    """
    API view for pushing transactions to the ledger.
    
    This is the main endpoint for submitting financial transactions
    to the blockchain ledger as specified in the requirements.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Push a transaction to the ledger.
        
        POST /api/ledger/push/
        
        Expected payload:
        {
            "transaction_type": "invoice",
            "source_module": "finance",
            "source_id": "INV-001",
            "transaction_data": {
                "amount": 1000.00,
                "currency": "USD",
                "description": "Invoice payment"
            }
        }
        
        Returns:
        {
            "id": "uuid",
            "hash": "sha256_hash",
            "status": "pending",
            "message": "Transaction logged successfully"
        }
        """
        try:
            logger.info(f"Received ledger push request from user {request.user.id}")
            
            # Validate request data
            serializer = LedgerTransactionCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': 'Invalid transaction data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create transaction using service
            transaction_service = TransactionService(
                organization_id=str(request.user.organization.id)
            )
            
            ledger_transaction = transaction_service.create_transaction(
                transaction_type=serializer.validated_data['transaction_type'],
                source_module=serializer.validated_data['source_module'],
                source_id=serializer.validated_data['source_id'],
                transaction_data=serializer.validated_data['transaction_data'],
                organization_id=str(request.user.organization.id),
                created_by_id=str(request.user.id)
            )
            
            # Auto-submit if configured
            if hasattr(request.user.organization, 'ledger_config') and request.user.organization.ledger_config.auto_confirm:
                transaction_service.submit_transaction(ledger_transaction)
                ledger_transaction.refresh_from_db()
            
            # Return response
            return Response({
                'id': str(ledger_transaction.id),
                'hash': ledger_transaction.hash,
                'blockchain_hash': ledger_transaction.blockchain_hash,
                'status': ledger_transaction.status,
                'message': 'Transaction logged successfully',
                'created_at': ledger_transaction.created_at
            }, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            logger.error(f"Validation error in ledger push: {e}")
            return Response({
                'error': 'Validation failed',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Failed to push transaction to ledger: {e}")
            return Response({
                'error': 'Failed to log transaction',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LedgerVerifyView(APIView):
    """
    API view for verifying transactions.
    
    Provides endpoint for verifying transaction integrity and blockchain status.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, transaction_id):
        """
        Verify a transaction.
        
        GET /api/ledger/verify/{transaction_id}/
        
        Query parameters:
        - verify_hash: bool (default: true)
        - verify_blockchain: bool (default: true)
        """
        try:
            # Get transaction
            try:
                ledger_transaction = LedgerTransaction.objects.get(
                    id=transaction_id,
                    organization=request.user.organization
                )
            except LedgerTransaction.DoesNotExist:
                return Response({
                    'error': 'Transaction not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Initialize transaction service
            transaction_service = TransactionService(
                organization_id=str(request.user.organization.id)
            )
            
            # Get verification options from query parameters
            verify_hash = request.query_params.get('verify_hash', 'true').lower() == 'true'
            verify_blockchain = request.query_params.get('verify_blockchain', 'true').lower() == 'true'
            
            # Verify transaction
            verification_result = transaction_service.verify_transaction(
                ledger_transaction=ledger_transaction,
                verify_hash=verify_hash,
                verify_blockchain=verify_blockchain
            )
            
            return Response(verification_result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to verify transaction {transaction_id}: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LedgerAuditTrailView(APIView):
    """
    API view for retrieving audit trail information.
    
    Provides endpoint for getting comprehensive audit trail data.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Get audit trail.
        
        GET /api/ledger/audit/
        
        Query parameters:
        - start_date: ISO datetime
        - end_date: ISO datetime
        - transaction_type: string
        - status: string
        - source_module: string
        - limit: int (default: 100, max: 1000)
        - offset: int (default: 0)
        """
        try:
            # Validate query parameters
            serializer = LedgerAuditTrailSerializer(data=request.query_params)
            if not serializer.is_valid():
                return Response({
                    'error': 'Invalid query parameters',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            validated_data = serializer.validated_data
            
            # Build queryset
            queryset = LedgerTransaction.objects.filter(
                organization=request.user.organization
            )
            
            # Apply filters
            if validated_data.get('start_date'):
                queryset = queryset.filter(created_at__gte=validated_data['start_date'])
            
            if validated_data.get('end_date'):
                queryset = queryset.filter(created_at__lte=validated_data['end_date'])
            
            if validated_data.get('transaction_type'):
                queryset = queryset.filter(transaction_type=validated_data['transaction_type'])
            
            if validated_data.get('status'):
                queryset = queryset.filter(status=validated_data['status'])
            
            if validated_data.get('source_module'):
                queryset = queryset.filter(source_module=validated_data['source_module'])
            
            # Get total count
            total_count = queryset.count()
            
            # Apply pagination
            limit = validated_data.get('limit', 100)
            offset = validated_data.get('offset', 0)
            
            transactions = queryset.order_by('-created_at')[offset:offset + limit]
            
            # Serialize transactions
            transaction_serializer = LedgerTransactionSerializer(transactions, many=True)
            
            # Build response
            response_data = {
                'transactions': transaction_serializer.data,
                'total_count': total_count,
                'has_next': offset + limit < total_count,
                'has_previous': offset > 0,
                'next_offset': offset + limit if offset + limit < total_count else None,
                'previous_offset': max(0, offset - limit) if offset > 0 else None
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to get audit trail: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(tags=['Ledger'])
class LedgerBatchViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing ledger batches.
    
    Provides CRUD operations for transaction batches and batch submission.
    """
    
    queryset = LedgerBatch.objects.all()
    serializer_class = LedgerBatchSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['batch_hash', 'blockchain_hash']
    ordering_fields = ['created_at', 'submitted_at', 'confirmed_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter queryset by organization."""
        queryset = super().get_queryset()
        
        # Filter by organization if user is authenticated
        if self.request.user.is_authenticated and hasattr(self.request.user, 'organization'):
            queryset = queryset.filter(organization=self.request.user.organization)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return LedgerBatchCreateSerializer
        return LedgerBatchSerializer
    
    def perform_create(self, serializer):
        """Create a new ledger batch."""
        try:
            # Create batch using service
            transaction_service = TransactionService(
                organization_id=str(self.request.user.organization.id)
            )
            
            batch = transaction_service.create_batch(
                transaction_ids=serializer.validated_data['transaction_ids'],
                organization_id=str(self.request.user.organization.id)
            )
            
            # Set the created instance for the response
            serializer.instance = batch
            
        except Exception as e:
            logger.error(f"Failed to create ledger batch: {e}")
            raise ValidationError(str(e))
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        Submit a batch to the blockchain.
        
        POST /api/ledger/batches/{id}/submit/
        """
        try:
            ledger_batch = self.get_object()
            
            # Initialize transaction service
            transaction_service = TransactionService(
                organization_id=str(ledger_batch.organization.id)
            )
            
            # Submit batch
            success = transaction_service.submit_batch(ledger_batch)
            
            if success:
                # Refresh the batch
                ledger_batch.refresh_from_db()
                
                return Response({
                    'message': 'Batch submitted successfully',
                    'batch': LedgerBatchSerializer(ledger_batch).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Failed to submit batch to blockchain'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Failed to submit batch {pk}: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(tags=['Ledger'])
class LedgerEventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for ledger events.
    
    Provides read access to audit trail events.
    """
    
    queryset = LedgerEvent.objects.all()
    serializer_class = LedgerEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['event_type', 'transaction']
    search_fields = ['transaction__source_id', 'blockchain_event_id']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter queryset by organization."""
        queryset = super().get_queryset()
        
        # Filter by organization if user is authenticated
        if self.request.user.is_authenticated and hasattr(self.request.user, 'organization'):
            queryset = queryset.filter(
                transaction__organization=self.request.user.organization
            )
        
        return queryset


@extend_schema(tags=['Ledger'])
class LedgerConfigurationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing ledger configuration.
    
    Provides CRUD operations for ledger configuration settings.
    """
    
    queryset = LedgerConfiguration.objects.all()
    serializer_class = LedgerConfigurationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset by organization."""
        queryset = super().get_queryset()
        
        # Filter by organization if user is authenticated
        if self.request.user.is_authenticated and hasattr(self.request.user, 'organization'):
            queryset = queryset.filter(organization=self.request.user.organization)
        
        return queryset
    
    def perform_create(self, serializer):
        """Create a new ledger configuration."""
        # Set organization from context
        serializer.save(organization=self.request.user.organization)
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """
        Test blockchain connection.
        
        POST /api/ledger/configurations/{id}/test_connection/
        """
        try:
            config = self.get_object()
            
            # Initialize blockchain service
            blockchain_service = BlockchainService(
                network=config.blockchain_network,
                rpc_endpoint=config.rpc_endpoint
            )
            
            # Test connection
            is_connected = blockchain_service.is_connected()
            
            return Response({
                'connected': is_connected,
                'message': 'Connection test completed'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to test connection for config {pk}: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
