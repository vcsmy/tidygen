"""
Tests for DID Authentication System
"""

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock

from .models import DIDDocument, DIDRole, DIDCredential, DIDSession, DIDPermission
from .services import DIDService, DIDAuthService, DIDRoleService, DIDCredentialService


class DIDDocumentModelTest(TestCase):
    """
    Test cases for DIDDocument model.
    """

    def setUp(self):
        """Set up test data."""
        self.sample_did = "did:ethr:0x1234567890abcdef"
        self.sample_document = {
            "@context": ["https://www.w3.org/ns/did/v1"],
            "id": self.sample_did,
            "verificationMethod": [{
                "id": f"{self.sample_did}#key-1",
                "type": "EcdsaSecp256k1RecoveryMethod2020",
                "controller": self.sample_did,
                "publicKeyMultibase": "0x1234567890abcdef"
            }]
        }

    def test_did_document_creation(self):
        """Test creating a DID document."""
        did_doc = DIDDocument.objects.create(
            did=self.sample_did,
            document=self.sample_document,
            controller=self.sample_did
        )

        self.assertEqual(did_doc.did, self.sample_did)
        self.assertEqual(did_doc.controller, self.sample_did)
        self.assertEqual(did_doc.status, 'active')
        self.assertIsNotNone(did_doc.created_at)

    def test_did_document_str_representation(self):
        """Test string representation of DID document."""
        did_doc = DIDDocument.objects.create(
            did=self.sample_did,
            document=self.sample_document,
            controller=self.sample_did
        )

        expected_str = f"{self.sample_did} (active)"
        self.assertEqual(str(did_doc), expected_str)

    def test_did_document_is_active(self):
        """Test DID document active status."""
        did_doc = DIDDocument.objects.create(
            did=self.sample_did,
            document=self.sample_document,
            controller=self.sample_did
        )

        self.assertTrue(did_doc.is_active())
        
        # Test expired DID
        did_doc.expires_at = timezone.now() - timezone.timedelta(days=1)
        did_doc.save()
        self.assertFalse(did_doc.is_active())