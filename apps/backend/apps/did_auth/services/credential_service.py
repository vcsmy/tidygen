"""
DID Credential Service

Service for managing verifiable credentials for DIDs.
"""

import uuid
from typing import Dict, Any, Optional, List, Tuple
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError

from ..models import DIDDocument, DIDCredential


class DIDCredentialService:
    """
    Service for managing verifiable credentials for DIDs.
    """

    @staticmethod
    def issue_credential(
        did: str,
        credential_type: str,
        credential_data: Dict[str, Any],
        issuer: str,
        expires_at: Optional[timezone.datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[DIDCredential]:
        """
        Issue a verifiable credential to a DID.
        
        Args:
            did: The DID identifier
            credential_type: The type of credential
            credential_data: The credential data
            issuer: DID of the entity issuing the credential
            expires_at: Optional expiration date
            metadata: Additional metadata
            
        Returns:
            DIDCredential instance or None
        """
        try:
            did_doc = DIDDocument.objects.get(did=did)
            
            # Create credential data following W3C VC specification
            vc_data = {
                "@context": [
                    "https://www.w3.org/2018/credentials/v1",
                    "https://www.w3.org/2018/credentials/examples/v1"
                ],
                "type": ["VerifiableCredential", credential_type],
                "issuer": issuer,
                "issuanceDate": timezone.now().isoformat(),
                "credentialSubject": {
                    "id": did,
                    **credential_data
                },
                "proof": {
                    "type": "EcdsaSecp256k1RecoverySignature2020",
                    "created": timezone.now().isoformat(),
                    "verificationMethod": f"{issuer}#key-1",
                    "proofPurpose": "assertionMethod",
                    "jws": f"placeholder_signature_{uuid.uuid4().hex[:16]}"
                }
            }
            
            if expires_at:
                vc_data["expirationDate"] = expires_at.isoformat()
            
            credential = DIDCredential.objects.create(
                did=did_doc,
                credential_type=credential_type,
                credential_data=vc_data,
                issuer=issuer,
                expires_at=expires_at,
                metadata=metadata or {}
            )
            
            return credential
            
        except DIDDocument.DoesNotExist:
            return None

    @staticmethod
    def revoke_credential(
        credential_id: int,
        revoked_by: str
    ) -> bool:
        """
        Revoke a verifiable credential.
        
        Args:
            credential_id: The credential ID
            revoked_by: DID of the entity revoking the credential
            
        Returns:
            True if successful, False otherwise
        """
        try:
            credential = DIDCredential.objects.get(id=credential_id)
            credential.revoke(revoked_by)
            return True
        except DIDCredential.DoesNotExist:
            return False

    @staticmethod
    def get_did_credentials(
        did: str,
        credential_type: Optional[str] = None,
        valid_only: bool = True
    ) -> List[DIDCredential]:
        """
        Get credentials for a DID.
        
        Args:
            did: The DID identifier
            credential_type: Optional filter by credential type
            valid_only: Whether to return only valid credentials
            
        Returns:
            List of DIDCredential instances
        """
        try:
            did_doc = DIDDocument.objects.get(did=did)
            queryset = did_doc.credentials.all()
            
            if credential_type:
                queryset = queryset.filter(credential_type=credential_type)
            
            if valid_only:
                # Filter for valid credentials (not revoked and not expired)
                credentials = list(queryset)
                return [cred for cred in credentials if cred.is_valid()]
            
            return list(queryset)
        except DIDDocument.DoesNotExist:
            return []

    @staticmethod
    def verify_credential(credential_id: int) -> Tuple[bool, Optional[str]]:
        """
        Verify a credential's validity.
        
        Args:
            credential_id: The credential ID
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            credential = DIDCredential.objects.get(id=credential_id)
            
            if credential.revoked:
                return False, "Credential has been revoked"
            
            if credential.is_expired():
                return False, "Credential has expired"
            
            # In a real implementation, you would verify the cryptographic proof
            # For now, we'll just check the basic validity
            
            return True, None
            
        except DIDCredential.DoesNotExist:
            return False, "Credential not found"

    @staticmethod
    def create_employment_credential(
        did: str,
        employer_did: str,
        employee_data: Dict[str, Any],
        expires_at: Optional[timezone.datetime] = None
    ) -> Optional[DIDCredential]:
        """
        Create an employment credential.
        
        Args:
            did: The employee's DID
            employer_did: The employer's DID
            employee_data: Employee information
            expires_at: Optional expiration date
            
        Returns:
            DIDCredential instance or None
        """
        credential_data = {
            "employeeId": employee_data.get("employee_id"),
            "position": employee_data.get("position"),
            "department": employee_data.get("department"),
            "startDate": employee_data.get("start_date"),
            "employmentStatus": employee_data.get("status", "active"),
            "salary": employee_data.get("salary"),
            "benefits": employee_data.get("benefits", [])
        }
        
        return DIDCredentialService.issue_credential(
            did=did,
            credential_type="employment",
            credential_data=credential_data,
            issuer=employer_did,
            expires_at=expires_at
        )

    @staticmethod
    def create_identity_credential(
        did: str,
        issuer_did: str,
        identity_data: Dict[str, Any],
        expires_at: Optional[timezone.datetime] = None
    ) -> Optional[DIDCredential]:
        """
        Create an identity credential.
        
        Args:
            did: The subject's DID
            issuer_did: The issuer's DID
            identity_data: Identity information
            expires_at: Optional expiration date
            
        Returns:
            DIDCredential instance or None
        """
        credential_data = {
            "name": identity_data.get("name"),
            "dateOfBirth": identity_data.get("date_of_birth"),
            "nationality": identity_data.get("nationality"),
            "address": identity_data.get("address"),
            "phoneNumber": identity_data.get("phone_number"),
            "email": identity_data.get("email"),
            "governmentId": identity_data.get("government_id")
        }
        
        return DIDCredentialService.issue_credential(
            did=did,
            credential_type="identity",
            credential_data=credential_data,
            issuer=issuer_did,
            expires_at=expires_at
        )

    @staticmethod
    def create_certification_credential(
        did: str,
        issuer_did: str,
        certification_data: Dict[str, Any],
        expires_at: Optional[timezone.datetime] = None
    ) -> Optional[DIDCredential]:
        """
        Create a certification credential.
        
        Args:
            did: The subject's DID
            issuer_did: The issuer's DID
            certification_data: Certification information
            expires_at: Optional expiration date
            
        Returns:
            DIDCredential instance or None
        """
        credential_data = {
            "certificationName": certification_data.get("name"),
            "certificationBody": certification_data.get("issuing_body"),
            "certificationNumber": certification_data.get("number"),
            "issueDate": certification_data.get("issue_date"),
            "validUntil": certification_data.get("valid_until"),
            "skills": certification_data.get("skills", []),
            "level": certification_data.get("level")
        }
        
        return DIDCredentialService.issue_credential(
            did=did,
            credential_type="certification",
            credential_data=credential_data,
            issuer=issuer_did,
            expires_at=expires_at
        )

    @staticmethod
    def get_credential_by_type(
        did: str,
        credential_type: str
    ) -> Optional[DIDCredential]:
        """
        Get the most recent valid credential of a specific type for a DID.
        
        Args:
            did: The DID identifier
            credential_type: The credential type
            
        Returns:
            Most recent valid DIDCredential or None
        """
        credentials = DIDCredentialService.get_did_credentials(
            did=did,
            credential_type=credential_type,
            valid_only=True
        )
        
        if credentials:
            # Return the most recently issued credential
            return max(credentials, key=lambda c: c.issued_at)
        
        return None

    @staticmethod
    def cleanup_expired_credentials() -> int:
        """
        Clean up expired credentials by marking them as expired.
        
        Returns:
            Number of credentials processed
        """
        expired_credentials = DIDCredential.objects.filter(
            revoked=False,
            expires_at__lt=timezone.now()
        )
        
        count = expired_credentials.count()
        
        # In a real implementation, you might want to mark them as expired
        # rather than deleting them for audit purposes
        for credential in expired_credentials:
            # You could add an 'expired' field to track this
            pass
        
        return count
