"""
Tests for freelancers app.
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db import IntegrityError
from rest_framework import status
from rest_framework.test import APIClient
from decimal import Decimal
from unittest.mock import patch

from .models import Freelancer, FreelancerDocument, FreelancerAvailability, FreelancerSkill, FreelancerSkillAssignment, FreelancerReview

User = get_user_model()


class FreelancerModelTests(TestCase):
    """Test cases for Freelancer model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testfreelancer',
            email='freelancer@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Freelancer'
        )
    
    @patch('apps.freelancers.models.uuid.uuid4')
    def test_freelancer_id_generation(self, mock_uuid):
        """Test that freelancer ID is generated automatically."""
        mock_uuid.return_value.hex = '12345678abcdef'
        
        freelancer = Freelancer.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            date_of_birth='1990-01-01',
            personal_email='john@example.com',
            personal_phone='+1234567890',
            address_line1='123 Main St',
            city='New York',
            state='NY',
            postal_code='10001',
            country='US',
            hourly_rate=25.00
        )
        
        self.assertTrue(freelancer.freelancer_id.startswith('FL'))
        self.assertEqual(len(freelancer.freelancer_id), 10)  # FL + 8 chars
    
    def test_freelancer_full_name_property(self):
        """Test the full_name property."""
        freelancer = Freelancer.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            date_of_birth='1990-01-01',
            personal_email='john@example.com',
            personal_phone='+1234567890',
            address_line1='123 Main St',
            city='New York',
            state='NY',
            postal_code='10001',
            country='US',
            hourly_rate=25.00
        )
        
        self.assertEqual(freelancer.full_name, 'John Doe')
    
    def test_freelancer_full_address_property(self):
        """Test the full_address property."""
        freelancer = Freelancer.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            date_of_birth='1990-01-01',
            personal_email='john@example.com',
            personal_phone='+1234567890',
            address_line1='123 Main St',
            address_line2='Apt 4B',
            city='New York',
            state='NY',
            postal_code='10001',
            country='US',
            hourly_rate=25.00
        )
        
        expected = '123 Main St, Apt 4B, New York, NY, 10001, US'
        self.assertEqual(freelancer.full_address, expected)
    
    def test_freelancer_is_eligible_for_jobs(self):
        """Test the is_eligible_for_jobs property."""
        freelancer = Freelancer.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            date_of_birth='1990-01-01',
            personal_email='john@example.com',
            personal_phone='+1234567890',
            address_line1='123 Main St',
            city='New York',
            state='NY',
            postal_code='10001',
            country='US',
            hourly_rate=25.00,
            status='active',
            is_available=True,
            background_check_completed=False
        )
        
        # Should not be eligible without background check
        self.assertFalse(freelancer.is_eligible_for_jobs)
        
        # Should be eligible after background check
        freelancer.background_check_completed = True
        freelancer.save()
        self.assertTrue(freelancer.is_eligible_for_jobs)
        
        # Should not be eligible if inactive
        freelancer.status = 'inactive'
        freelancer.save()
        self.assertFalse(freelancer.is_eligible_for_jobs)


class FreelancerAPITests(TestCase):
    """Test cases for Freelancer API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.freelancer_user = User.objects.create_user(
            username='freelancer',
            email='freelancer@test.com',
            password='testpass123',
            first_name='John',
            last_name='Freelancer'
        )
        self.freelancer = Freelancer.objects.create(
            user=self.freelancer_user,
            first_name='John',
            last_name='Freelancer',
            date_of_birth='1990-01-01',
            personal_email='john@example.com',
            personal_phone='+1234567890',
            address_line1='123 Main St',
            city='New York',
            state='NY',
            postal_code='10001',
            country='US',
            hourly_rate=25.00
        )
    
    def authenticate_user(self, user=None):
        """Helper to authenticate user."""
        from rest_framework_simplejwt.tokens import RefreshToken
        if user is None:
            user = self.user
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_freelancer_list_unauthenticated(self):
        """Test that unauthenticated users cannot access freelancer list."""
        response = self.client.get('/api/v1/freelancers/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_freelancer_list_authenticated(self):
        """Test that authenticated users can access freelancer list."""
        self.authenticate_user()
        response = self.client.get('/api/v1/freelancers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_freelancer_detail(self):
        """Test freelancer detail endpoint."""
        self.authenticate_user()
        response = self.client.get(f'/api/v1/freelancers/{self.freelancer.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['freelancer_id'], self.freelancer.freelancer_id)
    
    def test_freelancer_create(self):
        """Test freelancer creation."""
        self.authenticate_user(self.freelancer_user)
        
        data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'date_of_birth': '1985-05-15',
            'personal_email': 'jane@example.com',
            'personal_phone': '+1987654321',
            'address_line1': '456 Oak Ave',
            'city': 'Los Angeles',
            'state': 'CA',
            'postal_code': '90210',
            'country': 'US',
            'hourly_rate': 30.00,
            'currency': 'USD'
        }
        
        response = self.client.post('/api/v1/freelancers/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Freelancer.objects.filter(user=self.freelancer_user).exists())
    
    def test_freelancer_update_own_profile(self):
        """Test that freelancers can update their own profiles."""
        self.authenticate_user(self.freelancer_user)
        
        data = {
            'first_name': 'John Updated',
            'hourly_rate': 30.00
        }
        
        response = self.client.patch(f'/api/v1/freelancers/{self.freelancer.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.freelancer.refresh_from_db()
        self.assertEqual(self.freelancer.first_name, 'John Updated')
        self.assertEqual(self.freelancer.hourly_rate, Decimal('30.00'))
    
    def test_freelancer_search(self):
        """Test freelancer search functionality."""
        self.authenticate_user()
        
        response = self.client.get('/api/v1/freelancers/search/?q=John')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
    
    def test_freelancer_stats(self):
        """Test freelancer statistics endpoint."""
        self.authenticate_user()
        
        response = self.client.get(f'/api/v1/freelancers/{self.freelancer.id}/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_reviews', response.data)
        self.assertIn('average_ratings', response.data)


class FreelancerDocumentTests(TestCase):
    """Test cases for FreelancerDocument model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123'
        )
        self.freelancer = Freelancer.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            date_of_birth='1990-01-01',
            personal_email='john@example.com',
            personal_phone='+1234567890',
            address_line1='123 Main St',
            city='New York',
            state='NY',
            postal_code='10001',
            country='US',
            hourly_rate=25.00
        )
    
    def test_document_creation(self):
        """Test creating a freelancer document."""
        document = FreelancerDocument.objects.create(
            freelancer=self.freelancer,
            document_type='id_copy',
            title='Driver License',
            description='Valid driver license copy'
        )
        
        self.assertEqual(document.freelancer, self.freelancer)
        self.assertEqual(document.document_type, 'id_copy')
        self.assertFalse(document.is_verified)


class FreelancerAvailabilityTests(TestCase):
    """Test cases for FreelancerAvailability model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123'
        )
        self.freelancer = Freelancer.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            date_of_birth='1990-01-01',
            personal_email='john@example.com',
            personal_phone='+1234567890',
            address_line1='123 Main St',
            city='New York',
            state='NY',
            postal_code='10001',
            country='US',
            hourly_rate=25.00
        )
    
    def test_availability_creation(self):
        """Test creating freelancer availability."""
        from datetime import time
        
        availability = FreelancerAvailability.objects.create(
            freelancer=self.freelancer,
            day_of_week=0,  # Monday
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_available=True
        )
        
        self.assertEqual(availability.freelancer, self.freelancer)
        self.assertEqual(availability.day_of_week, 0)
        self.assertTrue(availability.is_available)


class FreelancerSkillTests(TestCase):
    """Test cases for FreelancerSkill and FreelancerSkillAssignment models."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123'
        )
        self.freelancer = Freelancer.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            date_of_birth='1990-01-01',
            personal_email='john@example.com',
            personal_phone='+1234567890',
            address_line1='123 Main St',
            city='New York',
            state='NY',
            postal_code='10001',
            country='US',
            hourly_rate=25.00
        )
    
    def test_skill_creation(self):
        """Test creating a freelancer skill."""
        skill = FreelancerSkill.objects.create(
            name='Deep Cleaning',
            category='cleaning',
            description='Advanced cleaning techniques',
            is_certification_required=False
        )
        
        self.assertEqual(skill.name, 'Deep Cleaning')
        self.assertEqual(skill.category, 'cleaning')
    
    def test_skill_assignment(self):
        """Test assigning a skill to a freelancer."""
        skill = FreelancerSkill.objects.create(
            name='Window Cleaning',
            category='cleaning'
        )
        
        assignment = FreelancerSkillAssignment.objects.create(
            freelancer=self.freelancer,
            skill=skill,
            proficiency_level='advanced',
            years_of_experience=3
        )
        
        self.assertEqual(assignment.freelancer, self.freelancer)
        self.assertEqual(assignment.skill, skill)
        self.assertEqual(assignment.proficiency_level, 'advanced')


class FreelancerReviewTests(TestCase):
    """Test cases for FreelancerReview model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123'
        )
        self.reviewer = User.objects.create_user(
            username='reviewer',
            email='reviewer@test.com',
            password='testpass123'
        )
        self.freelancer = Freelancer.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            date_of_birth='1990-01-01',
            personal_email='john@example.com',
            personal_phone='+1234567890',
            address_line1='123 Main St',
            city='New York',
            state='NY',
            postal_code='10001',
            country='US',
            hourly_rate=25.00
        )
    
    def test_review_creation(self):
        """Test creating a freelancer review."""
        review = FreelancerReview.objects.create(
            freelancer=self.freelancer,
            reviewer=self.reviewer,
            overall_rating=5,
            quality_rating=5,
            punctuality_rating=4,
            communication_rating=5,
            professionalism_rating=5,
            title='Excellent work!',
            comment='Did a great job cleaning our house.',
            would_recommend=True
        )
        
        self.assertEqual(review.freelancer, self.freelancer)
        self.assertEqual(review.reviewer, self.reviewer)
        self.assertEqual(review.overall_rating, 5)
        self.assertEqual(review.average_rating, 4.8)  # (5+5+4+5+5)/5


@pytest.mark.django_db
class FreelancerIntegrationTests:
    """Integration tests for freelancer workflows."""
    
    def test_complete_freelancer_registration_flow(self, freelancer_user, sample_freelancer_data):
        """Test the complete freelancer registration flow."""
        client = APIClient()
        
        # Authenticate user
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(freelancer_user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Create freelancer profile
        response = client.post('/api/v1/freelancers/', sample_freelancer_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify freelancer was created
        from apps.freelancers.models import Freelancer
        freelancer = Freelancer.objects.get(user=freelancer_user)
        assert freelancer.full_name == f"{sample_freelancer_data['first_name']} {sample_freelancer_data['last_name']}"
    
    def test_freelancer_skill_assignment_flow(self, freelancer_profile):
        """Test assigning skills to a freelancer."""
        from apps.freelancers.models import FreelancerSkill, FreelancerSkillAssignment
        
        # Create a skill
        skill = FreelancerSkill.objects.create(
            name='Eco-Friendly Cleaning',
            category='cleaning',
            description='Environmentally friendly cleaning methods'
        )
        
        # Assign skill to freelancer
        assignment = FreelancerSkillAssignment.objects.create(
            freelancer=freelancer_profile,
            skill=skill,
            proficiency_level='intermediate',
            years_of_experience=2
        )
        
        assert assignment.freelancer == freelancer_profile
        assert assignment.skill == skill
        assert skill.freelancer_assignments.filter(freelancer=freelancer_profile).exists()
