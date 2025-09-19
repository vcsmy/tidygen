"""
DID Authentication Views

Django REST Framework views for DID-based authentication.
"""

import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Q

from .models import DIDDocument, DIDRole, DIDCredential, DIDSession, DIDPermission
from .serializers import (
    DIDDocumentSerializer, DIDRoleSerializer, DIDCredentialSerializer,
    DIDSessionSerializer, DIDPermissionSerializer, DIDLoginSerializer,
    DIDCreateSerializer, DIDRoleAssignSerializer, DIDCredentialIssueSerializer,
    DIDSignatureVerifySerializer, DIDSessionInfoSerializer
)
from .services import (
    DIDService, DIDAuthService, DIDRoleService, DIDCredentialService,
    DIDBlockchainService, DIDRegistrySyncService
)

logger = logging.getLogger(__name__)


class DIDDocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing DID documents.
    """
    queryset = DIDDocument.objects.all()
    serializer_class = DIDDocumentSerializer
    filterset_fields = ['status', 'controller']
    search_fields = ['did', 'controller']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_permissions(self):
        """
        Set permissions based on action.
        """
        if self.action in ['create', 'update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'], url_path='verify-signature')
    def verify_signature(self, request, pk=None):
        """
        Verify a signature using the DID's verification method.
        """
        did_doc = self.get_object()
        serializer = DIDSignatureVerifySerializer(data=request.data)
        
        if serializer.is_valid():
            message = serializer.validated_data['message']
            signature = serializer.validated_data['signature']
            verification_method = serializer.validated_data.get('verification_method')
            
            is_valid = DIDService.verify_did_signature(
                did_doc.did, message, signature, verification_method
            )
            
            return Response({
                'valid': is_valid,
                'did': did_doc.did,
                'message': 'Signature verified' if is_valid else 'Invalid signature'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='sync-to-registry')
    def sync_to_registry(self, request, pk=None):
        """
        Sync a DID document to the on-chain registry.
        """
        did_doc = self.get_object()
        registry_sync = DIDRegistrySyncService()
        
        result = registry_sync.sync_did_to_registry(did_doc)
        
        if result['success']:
            return Response({
                'status': 'synced',
                'did': did_doc.did,
                'tx_hash': result['tx_hash'],
                'block_number': result.get('block_number'),
                'gas_used': result.get('gas_used')
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'sync_failed',
                'error': result['error']
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='sync-from-registry')
    def sync_from_registry(self, request):
        """
        Sync a DID document from the on-chain registry.
        """
        did_string = request.data.get('did')
        if not did_string:
            return Response({'error': 'DID string is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        registry_sync = DIDRegistrySyncService()
        result = registry_sync.sync_did_from_registry(did_string)
        
        if result['success']:
            return Response({
                'status': 'resolved',
                'did': result['did'],
                'document': result['document']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'resolve_failed',
                'error': result['error']
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='deactivate-on-registry')
    def deactivate_on_registry(self, request, pk=None):
        """
        Deactivate a DID on the on-chain registry.
        """
        did_doc = self.get_object()
        registry_sync = DIDRegistrySyncService()
        
        result = registry_sync.deactivate_did_on_registry(did_doc)
        
        if result['success']:
            return Response({
                'status': 'deactivated',
                'did': did_doc.did,
                'tx_hash': result['tx_hash'],
                'block_number': result.get('block_number')
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'deactivation_failed',
                'error': result['error']
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='registry-status')
    def registry_status(self, request):
        """
        Get the registry status of a DID.
        """
        did_string = request.query_params.get('did')
        if not did_string:
            return Response({'error': 'DID string is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        registry_sync = DIDRegistrySyncService()
        result = registry_sync.get_registry_status(did_string)
        
        return Response({
            'did': did_string,
            'status': result['status'],
            'success': result['success'],
            'error': result.get('error'),
            'document': result.get('document')
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='network-info')
    def network_info(self, request):
        """
        Get information about the connected blockchain network.
        """
        registry_sync = DIDRegistrySyncService()
        info = registry_sync.get_network_info()
        
        return Response(info, status=status.HTTP_200_OK)


class DIDRoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing DID roles.
    """
    queryset = DIDRole.objects.all()
    serializer_class = DIDRoleSerializer
    filterset_fields = ['role_name', 'is_active', 'did']
    search_fields = ['did__did', 'role_name', 'custom_role_name']
    ordering_fields = ['granted_at']
    ordering = ['-granted_at']

    def get_permissions(self):
        """
        Set permissions based on action.
        """
        if self.action in ['create', 'update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['post'], url_path='assign-role')
    def assign_role(self, request):
        """
        Assign a role to a DID.
        """
        serializer = DIDRoleAssignSerializer(data=request.data)
        
        if serializer.is_valid():
            did = serializer.validated_data['did']
            role_name = serializer.validated_data['role_name']
            custom_role_name = serializer.validated_data.get('custom_role_name', '')
            permissions = serializer.validated_data.get('permissions', [])
            expires_at = serializer.validated_data.get('expires_at')
            
            # For now, we'll use a system DID as the granter
            granted_by = "did:system:admin"
            
            role = DIDRoleService.assign_role(
                did=did,
                role_name=role_name,
                granted_by=granted_by,
                permissions=permissions,
                expires_at=expires_at,
                custom_role_name=custom_role_name
            )
            
            if role:
                return Response({
                    'status': 'role assigned',
                    'role': DIDRoleSerializer(role).data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'status': 'failed to assign role',
                'error': 'DID not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DIDSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing DID sessions (read-only).
    """
    queryset = DIDSession.objects.all()
    serializer_class = DIDSessionSerializer
    filterset_fields = ['is_active', 'did']
    search_fields = ['did__did', 'session_token']
    ordering_fields = ['created_at', 'last_activity']
    ordering = ['-created_at']

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        """
        Authenticate using DID signature.
        """
        serializer = DIDLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            did = serializer.validated_data['did']
            signature = serializer.validated_data['signature']
            message = serializer.validated_data['message']
            ip_address = serializer.validated_data.get('ip_address')
            user_agent = serializer.validated_data.get('user_agent', '')
            
            success, session, error = DIDAuthService.authenticate_did(
                did=did,
                signature=signature,
                message=message,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            if success:
                return Response({
                    'status': 'authenticated',
                    'session': DIDSessionSerializer(session).data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'status': 'authentication failed',
                'error': error
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='logout')
    def logout(self, request):
        """
        Logout and terminate session.
        """
        session_token = request.data.get('session_token')
        
        if not session_token:
            return Response({
                'status': 'logout failed',
                'error': 'Session token required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        success = DIDAuthService.terminate_session(session_token)
        
        if success:
            return Response({
                'status': 'logged out',
                'session_token': session_token
            }, status=status.HTTP_200_OK)
        
        return Response({
            'status': 'logout failed',
            'error': 'Invalid session token'
        }, status=status.HTTP_404_NOT_FOUND)


class DIDCredentialViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing DID credentials.
    """
    queryset = DIDCredential.objects.all()
    serializer_class = DIDCredentialSerializer
    filterset_fields = ['credential_type', 'issuer', 'revoked']
    search_fields = ['did__did', 'credential_type', 'issuer']
    ordering_fields = ['issued_at']
    ordering = ['-issued_at']

    def get_permissions(self):
        """
        Set permissions based on action.
        """
        if self.action in ['create', 'update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class DIDPermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing DID permissions (read-only).
    """
    queryset = DIDPermission.objects.all()
    serializer_class = DIDPermissionSerializer
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'display_name', 'description']
    ordering_fields = ['category', 'name']
    ordering = ['category', 'name']