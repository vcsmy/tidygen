"""
Tests for gig_management app.
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db import IntegrityError
from rest_framework import status
from rest_framework.test import APIClient
from decimal import Decimal
from datetime import datetime, time
from unittest.mock import patch

from .models import GigCategory, GigJob, GigApplication, JobMilestone, JobPhoto, JobMessage, JobReview

User = get_user_model()


class GigCategoryModelTests(TestCase):
    """Test cases for GigCategory model."""
    
    def test_category_creation(self):
        """Test creating a gig category."""
        category = GigCategory.objects.create(
            name='Residential Cleaning',
            description='Home cleaning services',
            icon='home',
            color='#FF5733',
            default_hourly_rate_min=20.00,
            default_hourly_rate_max=50.00
        )
        
        self.assertEqual(category.name, 'Residential Cleaning')
        self.assertTrue(category.is_active)
        self.assertEqual(category.default_hourly_rate_min, Decimal('20.00'))
    
    def test_category_job_count_property(self):
        """Test the job_count property."""
        category = GigCategory.objects.create(
            name='Test Category',
            description='Test description'
        )
        
        # Initially no jobs
        self.assertEqual(category.jobs.count(), 0)
        
        # Create a user and job
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        job = GigJob.objects.create(
            title='Test Job',
            description='Test description',
            category=category,
            client=user,
            client_type='individual',
            service_address='123 Test St',
            city='Test City',
            state='TS',
            postal_code='12345',
            country='US',
            status='published'
        )
        
        self.assertEqual(category.jobs.count(), 1)


class GigJobModelTests(TestCase):
    """Test cases for GigJob model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.category = GigCategory.objects.create(
            name='Test Category',
            description='Test category description'
        )
    
    @patch('apps.gig_management.models.uuid.uuid4')
    def test_job_id_generation(self, mock_uuid):
        """Test that job ID is generated automatically."""
        mock_uuid.return_value.hex = '12345678abcdef'
        
        job = GigJob.objects.create(
            title='Test Job',
            description='Test job description',
            category=self.category,
            client=self.user,
            client_type='individual',
            service_address='123 Test St',
            city='Test City',
            state='TS',
            postal_code='12345',
            country='US'
        )
        
        self.assertTrue(job.job_id.startswith('GIG'))
        self.assertEqual(len(job.job_id), 11)  # GIG + 8 chars
    
    def test_job_full_address_property(self):
        """Test the full_address property."""
        job = GigJob.objects.create(
            title='Test Job',
            description='Test job description',
            category=self.category,
            client=self.user,
            client_type='individual',
            service_address='123 Main St',
            city='New York',
            state='NY',
            postal_code='10001',
            country='US'
        )
        
        expected = '123 Main St, New York, NY, 10001, US'
        self.assertEqual(job.full_address, expected)
    
    def test_job_total_cost_calculation(self):
        """Test the total_cost property calculation."""
        # Test hourly rate calculation
        job_hourly = GigJob.objects.create(
            title='Hourly Job',
            description='Test hourly job',
            category=self.category,
            client=self.user,
            client_type='individual',
            service_address='123 Test St',
            city='Test City',
            state='TS',
            postal_code='12345',
            country='US',
            payment_method='hourly',
            hourly_rate=25.00,
            estimated_duration_hours=4.0
        )
        
        self.assertEqual(job_hourly.total_cost, Decimal('100.00'))
        
        # Test fixed price calculation
        job_fixed = GigJob.objects.create(
            title='Fixed Price Job',
            description='Test fixed price job',
            category=self.category,
            client=self.user,
            client_type='individual',
            service_address='123 Test St',
            city='Test City',
            state='TS',
            postal_code='12345',
            country='US',
            payment_method='fixed',
            fixed_price=150.00
        )
        
        self.assertEqual(job_fixed.total_cost, Decimal('150.00'))


class GigJobAPITests(TestCase):
    """Test cases for GigJob API endpoints."""
    
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
        self.category = GigCategory.objects.create(
            name='Residential Cleaning',
            description='Home cleaning services'
        )
        self.job = GigJob.objects.create(
            title='House Cleaning',
            description='Regular house cleaning service',
            category=self.category,
            client=self.user,
            client_type='individual',
            service_address='123 Main St',
            city='New York',
            state='NY',
            postal_code='10001',
            country='US',
            status='published'
        )
    
    def authenticate_user(self, user=None):
        """Helper to authenticate user."""
        from rest_framework_simplejwt.tokens import RefreshToken
        if user is None:
            user = self.user
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_job_list_unauthenticated(self):
        """Test that unauthenticated users cannot access job list."""
        response = self.client.get('/api/v1/gig-management/jobs/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_job_list_authenticated(self):
        """Test that authenticated users can access job list."""
        self.authenticate_user()
        response = self.client.get('/api/v1/gig-management/jobs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_job_detail(self):
        """Test job detail endpoint."""
        self.authenticate_user()
        response = self.client.get(f'/api/v1/gig-management/jobs/{self.job.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.job.title)
    
    def test_job_create(self):
        """Test job creation."""
        self.authenticate_user()
        
        data = {
            'title': 'Office Cleaning',
            'description': 'Office cleaning service',
            'category': self.category.id,
            'client_type': 'corporate',
            'service_address': '456 Business Ave',
            'city': 'San Francisco',
            'state': 'CA',
            'postal_code': '94105',
            'country': 'US',
            'service_type': 'commercial_cleaning',
            'property_type': 'office',
            'payment_method': 'hourly',
            'hourly_rate': 40.00,
            'estimated_duration_hours': 6.0
        }
        
        response = self.client.post('/api/v1/gig-management/jobs/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(GigJob.objects.filter(title='Office Cleaning').exists())
    
    def test_job_search(self):
        """Test job search functionality."""
        self.authenticate_user()
        
        response = self.client.get('/api/v1/gig-management/jobs/search/?q=cleaning')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
    
    def test_job_stats(self):
        """Test job statistics endpoint."""
        self.authenticate_user()
        
        response = self.client.get(f'/api/v1/gig-management/jobs/{self.job.id}/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('applications_count', response.data)
        self.assertIn('milestones_count', response.data)


class GigApplicationTests(TestCase):
    """Test cases for GigApplication model and API."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123'
        )
        self.freelancer_user = User.objects.create_user(
            username='freelancer',
            email='freelancer@test.com',
            password='testpass123'
        )
        
        # Create freelancer profile
        from apps.freelancers.models import Freelancer
        self.freelancer = Freelancer.objects.create(
            user=self.freelancer_user,
            first_name='John',
            last_name='Freelancer',
            date_of_birth='1990-01-01',
            personal_email='john@example.com',
            personal_phone='+1234567890',
            address_line1='123 Freelancer St',
            city='New York',
            state='NY',
            postal_code='10001',
            country='US',
            hourly_rate=25.00
        )
        
        self.category = GigCategory.objects.create(
            name='Test Category',
            description='Test description'
        )
        
        self.job = GigJob.objects.create(
            title='Test Job',
            description='Test job description',
            category=self.category,
            client=self.user,
            client_type='individual',
            service_address='123 Test St',
            city='Test City',
            state='TS',
            postal_code='12345',
            country='US',
            status='published'
        )
    
    def authenticate_freelancer(self):
        """Helper to authenticate freelancer."""
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(self.freelancer_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_application_creation(self):
        """Test creating a job application."""
        application = GigApplication.objects.create(
            job=self.job,
            freelancer=self.freelancer,
            cover_letter='I am interested in this job.',
            proposed_rate=30.00,
            estimated_completion_time=3.0
        )
        
        self.assertEqual(application.job, self.job)
        self.assertEqual(application.freelancer, self.freelancer)
        self.assertEqual(application.status, 'submitted')
    
    def test_application_api_create(self):
        """Test creating application via API."""
        self.authenticate_freelancer()
        
        data = {
            'job': self.job.id,
            'cover_letter': 'I would like to apply for this job.',
            'proposed_rate': 28.00,
            'estimated_completion_time': 4.0
        }
        
        response = self.client.post(
            f'/api/v1/gig-management/jobs/{self.job.id}/applications/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(GigApplication.objects.filter(job=self.job, freelancer=self.freelancer).exists())
    
    def test_application_unique_constraint(self):
        """Test that a freelancer can only apply once to a job."""
        # Create first application
        GigApplication.objects.create(
            job=self.job,
            freelancer=self.freelancer,
            cover_letter='First application'
        )
        
        # Try to create second application - should fail
        with self.assertRaises(IntegrityError):
            GigApplication.objects.create(
                job=self.job,
                freelancer=self.freelancer,
                cover_letter='Second application'
            )


class JobMilestoneTests(TestCase):
    """Test cases for JobMilestone model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123'
        )
        self.category = GigCategory.objects.create(
            name='Test Category',
            description='Test description'
        )
        self.job = GigJob.objects.create(
            title='Test Job',
            description='Test job description',
            category=self.category,
            client=self.user,
            client_type='individual',
            service_address='123 Test St',
            city='Test City',
            state='TS',
            postal_code='12345',
            country='US'
        )
    
    def test_milestone_creation(self):
        """Test creating a job milestone."""
        milestone = JobMilestone.objects.create(
            job=self.job,
            milestone_type='start',
            title='Job Started',
            description='Freelancer has started the job',
            expected_date=datetime.now()
        )
        
        self.assertEqual(milestone.job, self.job)
        self.assertEqual(milestone.milestone_type, 'start')
        self.assertFalse(milestone.is_completed)


class JobReviewTests(TestCase):
    """Test cases for JobReview model."""
    
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
        self.category = GigCategory.objects.create(
            name='Test Category',
            description='Test description'
        )
        self.job = GigJob.objects.create(
            title='Test Job',
            description='Test job description',
            category=self.category,
            client=self.user,
            client_type='individual',
            service_address='123 Test St',
            city='Test City',
            state='TS',
            postal_code='12345',
            country='US',
            status='completed'
        )
    
    def test_review_creation(self):
        """Test creating a job review."""
        review = JobReview.objects.create(
            job=self.job,
            reviewer=self.reviewer,
            overall_rating=5,
            quality_rating=5,
            timeliness_rating=4,
            communication_rating=5,
            professionalism_rating=5,
            title='Great job!',
            comment='Excellent work, highly recommended.',
            would_recommend=True
        )
        
        self.assertEqual(review.job, self.job)
        self.assertEqual(review.reviewer, self.reviewer)
        self.assertEqual(review.overall_rating, 5)
        self.assertEqual(review.average_rating, 4.8)  # (5+5+4+5+5)/5
    
    def test_review_unique_constraint(self):
        """Test that a user can only review a job once."""
        # Create first review
        JobReview.objects.create(
            job=self.job,
            reviewer=self.reviewer,
            overall_rating=5,
            quality_rating=5,
            timeliness_rating=4,
            communication_rating=5,
            professionalism_rating=5,
            title='Great job!',
            comment='Excellent work.'
        )
        
        # Try to create second review - should fail
        with self.assertRaises(IntegrityError):
            JobReview.objects.create(
                job=self.job,
                reviewer=self.reviewer,
                overall_rating=4,
                quality_rating=4,
                timeliness_rating=5,
                communication_rating=4,
                professionalism_rating=4,
                title='Second review',
                comment='Another comment.'
            )


@pytest.mark.django_db
class GigManagementIntegrationTests:
    """Integration tests for gig management workflows."""
    
    def test_complete_job_application_flow(self, freelancer_profile, gig_job):
        """Test the complete job application workflow."""
        client = APIClient()
        
        # Authenticate freelancer
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(freelancer_profile.user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Apply to job
        data = {
            'cover_letter': 'I am very interested in this job.',
            'proposed_rate': 30.00,
            'estimated_completion_time': 4.0
        }
        
        response = client.post(
            f'/api/v1/gig-management/jobs/{gig_job.id}/applications/',
            data
        )
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify application was created
        from apps.gig_management.models import GigApplication
        application = GigApplication.objects.get(job=gig_job, freelancer=freelancer_profile)
        assert application.cover_letter == data['cover_letter']
        assert application.proposed_rate == data['proposed_rate']
    
    def test_job_creation_to_completion_flow(self, client_user, gig_category):
        """Test complete job lifecycle from creation to completion."""
        client = APIClient()
        
        # Authenticate client
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(client_user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Create job
        job_data = {
            'title': 'Complete Test Job',
            'description': 'Full workflow test job',
            'category': gig_category.id,
            'client_type': 'individual',
            'service_address': '123 Test St',
            'city': 'Test City',
            'state': 'TS',
            'postal_code': '12345',
            'country': 'US',
            'service_type': 'deep_cleaning',
            'property_type': 'house',
            'payment_method': 'hourly',
            'hourly_rate': 35.00,
            'estimated_duration_hours': 6.0
        }
        
        response = client.post('/api/v1/gig-management/jobs/', job_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify job was created
        from apps.gig_management.models import GigJob
        job = GigJob.objects.get(title=job_data['title'])
        assert job.client == client_user
        assert job.status == 'draft'
        
        # Update job status to published
        update_response = client.patch(
            f'/api/v1/gig-management/jobs/{job.id}/',
            {'status': 'published'}
        )
        assert update_response.status_code == status.HTTP_200_OK
        
        job.refresh_from_db()
        assert job.status == 'published'
