from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock
import json

from .models import AuditEvent
from .services import AuditService, HashService, MerkleService
from .serializers import AuditEventSerializer

User = get_user_model()


class AuditEventModelTest(TestCase):
    """
    Test cases for AuditEvent model.
    """
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_audit_event_creation(self):
        """Test creating an audit event."""
        event = AuditEvent.objects.create(
            event_type='user_login',
            user=self.user,
            object_type='User',
            object_id=str(self.user.id),
            data={'ip_address': '192.168.1.1'},
            hash='test_hash_123'
        )
        
        self.assertEqual(event.event_type, 'user_login')
        self.assertEqual(event.user, self.user)
        self.assertEqual(event.object_type, 'User')
        self.assertEqual(event.object_id, str(self.user.id))
        self.assertEqual(event.status, 'pending')
        self.assertIsNotNone(event.created_at)
        
    def test_audit_event_str_representation(self):
        """Test string representation of audit event."""
        event = AuditEvent.objects.create(
            event_type='invoice_created',
            user=self.user,
            object_type='Invoice',
            object_id='123',
            data={'amount': 100.00},
            hash='test_hash_456'
        )
        
        expected_str = f"[{event.created_at.strftime('%Y-%m-%d %H:%M')}] invoice_created by {self.user.username}"
        self.assertEqual(str(event), expected_str)