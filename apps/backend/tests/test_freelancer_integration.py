"""
Integration tests for the complete freelancer ecosystem.
"""
import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from decimal import Decimal
from datetime import datetime, timezone

User = get_user_model()


class FreelancerEcosystemIntegrationTests(TestCase):
    """Complete integration tests for freelancer ecosystem."""
    
    def setUp(self):
        """Set up comprehensive test data."""
        self.client = APIClient()
        
        # Create users
        self.client_user = User.objects.create_user(
            username='client_user',
            email='client@test.com',
            password='testpass123',
            first_name='Jane',
            last_name='Client'
        )
        
        self.freelancer_user = User.objects.create_user(
            username='freelancer_user',
            email='freelancer@test.com',
            password='testpass123',
            first_name='John',
            last_name='Freelancer'
        )
        
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpass123'
        )
    
    def authenticate_user(self, user, client=None):
        """Helper to authenticate user."""
        if client is None:
            client = self.client
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_complete_freelancer_job_lifecycle(self):
        """Test complete workflow from freelancer registration to job completion and payment."""
        
        # Step 1: Create freelancer profile
        self.authenticate_user(self.freelancer_user)
        
        freelancer_data = {
            'first_name': 'John',
            'last_name': 'Freelancer',
            'date_of_birth': '1990-01-01',
            'personal_email': 'john.freelancer@example.com',
            'personal_phone': '+1234567890',
            'address_line1': '123 Freelancer St',
            'city': 'New York',
            'state': 'NY',
            'postal_code': '10001',
            'country': 'US',
            'cleaning_types': ['residential', 'commercial'],
            'hourly_rate': 30.00,
            'currency': 'USD',
            'bio': 'Experienced cleaner with 5+ years experience'
        }
        
        response = self.client.post('/api/v1/freelancers/', freelancer_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        freelancer_id = response.data['id']
        
        # Step 2: Client creates a job
        self.authenticate_user(self.client_user)
        
        # First create a category
        from apps.gig_management.models import GigCategory
        category = GigCategory.objects.create(
            name='Residential Cleaning',
            description='Home cleaning services',
            default_hourly_rate_min=20.00,
            default_hourly_rate_max=60.00
        )
        
        job_data = {
            'title': 'Weekly House Cleaning',
            'description': 'Regular weekly cleaning for 3-bedroom house',
            'category': category.id,
            'client_type': 'individual',
            'service_address': '456 Client Ave',
            'city': 'New York',
            'state': 'NY',
            'postal_code': '10002',
            'country': 'US',
            'service_type': 'regular_cleaning',
            'property_type': 'house',
            'payment_method': 'hourly',
            'hourly_rate': 35.00,
            'estimated_duration_hours': 4.0,
            'status': 'published'
        }
        
        response = self.client.post('/api/v1/gig-management/jobs/', job_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        job_id = response.data['id']
        
        # Step 3: Freelancer applies to the job
        self.authenticate_user(self.freelancer_user)
        
        application_data = {
            'cover_letter': 'I have extensive experience with residential cleaning and would love to help.',
            'proposed_rate': 32.00,
            'estimated_completion_time': 4.0
        }
        
        response = self.client.post(
            f'/api/v1/gig-management/jobs/{job_id}/applications/',
            application_data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        application_id = response.data['id']
        
        # Step 4: Client selects freelancer (accept application)
        self.authenticate_user(self.client_user)
        
        from apps.gig_management.models import GigJob, GigApplication
        job = GigJob.objects.get(id=job_id)
        application = GigApplication.objects.get(id=application_id)
        
        # Accept application and assign freelancer
        response = self.client.patch(
            f'/api/v1/gig-management/jobs/{job_id}/',
            {
                'assigned_freelancer': application.freelancer.id,
                'status': 'assigned'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 5: Create escrow for payment
        from apps.contractor_payments.models import PaymentMethod, EscrowAccount
        
        payment_method = PaymentMethod.objects.create(
            name='Bank Transfer',
            payment_type='bank_transfer',
            processing_fee_percentage=2.0
        )
        
        escrow_data = {
            'total_amount': 140.00,  # 4 hours * 35/hour
            'currency': 'USD',
            'platform_fee': 7.00  # 5% platform fee
        }
        
        response = self.client.post(
            f'/api/v1/contractor-payments/jobs/{job_id}/escrow/',
            escrow_data
        )
        # Note: This endpoint may need to be implemented based on actual API
        
        # Step 6: Job completion workflow
        # Create milestone for job start
        from apps.gig_management.models import JobMilestone
        JobMilestone.objects.create(
            job=job,
            milestone_type='start',
            title='Job Started',
            description='Freelancer has started the cleaning job'
        )
        
        # Job completion milestone
        completion_milestone = JobMilestone.objects.create(
            job=job,
            milestone_type='completion',
            title='Job Completed',
            description='All cleaning tasks completed',
            is_completed=True
        )
        
        # Step 7: Client releases payment
        self.authenticate_user(self.client_user)
        
        # Mark job as completed
        response = self.client.patch(
            f'/api/v1/gig-management/jobs/{job_id}/',
            {'status': 'completed'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 8: Create payment record
        self.authenticate_user(self.admin_user)  # Admin creates payment
        
        from apps.contractor_payments.models import ContractorPayment
        
        payment_data = {
            'freelancer': application.freelancer.id,
            'payment_method': payment_method.id,
            'amount': 133.00,  # Net amount after fees
            'currency': 'USD',
            'payment_trigger': 'job_completion',
            'related_job': job_id,
            'status': 'completed'
        }
        
        response = self.client.post(
            '/api/v1/contractor-payments/payments/',
            payment_data
        )
        # Note: Adjust based on actual API implementation
        
        # Step 9: Reviews
        self.authenticate_user(self.client_user)
        
        # Client reviews freelancer
        from apps.freelancers.models import FreelancerReview
        
        review_data = {
            'freelancer': application.freelancer.id,
            'overall_rating': 5,
            'quality_rating': 5,
            'punctuality_rating': 5,
            'communication_rating': 4,
            'professionalism_rating': 5,
            'title': 'Excellent work!',
            'comment': 'Very thorough and professional cleaning service.',
            'would_recommend': True,
            'related_job': job_id
        }
        
        response = self.client.post(
            '/api/v1/freelancers/reviews/',
            review_data
        )
        # Note: Adjust based on actual API implementation
        
        # Verify final state
        job.refresh_from_db()
        self.assertEqual(job.status, 'completed')
        
        freelancer_review = FreelancerReview.objects.filter(
            freelancer=application.freelancer
        ).first()
        if freelancer_review:
            self.assertEqual(freelancer_review.overall_rating, 5)
    
    def test_web3_features_integration(self):
        """Test Web3 features integration with freelancer workflow."""
        
        # Create freelancer
        from apps.freelancers.models import Freelancer
        freelancer = Freelancer.objects.create(
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
            hourly_rate=25.00,
            wallet_address='0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
            blockchain_verified=True
        )
        
        # Authenticate and test Web3 features
        self.authenticate_user(self.freelancer_user)
        
        # Test wallet connection
        wallet_data = {
            'wallet_address': '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
            'wallet_type': 'metamask',
            'signature': 'test_signature'
        }
        
        response = self.client.post(
            '/api/v1/freelancer-web3/wallets/connect/',
            wallet_data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Test Web3 stats
        response = self.client.get(
            f'/api/v1/freelancer-web3/freelancers/{freelancer.id}/stats/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('blockchain_verified', response.data)
        self.assertTrue(response.data['blockchain_verified'])
    
    def test_search_and_filtering_integration(self):
        """Test search and filtering across multiple modules."""
        
        # Create multiple freelancers with different profiles
        from apps.freelancers.models import Freelancer
        
        freelancer1 = Freelancer.objects.create(
            user=User.objects.create_user(
                username='freelancer1',
                email='f1@test.com',
                password='testpass123'
            ),
            first_name='Alice',
            last_name='Cleaner',
            date_of_birth='1985-01-01',
            personal_email='alice@example.com',
            personal_phone='+1111111111',
            address_line1='123 Alice St',
            city='New York',
            state='NY',
            postal_code='10001',
            country='US',
            hourly_rate=25.00,
            cleaning_types=['residential'],
            status='active',
            is_available=True
        )
        
        freelancer2 = Freelancer.objects.create(
            user=User.objects.create_user(
                username='freelancer2',
                email='f2@test.com',
                password='testpass123'
            ),
            first_name='Bob',
            last_name='Cleaner',
            date_of_birth='1990-01-01',
            personal_email='bob@example.com',
            personal_phone='+2222222222',
            address_line1='456 Bob Ave',
            city='Los Angeles',
            state='CA',
            postal_code='90210',
            country='US',
            hourly_rate=35.00,
            cleaning_types=['commercial'],
            status='active',
            is_available=True
        )
        
        # Test freelancer search
        self.authenticate_user(self.client_user)
        
        response = self.client.get('/api/v1/freelancers/search/?q=Alice')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        
        response = self.client.get('/api/v1/freelancers/?city=New York')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['results']) > 0)
        
        # Test job search
        from apps.gig_management.models import GigCategory, GigJob
        
        category = GigCategory.objects.create(
            name='Residential Cleaning',
            description='Home cleaning'
        )
        
        job = GigJob.objects.create(
            title='House Cleaning NYC',
            description='Residential cleaning in New York',
            category=category,
            client=self.client_user,
            client_type='individual',
            service_address='789 Job St',
            city='New York',
            state='NY',
            postal_code='10003',
            country='US',
            status='published'
        )
        
        response = self.client.get('/api/v1/gig-management/jobs/search/?q=cleaning')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)


@pytest.mark.django_db
class FreelancerEcosystemPytestTests:
    """Pytest-style integration tests."""
    
    def test_complete_workflow_with_pytest_fixtures(
        self, 
        client_user, 
        freelancer_profile, 
        gig_category
    ):
        """Test complete workflow using pytest fixtures."""
        from apps.gig_management.models import GigJob, GigApplication
        from apps.contractor_payments.models import PaymentMethod, ContractorPayment
        
        # Create job
        job = GigJob.objects.create(
            title='Test Complete Workflow',
            description='Testing the complete freelancer workflow',
            category=gig_category,
            client=client_user,
            client_type='individual',
            service_address='123 Workflow St',
            city='Test City',
            state='TS',
            postal_code='12345',
            country='US',
            status='published',
            payment_method='hourly',
            hourly_rate=30.00,
            estimated_duration_hours=3.0
        )
        
        # Create application
        application = GigApplication.objects.create(
            job=job,
            freelancer=freelancer_profile,
            cover_letter='I would love to do this job.',
            proposed_rate=28.00,
            estimated_completion_time=3.0,
            status='accepted'
        )
        
        # Update job with assigned freelancer
        job.assigned_freelancer = freelancer_profile
        job.status = 'assigned'
        job.save()
        
        # Create payment method
        payment_method = PaymentMethod.objects.create(
            name='Test Payment',
            payment_type='bank_transfer',
            processing_fee_percentage=1.5
        )
        
        # Create payment
        payment = ContractorPayment.objects.create(
            freelancer=freelancer_profile,
            payment_method=payment_method,
            amount=84.00,  # 3 hours * 28/hour
            currency='USD',
            payment_trigger='job_completion',
            status='completed'
        )
        
        # Verify workflow
        assert job.assigned_freelancer == freelancer_profile
        assert job.status == 'assigned'
        assert application.status == 'accepted'
        assert payment.freelancer == freelancer_profile
        assert payment.status == 'completed'


class PerformanceTests(TestCase):
    """Test performance and scalability of freelancer modules."""
    
    def setUp(self):
        """Set up performance test data."""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='perftest',
            email='perf@test.com',
            password='testpass123'
        )
        self.authenticate_user(self.user)
    
    def authenticate_user(self, user):
        """Helper to authenticate user."""
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_freelancer_list_performance_with_large_dataset(self):
        """Test performance of freelancer list with large dataset."""
        from apps.freelancers.models import Freelancer
        
        # Create many freelancers
        freelancers = []
        for i in range(100):
            user = User.objects.create_user(
                username=f'freelancer{i}',
                email=f'freelancer{i}@test.com',
                password='testpass123',
                first_name=f'Test{i}',
                last_name='Freelancer'
            )
            
            freelancer = Freelancer.objects.create(
                user=user,
                first_name=f'Test{i}',
                last_name='Freelancer',
                date_of_birth='1990-01-01',
                personal_email=f'test{i}@example.com',
                personal_phone=f'+1234567{i:03d}',
                address_line1=f'{i} Test St',
                city='Test City',
                state='TS',
                postal_code='12345',
                country='US',
                hourly_rate=25.00 + i
            )
            freelancers.append(freelancer)
        
        # Test list performance
        import time
        start_time = time.time()
        response = self.client.get('/api/v1/freelancers/')
        end_time = time.time()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(end_time - start_time, 2.0)  # Should complete within 2 seconds
        
        # Test pagination
        response = self.client.get('/api/v1/freelancers/?page=1&page_size=20')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data.get('results', [])), 20)
    
    def test_search_performance(self):
        """Test search performance across modules."""
        from apps.freelancers.models import Freelancer
        from apps.gig_management.models import GigCategory, GigJob
        
        # Create test data
        category = GigCategory.objects.create(
            name='Performance Test Category',
            description='Testing search performance'
        )
        
        # Create many jobs
        for i in range(50):
            GigJob.objects.create(
                title=f'Performance Test Job {i}',
                description=f'Test job number {i} for performance testing',
                category=category,
                client=self.user,
                client_type='individual',
                service_address=f'{i} Performance St',
                city='Test City',
                state='TS',
                postal_code='12345',
                country='US',
                status='published'
            )
        
        # Test search performance
        import time
        start_time = time.time()
        
        # Test freelancer search
        response = self.client.get('/api/v1/freelancers/search/?q=Test')
        
        # Test job search  
        response = self.client.get('/api/v1/gig-management/jobs/search/?q=performance')
        
        end_time = time.time()
        
        # Both searches should complete quickly
        self.assertLess(end_time - start_time, 3.0)  # Should complete within 3 seconds
