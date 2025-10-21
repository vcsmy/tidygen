"""
Wallet Views

This module defines Django REST Framework views for wallet-based authentication,
including wallet management, signature requests, and transaction signing.
"""

import logging
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from .models import Wallet, WalletSignature, WalletPermission, WalletSession
from .serializers import (
    WalletSerializer,
    WalletCreateSerializer,
    WalletSignatureSerializer,
    WalletSignatureRequestSerializer,
    WalletSignatureVerifySerializer,
    WalletPermissionSerializer,
    WalletSessionSerializer,
    WalletConnectSerializer,
    WalletDisconnectSerializer,
    TransactionSignatureRequestSerializer,
    WalletStatusSerializer,
    SupportedWalletsSerializer
)
from .services import WalletService

User = get_user_model()
logger = logging.getLogger(__name__)


@extend_schema(tags=['Wallet'])
class WalletViewSet(viewsets.ModelViewSet):
    """
    ViewSet for wallet management.
    
    Provides CRUD operations for user wallets including connection,
    verification, and management.
    """
    
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get wallets for the authenticated user."""
        return Wallet.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """Create a new wallet connection."""
        serializer = WalletCreateSerializer(data=request.data)
        if serializer.is_valid():
            wallet = serializer.save()
            return Response(
                WalletSerializer(wallet).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def set_primary(self, request, pk=None):
        """Set a wallet as the user's primary wallet."""
        wallet_service = WalletService()
        
        result = wallet_service.set_primary_wallet(
            user_id=str(request.user.id),
            wallet_id=str(pk)
        )
        
        if 'error' in result:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(result, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def disconnect(self, request, pk=None):
        """Disconnect a wallet."""
        wallet_service = WalletService()
        
        result = wallet_service.disconnect_wallet(
            user_id=str(request.user.id),
            wallet_id=str(pk)
        )
        
        if 'error' in result:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(result, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get wallet connection status."""
        try:
            wallet = self.get_object()
            wallet_service = WalletService()
            
            # Get wallet-specific service
            if wallet.wallet_type == 'metamask':
                service = wallet_service.metamask_service
            elif wallet.wallet_type == 'polkadot':
                service = wallet_service.polkadot_service
            else:
                return Response(
                    {'error': 'Unsupported wallet type'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get network info
            network_info = service.get_network_info()
            balance_info = service.get_address_balance(wallet.address)
            
            status_data = {
                'connected': service.is_connected(),
                'wallet_type': wallet.wallet_type,
                'address': wallet.address,
                'network_name': network_info.get('network_name', 'Unknown'),
                'chain_id': network_info.get('chain_id', 'Unknown'),
                'balance': balance_info,
                'is_verified': wallet.is_verified,
                'last_used': wallet.last_used
            }
            
            serializer = WalletStatusSerializer(status_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Wallet.DoesNotExist:
            return Response(
                {'error': 'Wallet not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Failed to get wallet status: {e}")
            return Response(
                {'error': 'Failed to get wallet status'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WalletConnectView(APIView):
    """
    API view for wallet connection.
    
    Handles initial wallet connection and setup.
    """
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Connect a wallet to the system."""
        serializer = WalletConnectSerializer(data=request.data)
        if serializer.is_valid():
            wallet_service = WalletService()
            
            result = wallet_service.connect_wallet(
                wallet_type=serializer.validated_data['wallet_type'],
                address=serializer.validated_data['address'],
                chain_id=serializer.validated_data['chain_id'],
                network_name=serializer.validated_data['network_name'],
                public_key=serializer.validated_data.get('public_key'),
                metadata=serializer.validated_data.get('metadata', {})
            )
            
            if 'error' in result:
                return Response(
                    {'error': result['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(result, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WalletAuthenticationView(APIView):
    """
    API view for wallet authentication.
    
    Handles signature requests and verification for wallet authentication.
    """
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Request wallet authentication signature."""
        serializer = WalletSignatureRequestSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        """Verify wallet authentication signature."""
        serializer = WalletSignatureVerifySerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Wallet'])
class WalletSignatureViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for wallet signatures.
    
    Provides read-only access to signature requests and verification status.
    """
    
    serializer_class = WalletSignatureSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get signatures for user's wallets."""
        user_wallets = Wallet.objects.filter(user=self.request.user)
        return WalletSignature.objects.filter(
            wallet__in=user_wallets
        ).order_by('-created_at')


@extend_schema(tags=['Wallet'])
class WalletPermissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for wallet permissions.
    
    Provides CRUD operations for wallet-based permissions and access control.
    """
    
    serializer_class = WalletPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get permissions for user's wallets."""
        user_wallets = Wallet.objects.filter(user=self.request.user)
        return WalletPermission.objects.filter(
            wallet__in=user_wallets
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set the user who granted the permission."""
        serializer.save(granted_by=self.request.user)


@extend_schema(tags=['Wallet'])
class WalletSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for wallet sessions.
    
    Provides read-only access to active wallet authentication sessions.
    """
    
    serializer_class = WalletSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get active sessions for user's wallets."""
        user_wallets = Wallet.objects.filter(user=self.request.user)
        return WalletSession.objects.filter(
            wallet__in=user_wallets,
            is_active=True
        ).order_by('-last_activity')
    
    @action(detail=True, methods=['post'])
    def extend(self, request, pk=None):
        """Extend session expiration time."""
        try:
            session = self.get_object()
            hours = request.data.get('hours', 24)
            
            session.extend(hours=hours)
            
            return Response(
                {'message': f'Session extended by {hours} hours'},
                status=status.HTTP_200_OK
            )
        except WalletSession.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Failed to extend session: {e}")
            return Response(
                {'error': 'Failed to extend session'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a wallet session."""
        try:
            session = self.get_object()
            session.deactivate()
            
            return Response(
                {'message': 'Session deactivated'},
                status=status.HTTP_200_OK
            )
        except WalletSession.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Failed to deactivate session: {e}")
            return Response(
                {'error': 'Failed to deactivate session'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TransactionSignatureView(APIView):
    """
    API view for transaction signature requests.
    
    Handles requests for signing transactions with wallet.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Request signature for a transaction."""
        serializer = TransactionSignatureRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            wallet_service = WalletService()
            
            transaction_data = {
                'type': serializer.validated_data['transaction_type'],
                'amount': str(serializer.validated_data['amount']),
                'currency': serializer.validated_data['currency'],
                'description': serializer.validated_data['description'],
                'recipient': serializer.validated_data.get('recipient'),
                'metadata': serializer.validated_data.get('metadata', {})
            }
            
            result = wallet_service.request_transaction_signature(
                wallet_id=str(serializer.validated_data['wallet_id']),
                transaction_data=transaction_data,
                user_id=str(request.user.id)
            )
            
            if 'error' in result:
                return Response(
                    {'error': result['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(result, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        """Verify transaction signature."""
        signature_id = request.data.get('signature_id')
        signature = request.data.get('signature')
        
        if not signature_id or not signature:
            return Response(
                {'error': 'signature_id and signature are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        wallet_service = WalletService()
        
        result = wallet_service.verify_transaction_signature(
            signature_id=str(signature_id),
            signature=signature
        )
        
        if 'error' in result:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(result, status=status.HTTP_200_OK)


class SupportedWalletsView(APIView):
    """
    API view for supported wallet types.
    
    Provides information about available wallet integrations.
    """
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Get list of supported wallet types."""
        wallet_service = WalletService()
        supported_wallets = wallet_service.get_supported_wallet_types()
        
        serializer = SupportedWalletsSerializer(supported_wallets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WalletNetworkInfoView(APIView):
    """
    API view for wallet network information.
    
    Provides network status and configuration for different wallet types.
    """
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, wallet_type):
        """Get network information for a wallet type."""
        wallet_service = WalletService()
        
        if wallet_type == 'metamask':
            service = wallet_service.metamask_service
        elif wallet_type == 'polkadot':
            service = wallet_service.polkadot_service
        else:
            return Response(
                {'error': 'Unsupported wallet type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        network_info = service.get_network_info()
        supported_networks = service.get_supported_networks()
        
        return Response({
            'network_info': network_info,
            'supported_networks': supported_networks
        }, status=status.HTTP_200_OK)


class WalletAccountInfoView(APIView):
    """
    API view for wallet account information.
    
    Provides account details and balance information.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, wallet_id):
        """Get account information for a wallet."""
        try:
            wallet = Wallet.objects.get(
                id=wallet_id,
                user=request.user,
                is_active=True
            )
            
            wallet_service = WalletService()
            
            # Get wallet-specific service
            if wallet.wallet_type == 'metamask':
                service = wallet_service.metamask_service
            elif wallet.wallet_type == 'polkadot':
                service = wallet_service.polkadot_service
            else:
                return Response(
                    {'error': 'Unsupported wallet type'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            account_info = service.get_account_info(wallet.address)
            
            if 'error' in account_info:
                return Response(
                    {'error': account_info['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(account_info, status=status.HTTP_200_OK)
            
        except Wallet.DoesNotExist:
            return Response(
                {'error': 'Wallet not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Failed to get account info: {e}")
            return Response(
                {'error': 'Failed to get account info'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
