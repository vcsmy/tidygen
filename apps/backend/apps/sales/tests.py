"""
Comprehensive tests for sales and client management functionality.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta

from apps.sales.models import (
    Client, IndividualClient, CorporateClient, ClientContact, ClientNote,
    ClientDocument, ClientTag, ClientTagAssignment, ClientInteraction,
    ClientSegment, ClientSegmentAssignment
)

User = get_user_model()


class ClientModelTests(TestCase):
    """Test client models."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.organization.members.create(
            user=self.user,
            role='admin'
        )
    
    def test_individual_client_creation(self):
        """Test individual client creation."""
        client = Client.objects.create(
            organization=self.organization,
            client_type='individual',
            email="john@example.com",
            phone="+1234567890",
            created_by=self.user
        )
        
        individual_client = IndividualClient.objects.create(
            client=client,
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1990, 1, 1),
            gender="male",
            job_title="Software Engineer"
        )
        
        self.assertEqual(client.client_type, 'individual')
        self.assertEqual(individual_client.first_name, "John")
        self.assertEqual(individual_client.last_name, "Doe")
        self.assertEqual(client.display_name, "John Doe")
    
    def test_corporate_client_creation(self):
        """Test corporate client creation."""
        client = Client.objects.create(
            organization=self.organization,
            client_type='corporate',
            email="info@acme.com",
            phone="+1234567890",
            created_by=self.user
        )
        
        corporate_client = CorporateClient.objects.create(
            client=client,
            company_name="Acme Corporation",
            legal_name="Acme Corp LLC",
            business_type="corporation",
            founded_year=2020,
            annual_revenue=Decimal('1000000.00')
        )
        
        self.assertEqual(client.client_type, 'corporate')
        self.assertEqual(corporate_client.company_name, "Acme Corporation")
        self.assertEqual(corporate_client.business_type, "corporation")
        self.assertEqual(client.display_name, "Acme Corporation")
    
    def test_client_contact_creation(self):
        """Test client contact creation."""
        client = Client.objects.create(
            organization=self.organization,
            client_type='individual',
            email="john@example.com",
            created_by=self.user
        )
        
        contact = ClientContact.objects.create(
            client=client,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            phone="+1234567891",
            job_title="Manager",
            is_primary=True
        )
        
        self.assertEqual(contact.client, client)
        self.assertEqual(contact.full_name, "Jane Smith")
        self.assertTrue(contact.is_primary)
    
    def test_client_note_creation(self):
        """Test client note creation."""
        client = Client.objects.create(
            organization=self.organization,
            client_type='individual',
            email="john@example.com",
            created_by=self.user
        )
        
        note = ClientNote.objects.create(
            client=client,
            note_type='meeting',
            title="Initial Meeting",
            content="Had a great initial meeting with the client.",
            related_user=self.user
        )
        
        self.assertEqual(note.client, client)
        self.assertEqual(note.note_type, 'meeting')
        self.assertEqual(note.title, "Initial Meeting")
    
    def test_client_interaction_creation(self):
        """Test client interaction creation."""
        client = Client.objects.create(
            organization=self.organization,
            client_type='individual',
            email="john@example.com",
            created_by=self.user
        )
        
        interaction = ClientInteraction.objects.create(
            client=client,
            interaction_type='phone_call',
            subject="Follow-up call",
            description="Called to follow up on proposal",
            initiated_by=self.user,
            duration_minutes=30
        )
        
        self.assertEqual(interaction.client, client)
        self.assertEqual(interaction.interaction_type, 'phone_call')
        self.assertEqual(interaction.duration_minutes, 30)
    
    def test_client_tag_creation(self):
        """Test client tag creation."""
        tag = ClientTag.objects.create(
            organization=self.organization,
            name="VIP Client",
            color="#ff0000",
            description="Very important client"
        )
        
        self.assertEqual(tag.name, "VIP Client")
        self.assertEqual(tag.color, "#ff0000")
    
    def test_client_segment_creation(self):
        """Test client segment creation."""
        segment = ClientSegment.objects.create(
            organization=self.organization,
            name="Enterprise Clients",
            description="Large enterprise clients",
            criteria={'annual_revenue__gte': 1000000}
        )
        
        self.assertEqual(segment.name, "Enterprise Clients")
        self.assertEqual(segment.criteria['annual_revenue__gte'], 1000000)


class ClientAPITests(APITestCase):
    """Test client API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.organization.members.create(
            user=self.user,
            role='admin'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_individual_client_create(self):
        """Test individual client creation via API."""
        url = reverse('client-list')
        data = {
            'client_type': 'individual',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'individual_client': {
                'first_name': 'John',
                'last_name': 'Doe',
                'date_of_birth': '1990-01-01',
                'gender': 'male',
                'job_title': 'Software Engineer'
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Client.objects.count(), 1)
        self.assertEqual(IndividualClient.objects.count(), 1)
    
    def test_corporate_client_create(self):
        """Test corporate client creation via API."""
        url = reverse('client-list')
        data = {
            'client_type': 'corporate',
            'email': 'info@acme.com',
            'phone': '+1234567890',
            'corporate_client': {
                'company_name': 'Acme Corporation',
                'legal_name': 'Acme Corp LLC',
                'business_type': 'corporation',
                'founded_year': 2020,
                'annual_revenue': '1000000.00'
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Client.objects.count(), 1)
        self.assertEqual(CorporateClient.objects.count(), 1)
    
    def test_client_list(self):
        """Test client list endpoint."""
        # Create test clients
        client1 = Client.objects.create(
            organization=self.organization,
            client_type='individual',
            email="john@example.com",
            created_by=self.user
        )
        IndividualClient.objects.create(
            client=client1,
            first_name="John",
            last_name="Doe"
        )
        
        client2 = Client.objects.create(
            organization=self.organization,
            client_type='corporate',
            email="info@acme.com",
            created_by=self.user
        )
        CorporateClient.objects.create(
            client=client2,
            company_name="Acme Corporation"
        )
        
        url = reverse('client-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_client_detail(self):
        """Test client detail endpoint."""
        client = Client.objects.create(
            organization=self.organization,
            client_type='individual',
            email="john@example.com",
            created_by=self.user
        )
        IndividualClient.objects.create(
            client=client,
            first_name="John",
            last_name="Doe"
        )
        
        url = reverse('client-detail', kwargs={'pk': client.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'john@example.com')
        self.assertEqual(response.data['display_name'], 'John Doe')
    
    def test_client_contact_add(self):
        """Test adding contact to client."""
        client = Client.objects.create(
            organization=self.organization,
            client_type='individual',
            email="john@example.com",
            created_by=self.user
        )
        
        url = reverse('client-add-contact', kwargs={'pk': client.pk})
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'phone': '+1234567891',
            'job_title': 'Manager',
            'is_primary': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ClientContact.objects.count(), 1)
    
    def test_client_note_add(self):
        """Test adding note to client."""
        client = Client.objects.create(
            organization=self.organization,
            client_type='individual',
            email="john@example.com",
            created_by=self.user
        )
        
        url = reverse('client-add-note', kwargs={'pk': client.pk})
        data = {
            'note_type': 'meeting',
            'title': 'Initial Meeting',
            'content': 'Had a great initial meeting with the client.'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ClientNote.objects.count(), 1)
    
    def test_client_interaction_add(self):
        """Test adding interaction to client."""
        client = Client.objects.create(
            organization=self.organization,
            client_type='individual',
            email="john@example.com",
            created_by=self.user
        )
        
        url = reverse('client-add-interaction', kwargs={'pk': client.pk})
        data = {
            'interaction_type': 'phone_call',
            'subject': 'Follow-up call',
            'description': 'Called to follow up on proposal',
            'duration_minutes': 30
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ClientInteraction.objects.count(), 1)
    
    def test_client_tag_assign(self):
        """Test assigning tag to client."""
        client = Client.objects.create(
            organization=self.organization,
            client_type='individual',
            email="john@example.com",
            created_by=self.user
        )
        
        tag = ClientTag.objects.create(
            organization=self.organization,
            name="VIP Client",
            color="#ff0000"
        )
        
        url = reverse('client-assign-tag', kwargs={'pk': client.pk})
        data = {'tag_id': tag.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ClientTagAssignment.objects.count(), 1)
    
    def test_client_status_change(self):
        """Test changing client status."""
        client = Client.objects.create(
            organization=self.organization,
            client_type='individual',
            email="john@example.com",
            status='prospect',
            created_by=self.user
        )
        
        url = reverse('client-change-status', kwargs={'pk': client.pk})
        data = {'status': 'active'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        client.refresh_from_db()
        self.assertEqual(client.status, 'active')
        self.assertEqual(ClientNote.objects.count(), 1)  # Status change note
    
    def test_client_priority_change(self):
        """Test changing client priority."""
        client = Client.objects.create(
            organization=self.organization,
            client_type='individual',
            email="john@example.com",
            priority='medium',
            created_by=self.user
        )
        
        url = reverse('client-change-priority', kwargs={'pk': client.pk})
        data = {'priority': 'high'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        client.refresh_from_db()
        self.assertEqual(client.priority, 'high')
        self.assertEqual(ClientNote.objects.count(), 1)  # Priority change note
    
    def test_client_analytics(self):
        """Test client analytics endpoint."""
        # Create test clients
        client1 = Client.objects.create(
            organization=self.organization,
            client_type='individual',
            email="john@example.com",
            status='active',
            created_by=self.user
        )
        client2 = Client.objects.create(
            organization=self.organization,
            client_type='corporate',
            email="info@acme.com",
            status='prospect',
            created_by=self.user
        )
        
        url = reverse('client-analytics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_clients', response.data)
        self.assertIn('active_clients', response.data)
        self.assertIn('client_distribution', response.data)
    
    def test_client_dashboard(self):
        """Test client dashboard endpoint."""
        # Create test clients
        client1 = Client.objects.create(
            organization=self.organization,
            client_type='individual',
            email="john@example.com",
            status='active',
            created_by=self.user
        )
        client2 = Client.objects.create(
            organization=self.organization,
            client_type='corporate',
            email="info@acme.com",
            status='prospect',
            created_by=self.user
        )
        
        url = reverse('client-dashboard-overview')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_clients', response.data)
        self.assertIn('clients_by_type', response.data)
        self.assertIn('recent_clients', response.data)


class ClientSignalTests(TestCase):
    """Test client signals."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.organization.members.create(
            user=self.user,
            role='admin'
        )
    
    def test_client_activity_update_on_interaction(self):
        """Test client activity date update on interaction."""
        client = Client.objects.create(
            organization=self.organization,
            client_type='individual',
            email="john@example.com",
            created_by=self.user
        )
        
        # Create interaction
        interaction = ClientInteraction.objects.create(
            client=client,
            interaction_type='phone_call',
            subject='Test call',
            initiated_by=self.user
        )
        
        # Check that client's last_contact_date was updated
        client.refresh_from_db()
        self.assertIsNotNone(client.last_contact_date)
        self.assertIsNotNone(client.last_activity_date)
    
    def test_client_activity_update_on_note(self):
        """Test client activity date update on note."""
        client = Client.objects.create(
            organization=self.organization,
            client_type='individual',
            email="john@example.com",
            created_by=self.user
        )
        
        # Create note
        note = ClientNote.objects.create(
            client=client,
            note_type='general',
            title='Test note',
            content='Test content',
            related_user=self.user
        )
        
        # Check that client's last_activity_date was updated
        client.refresh_from_db()
        self.assertIsNotNone(client.last_activity_date)
    
    def test_primary_contact_ensured(self):
        """Test that only one primary contact is allowed."""
        client = Client.objects.create(
            organization=self.organization,
            client_type='individual',
            email="john@example.com",
            created_by=self.user
        )
        
        # Create first primary contact
        contact1 = ClientContact.objects.create(
            client=client,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            is_primary=True
        )
        
        # Create second primary contact
        contact2 = ClientContact.objects.create(
            client=client,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            is_primary=True
        )
        
        # Check that only the second contact is primary
        contact1.refresh_from_db()
        contact2.refresh_from_db()
        self.assertFalse(contact1.is_primary)
        self.assertTrue(contact2.is_primary)
    
    def test_default_tags_assigned(self):
        """Test that default tags are assigned to new clients."""
        client = Client.objects.create(
            organization=self.organization,
            client_type='individual',
            email="john@example.com",
            status='prospect',
            created_by=self.user
        )
        
        # Check that default tags were created and assigned
        self.assertTrue(ClientTag.objects.filter(name='Individual Client').exists())
        self.assertTrue(ClientTag.objects.filter(name='Prospect Status').exists())
        self.assertEqual(ClientTagAssignment.objects.count(), 2)
    
    def test_welcome_interaction_created(self):
        """Test that welcome interaction is created for new clients."""
        client = Client.objects.create(
            organization=self.organization,
            client_type='individual',
            email="john@example.com",
            created_by=self.user
        )
        
        # Check that welcome interaction was created
        self.assertTrue(ClientInteraction.objects.filter(
            client=client,
            subject='Welcome to our services'
        ).exists())


class ClientFilterTests(TestCase):
    """Test client filters."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.organization.members.create(
            user=self.user,
            role='admin'
        )
    
    def test_client_type_filter(self):
        """Test client type filtering."""
        client1 = Client.objects.create(
            organization=self.organization,
            client_type='individual',
            email="john@example.com",
            created_by=self.user
        )
        client2 = Client.objects.create(
            organization=self.organization,
            client_type='corporate',
            email="info@acme.com",
            created_by=self.user
        )
        
        from apps.sales.filters import ClientFilter
        
        # Test individual filter
        filter_data = {'client_type': 'individual'}
        filtered_clients = ClientFilter(filter_data, queryset=Client.objects.all()).qs
        self.assertEqual(filtered_clients.count(), 1)
        self.assertEqual(filtered_clients.first(), client1)
        
        # Test corporate filter
        filter_data = {'client_type': 'corporate'}
        filtered_clients = ClientFilter(filter_data, queryset=Client.objects.all()).qs
        self.assertEqual(filtered_clients.count(), 1)
        self.assertEqual(filtered_clients.first(), client2)
    
    def test_client_status_filter(self):
        """Test client status filtering."""
        client1 = Client.objects.create(
            organization=self.organization,
            client_type='individual',
            email="john@example.com",
            status='active',
            created_by=self.user
        )
        client2 = Client.objects.create(
            organization=self.organization,
            client_type='individual',
            email="jane@example.com",
            status='prospect',
            created_by=self.user
        )
        
        from apps.sales.filters import ClientFilter
        
        # Test active filter
        filter_data = {'status': 'active'}
        filtered_clients = ClientFilter(filter_data, queryset=Client.objects.all()).qs
        self.assertEqual(filtered_clients.count(), 1)
        self.assertEqual(filtered_clients.first(), client1)
        
        # Test prospect filter
        filter_data = {'status': 'prospect'}
        filtered_clients = ClientFilter(filter_data, queryset=Client.objects.all()).qs
        self.assertEqual(filtered_clients.count(), 1)
        self.assertEqual(filtered_clients.first(), client2)
    
    def test_client_city_filter(self):
        """Test client city filtering."""
        client1 = Client.objects.create(
            organization=self.organization,
            client_type='individual',
            email="john@example.com",
            city="New York",
            created_by=self.user
        )
        client2 = Client.objects.create(
            organization=self.organization,
            client_type='individual',
            email="jane@example.com",
            city="Los Angeles",
            created_by=self.user
        )
        
        from apps.sales.filters import ClientFilter
        
        # Test city filter
        filter_data = {'city': 'New York'}
        filtered_clients = ClientFilter(filter_data, queryset=Client.objects.all()).qs
        self.assertEqual(filtered_clients.count(), 1)
        self.assertEqual(filtered_clients.first(), client1)
    
    def test_client_has_interactions_filter(self):
        """Test client has interactions filter."""
        client1 = Client.objects.create(
            organization=self.organization,
            client_type='individual',
            email="john@example.com",
            created_by=self.user
        )
        client2 = Client.objects.create(
            organization=self.organization,
            client_type='individual',
            email="jane@example.com",
            created_by=self.user
        )
        
        # Add interaction to client1
        ClientInteraction.objects.create(
            client=client1,
            interaction_type='phone_call',
            subject='Test call',
            initiated_by=self.user
        )
        
        from apps.sales.filters import ClientFilter
        
        # Test has interactions filter
        filter_data = {'has_interactions': True}
        filtered_clients = ClientFilter(filter_data, queryset=Client.objects.all()).qs
        self.assertEqual(filtered_clients.count(), 1)
        self.assertEqual(filtered_clients.first(), client1)
        
        # Test no interactions filter
        filter_data = {'has_interactions': False}
        filtered_clients = ClientFilter(filter_data, queryset=Client.objects.all()).qs
        self.assertEqual(filtered_clients.count(), 1)
        self.assertEqual(filtered_clients.first(), client2)
