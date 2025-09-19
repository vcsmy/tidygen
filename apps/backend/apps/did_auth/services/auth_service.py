"""
DID Authentication Service

Service for handling DID-based authentication and session management.
"""

import uuid
import hashlib
from typing import Dict, Any, Optional, Tuple
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import timedelta

from ..models import DIDDocument, DIDSession, DIDRole
from .did_service import DIDService


class DIDAuthService:
    """
    Service for DID-based authentication and session management.
    """

    @staticmethod
    def authenticate_did(
        did: str,
        signature: str,
        message: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[bool, Optional[DIDSession], Optional[str]]:
        """
        Authenticate a DID using signature verification.
        
        Args:
            did: The DID identifier
            signature: The signature to verify
            message: The message that was signed
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Tuple of (success, session, error_message)
        """
        try:
            # Get DID document
            did_doc = DIDService.get_did_document(did)
            if not did_doc:
                return False, None, "DID not found"
            
            # Check if DID is active
            if not did_doc.is_active():
                return False, None, "DID is not active"
            
            # Verify signature
            if not DIDService.verify_did_signature(did, message, signature):
                return False, None, "Invalid signature"
            
            # Create session
            session = DIDAuthService.create_session(
                did_doc, ip_address, user_agent
            )
            
            return True, session, None
            
        except Exception as e:
            return False, None, str(e)

    @staticmethod
    def create_session(
        did_doc: DIDDocument,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        duration_hours: int = 24
    ) -> DIDSession:
        """
        Create a new authentication session for a DID.
        
        Args:
            did_doc: The DID document
            ip_address: Client IP address
            user_agent: Client user agent
            duration_hours: Session duration in hours
            
        Returns:
            DIDSession instance
        """
        with transaction.atomic():
            # Generate session token
            session_token = DIDAuthService.generate_session_token()
            
            # Calculate expiration time
            expires_at = timezone.now() + timedelta(hours=duration_hours)
            
            # Create session
            session = DIDSession.objects.create(
                did=did_doc,
                session_token=session_token,
                expires_at=expires_at,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            return session

    @staticmethod
    def validate_session(session_token: str) -> Tuple[bool, Optional[DIDSession], Optional[str]]:
        """
        Validate a session token.
        
        Args:
            session_token: The session token to validate
            
        Returns:
            Tuple of (valid, session, error_message)
        """
        try:
            session = DIDSession.objects.get(session_token=session_token)
            
            if not session.is_valid():
                return False, None, "Session expired or inactive"
            
            # Update last activity
            session.last_activity = timezone.now()
            session.save(update_fields=['last_activity'])
            
            return True, session, None
            
        except DIDSession.DoesNotExist:
            return False, None, "Invalid session token"

    @staticmethod
    def terminate_session(session_token: str) -> bool:
        """
        Terminate a session.
        
        Args:
            session_token: The session token to terminate
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session = DIDSession.objects.get(session_token=session_token)
            session.terminate()
            return True
        except DIDSession.DoesNotExist:
            return False

    @staticmethod
    def terminate_all_sessions(did: str) -> int:
        """
        Terminate all sessions for a DID.
        
        Args:
            did: The DID identifier
            
        Returns:
            Number of sessions terminated
        """
        try:
            did_doc = DIDDocument.objects.get(did=did)
            sessions = did_doc.sessions.filter(is_active=True)
            count = sessions.count()
            
            for session in sessions:
                session.terminate()
            
            return count
        except DIDDocument.DoesNotExist:
            return 0

    @staticmethod
    def get_active_sessions(did: str) -> list:
        """
        Get all active sessions for a DID.
        
        Args:
            did: The DID identifier
            
        Returns:
            List of active DIDSession instances
        """
        try:
            did_doc = DIDDocument.objects.get(did=did)
            return list(did_doc.sessions.filter(is_active=True))
        except DIDDocument.DoesNotExist:
            return []

    @staticmethod
    def cleanup_expired_sessions() -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        expired_sessions = DIDSession.objects.filter(
            is_active=True,
            expires_at__lt=timezone.now()
        )
        
        count = expired_sessions.count()
        
        for session in expired_sessions:
            session.terminate()
        
        return count

    @staticmethod
    def generate_session_token() -> str:
        """
        Generate a unique session token.
        
        Returns:
            Unique session token string
        """
        # Generate a unique token
        unique_id = str(uuid.uuid4())
        timestamp = str(int(timezone.now().timestamp()))
        
        # Create hash for additional security
        token_data = f"{unique_id}:{timestamp}"
        token_hash = hashlib.sha256(token_data.encode()).hexdigest()
        
        return f"did_session_{token_hash[:32]}"

    @staticmethod
    def check_permission(
        session_token: str,
        permission: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if a session has a specific permission.
        
        Args:
            session_token: The session token
            permission: The permission to check
            
        Returns:
            Tuple of (has_permission, error_message)
        """
        valid, session, error = DIDAuthService.validate_session(session_token)
        
        if not valid:
            return False, error
        
        # Check if DID has the permission
        has_permission = DIDService.check_did_permission(session.did.did, permission)
        
        if not has_permission:
            return False, "Insufficient permissions"
        
        return True, None

    @staticmethod
    def get_session_info(session_token: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a session.
        
        Args:
            session_token: The session token
            
        Returns:
            Session information dictionary or None
        """
        valid, session, error = DIDAuthService.validate_session(session_token)
        
        if not valid:
            return None
        
        # Get DID roles
        roles = DIDService.get_did_roles(session.did.did)
        role_names = [role.role_name for role in roles if role.is_valid()]
        
        # Get all permissions
        permissions = []
        for role in roles:
            if role.is_valid():
                permissions.extend(role.permissions)
        
        return {
            'did': session.did.did,
            'controller': session.did.controller,
            'roles': role_names,
            'permissions': list(set(permissions)),  # Remove duplicates
            'created_at': session.created_at,
            'expires_at': session.expires_at,
            'last_activity': session.last_activity,
            'ip_address': str(session.ip_address) if session.ip_address else None,
            'user_agent': session.user_agent
        }

    @staticmethod
    def refresh_session(session_token: str, duration_hours: int = 24) -> Tuple[bool, Optional[str]]:
        """
        Refresh a session by extending its expiration time.
        
        Args:
            session_token: The session token
            duration_hours: New duration in hours
            
        Returns:
            Tuple of (success, error_message)
        """
        valid, session, error = DIDAuthService.validate_session(session_token)
        
        if not valid:
            return False, error
        
        # Extend session
        session.extend(duration_hours)
        
        return True, None
