"""
DID Service

Core service for managing DID documents and operations.
"""

import json
import uuid
import hashlib
from typing import Dict, Any, Optional, List
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError

from ..models import DIDDocument, DIDRole, DIDCredential


class DIDService:
    """
    Service for managing DID documents and operations.
    """

    @staticmethod
    def create_did_document(
        did: str,
        document: Dict[str, Any],
        controller: str,
        expires_at: Optional[timezone.datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DIDDocument:
        """
        Create a new DID document.
        
        Args:
            did: The DID identifier
            document: The DID document as per W3C specification
            controller: The DID of the controller
            expires_at: Optional expiration date
            metadata: Additional metadata
            
        Returns:
            DIDDocument instance
        """
        with transaction.atomic():
            # Validate DID format
            if not did.startswith('did:'):
                raise ValidationError("DID must start with 'did:'")
            
            # Validate document structure
            required_fields = ['@context', 'id', 'verificationMethod']
            for field in required_fields:
                if field not in document:
                    raise ValidationError(f"DID document must contain '{field}' field")
            
            # Ensure document ID matches DID
            if document.get('id') != did:
                document['id'] = did
            
            # Create DID document
            did_doc = DIDDocument.objects.create(
                did=did,
                document=document,
                controller=controller,
                expires_at=expires_at,
                metadata=metadata or {}
            )
            
            return did_doc

    @staticmethod
    def get_did_document(did: str) -> Optional[DIDDocument]:
        """
        Get a DID document by DID.
        
        Args:
            did: The DID identifier
            
        Returns:
            DIDDocument instance or None
        """
        try:
            return DIDDocument.objects.get(did=did)
        except DIDDocument.DoesNotExist:
            return None

    @staticmethod
    def update_did_document(
        did: str,
        document: Dict[str, Any],
        updated_by: str
    ) -> Optional[DIDDocument]:
        """
        Update a DID document.
        
        Args:
            did: The DID identifier
            document: Updated DID document
            updated_by: DID of the entity updating the document
            
        Returns:
            Updated DIDDocument instance or None
        """
        try:
            did_doc = DIDDocument.objects.get(did=did)
            
            # Validate document structure
            required_fields = ['@context', 'id', 'verificationMethod']
            for field in required_fields:
                if field not in document:
                    raise ValidationError(f"DID document must contain '{field}' field")
            
            # Ensure document ID matches DID
            if document.get('id') != did:
                document['id'] = did
            
            # Update document
            did_doc.document = document
            did_doc.updated_at = timezone.now()
            did_doc.save()
            
            return did_doc
        except DIDDocument.DoesNotExist:
            return None

    @staticmethod
    def revoke_did_document(did: str, revoked_by: str) -> bool:
        """
        Revoke a DID document.
        
        Args:
            did: The DID identifier
            revoked_by: DID of the entity revoking the document
            
        Returns:
            True if successful, False otherwise
        """
        try:
            did_doc = DIDDocument.objects.get(did=did)
            did_doc.status = 'revoked'
            did_doc.updated_at = timezone.now()
            did_doc.save()
            return True
        except DIDDocument.DoesNotExist:
            return False

    @staticmethod
    def verify_did_signature(
        did: str,
        message: str,
        signature: str,
        verification_method: Optional[str] = None
    ) -> bool:
        """
        Verify a signature using a DID's verification method.
        
        Args:
            did: The DID identifier
            message: The message that was signed
            signature: The signature to verify
            verification_method: Specific verification method to use
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            did_doc = DIDDocument.objects.get(did=did)
            
            if not did_doc.is_active():
                return False
            
            verification_methods = did_doc.get_verification_methods()
            
            if verification_method:
                # Use specific verification method
                vm = next((vm for vm in verification_methods if vm.get('id') == verification_method), None)
                if not vm:
                    return False
                verification_methods = [vm]
            
            # For now, we'll implement a basic verification
            # In a real implementation, you would use DIDKit or similar
            # to verify the signature against the public key
            
            # This is a placeholder implementation
            # In practice, you would:
            # 1. Extract the public key from the verification method
            # 2. Use cryptographic libraries to verify the signature
            # 3. Return the verification result
            
            return True  # Placeholder - always returns True for now
            
        except DIDDocument.DoesNotExist:
            return False

    @staticmethod
    def get_did_roles(did: str) -> List[DIDRole]:
        """
        Get all active roles for a DID.
        
        Args:
            did: The DID identifier
            
        Returns:
            List of active DIDRole instances
        """
        try:
            did_doc = DIDDocument.objects.get(did=did)
            return list(did_doc.roles.filter(is_active=True))
        except DIDDocument.DoesNotExist:
            return []

    @staticmethod
    def get_did_credentials(did: str) -> List[DIDCredential]:
        """
        Get all valid credentials for a DID.
        
        Args:
            did: The DID identifier
            
        Returns:
            List of valid DIDCredential instances
        """
        try:
            did_doc = DIDDocument.objects.get(did=did)
            return [cred for cred in did_doc.credentials.all() if cred.is_valid()]
        except DIDDocument.DoesNotExist:
            return []

    @staticmethod
    def check_did_permission(did: str, permission: str) -> bool:
        """
        Check if a DID has a specific permission.
        
        Args:
            did: The DID identifier
            permission: The permission to check
            
        Returns:
            True if DID has permission, False otherwise
        """
        roles = DIDService.get_did_roles(did)
        
        for role in roles:
            if role.is_valid() and role.has_permission(permission):
                return True
        
        return False

    @staticmethod
    def generate_did(prefix: str = "did:ethr") -> str:
        """
        Generate a new DID identifier.
        
        Args:
            prefix: The DID prefix (default: "did:ethr")
            
        Returns:
            Generated DID string
        """
        # Generate a unique identifier
        unique_id = str(uuid.uuid4()).replace('-', '')
        
        # Create a hash for additional uniqueness
        hash_obj = hashlib.sha256(unique_id.encode())
        hash_hex = hash_obj.hexdigest()[:16]  # Use first 16 characters
        
        return f"{prefix}:{hash_hex}"

    @staticmethod
    def create_verification_method(
        did: str,
        key_type: str = "EcdsaSecp256k1RecoveryMethod2020",
        public_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a verification method for a DID.
        
        Args:
            did: The DID identifier
            key_type: The type of verification method
            public_key: The public key (if not provided, will be generated)
            
        Returns:
            Verification method dictionary
        """
        if not public_key:
            # Generate a placeholder public key
            # In practice, you would generate a real cryptographic key
            public_key = f"0x{str(uuid.uuid4()).replace('-', '')[:40]}"
        
        verification_method_id = f"{did}#key-1"
        
        return {
            "id": verification_method_id,
            "type": key_type,
            "controller": did,
            "publicKeyMultibase": public_key
        }

    @staticmethod
    def create_did_document_template(
        did: str,
        controller: str,
        public_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a standard DID document template.
        
        Args:
            did: The DID identifier
            controller: The DID of the controller
            public_key: The public key for verification
            
        Returns:
            DID document dictionary
        """
        verification_method = DIDService.create_verification_method(did, public_key=public_key)
        
        return {
            "@context": [
                "https://www.w3.org/ns/did/v1",
                "https://w3id.org/security/suites/secp256k1recovery-2020/v2"
            ],
            "id": did,
            "controller": controller,
            "verificationMethod": [verification_method],
            "authentication": [verification_method["id"]],
            "assertionMethod": [verification_method["id"]],
            "capabilityInvocation": [verification_method["id"]],
            "capabilityDelegation": [verification_method["id"]]
        }
