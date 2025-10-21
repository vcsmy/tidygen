"""
Tests for contractor_payments app.
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db import IntegrityError
from rest_framework import status
from rest_framework.test import APIClient
from decimal import Decimal
from datetime import datetime, timezone
from unittest.mock import patch

from .models import PaymentMethod, ContractorPayment, EscrowAccount, PaymentSchedule, DisputeResolution

User = get_user_model()


class PaymentMethodModelTests(TestCase):
    """Test cases for PaymentMethod model."""
    
    def test_payment_method_creation(self):
        """Test creating a payment method."""
        method = PaymentMethod.objects.create(
            name='Bank Transfer',
            payment_type='bank_transfer',
            processing_fee_percentage=1.5,
            min_payment_amount=10.00,
            max_payment_amount=10000.00,
            supported_currencies=['USD', 'EUR']
        )
        
        self.assertEqual(method.name, 'Bank Transfer')
        self.assertEqual(method.payment_type, 'bank_transfer')
        self.assertEqual(method.processing_fee_percentage, Decimal('1.5'))
        self.assertTrue(method.is_active)
    
    def test_payment_method_web3_enabled(self):
        """Test Web3 enabled payment method."""
        method = PaymentMethod.objects.create(
            name='Crypto Wallet',
            payment_type='crypto_wallet',
            web3_enabled=True,
            supported_currencies=['ETH', 'BTC']
        )
        
        self.assertTrue(method.web3_enabled)
        self.assertIn('ETH', method.supported_currencies)


class ContractorPaymentModelTests(TestCase):
    """Test cases for ContractorPayment model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create freelancer profile
        from apps.freelancers.models import Freelancer
        self.freelancer = Freelancer.objects.create(
            user=self.user,
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
        
        self.payment_method = PaymentMethod.objects.create(
            name='Test Payment Method',
            payment_type='bank_transfer',
            processing_fee_percentage=2.0
        )
    
    @patch('apps.contractor_payments.models.uuid.uuid4')
    def test_payment_id_generation(self, mock_uuid):
        """Test that payment ID is generated automatically."""
        mock_uuid.return_value.hex = '12345678abcdef'
        
        payment = ContractorPayment.objects.create(
            freelancer=self.freelancer,
            payment_method=self.payment_method,
            amount=100.00,
            currency='USD',
            payment_trigger='job_completion'
        )
        
        self.assertTrue(payment.payment_id.startswith('PAY'))
        self.assertEqual(len(payment.payment_id), 11)  # PAY + 8 chars
    
    def test_net_amount_calculation(self):
        """Test that net amount is calculated correctly."""
        payment = ContractorPayment.objects.create(
            freelancer=self.freelancer,
            payment_method=self.payment_method,
            amount=100.00,
            currency='USD',
            processing_fee=2.50,  # 2.5% of 100 = 2.50
            payment_trigger='job_completion'
        )
        
        # Net amount should be amount - processing fee
        expected_net = Decimal('100.00') - Decimal('2.50')
        self.assertEqual(payment.net_amount, expected_net)
    
    def test_payment_save_calculates_net_amount(self):
        """Test that save method calculates net amount if not set."""
        payment = ContractorPayment(
            freelancer=self.freelancer,
            payment_method=self.payment_method,
            amount=150.00,
            currency='USD',
            processing_fee=3.00,
            payment_trigger='job_completion'
        )
        
        # Net amount should be calculated on save
        payment.save()
        expected_net = Decimal('150.00') - Decimal('3.00')
        self.assertEqual(payment.net_amount, expected_net)


class ContractorPaymentAPITests(TestCase):
    """Test cases for ContractorPayment API endpoints."""
    
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
        
        # Create freelancer profile
        from apps.freelancers.models import Freelancer
        self.freelancer = Freelancer.objects.create(
            user=self.user,
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
        
        self.payment_method = PaymentMethod.objects.create(
            name='Bank Transfer',
            payment_type='bank_transfer',
            processing_fee_percentage=1.5
        )
        
        self.payment = ContractorPayment.objects.create(
            freelancer=self.freelancer,
            payment_method=self.payment_method,
            amount=200.00,
            currency='USD',
            payment_trigger='job_completion',
            status='pending'
        )
    
    def authenticate_user(self, user=None):
        """Helper to authenticate user."""
        from rest_framework_simplejwt.tokens import RefreshToken
        if user is None:
            user = self.user
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_payment_list_unauthenticated(self):
        """Test that unauthenticated users cannot access payment list."""
        response = self.client.get('/api/v1/contractor-payments/payments/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_payment_list_authenticated_freelancer(self):
        """Test that freelancers can access their own payments."""
        self.authenticate_user()
        response = self.client.get('/api/v1/contractor-payments/payments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_payment_detail(self):
        """Test payment detail endpoint."""
        self.authenticate_user()
        response = self.client.get(f'/api/v1/contractor-payments/payments/{self.payment.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['payment_id'], self.payment.payment_id)
    
    def test_payment_statistics(self):
        """Test payment statistics endpoint."""
        self.authenticate_user()
        
        # Create completed payment for statistics
        ContractorPayment.objects.create(
            freelancer=self.freelancer,
            payment_method=self.payment_method,
            amount=150.00,
            currency='USD',
            payment_trigger='milestone_completion',
            status='completed'
        )
        
        response = self.client.get(f'/api/v1/contractor-payments/freelancers/{self.freelancer.id}/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_payments', response.data)
        self.assertIn('completed_payments', response.data)
        self.assertIn('total_paid', response.data)


class EscrowAccountModelTests(TestCase):
    """Test cases for EscrowAccount model."""
    
    def setUp(self):
        """Set up test data."""
        self.client_user = User.objects.create_user(
            username='client',
            email='client@test.com',
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
        
        # Create job
        from apps.gig_management.models import GigCategory, GigJob
        self.category = GigCategory.objects.create(
            name='Test Category',
            description='Test description'
        )
        
        self.job = GigJob.objects.create(
            title='Test Job',
            description='Test job description',
            category=self.category,
            client=self.client_user,
            client_type='individual',
            service_address='123 Test St',
            city='Test City',
            state='TS',
            postal_code='12345',
            country='US'
        )
    
    @patch('apps.contractor_payments.models.uuid.uuid4')
    def test_escrow_id_generation(self, mock_uuid):
        """Test that escrow ID is generated automatically."""
        mock_uuid.return_value.hex = '12345678abcdef'
        
        escrow = EscrowAccount.objects.create(
            job=self.job,
            client=self.client_user,
            freelancer=self.freelancer,
            total_amount=500.00,
            currency='USD',
            platform_fee=25.00
        )
        
        self.assertTrue(escrow.escrow_id.startswith('ESCROW'))
        self.assertEqual(len(escrow.escrow_id), 11)  # ESCROW + 6 chars
    
    def test_escrow_net_amount_calculation(self):
        """Test escrow net amount calculation."""
        escrow = EscrowAccount.objects.create(
            job=self.job,
            client=self.client_user,
            freelancer=self.freelancer,
            total_amount=500.00,
            currency='USD',
            platform_fee=25.00
        )
        
        expected_net = Decimal('500.00') - Decimal('25.00')
        self.assertEqual(escrow.net_amount, expected_net)
    
    def test_escrow_is_funded_property(self):
        """Test the is_funded property."""
        escrow = EscrowAccount.objects.create(
            job=self.job,
            client=self.client_user,
            freelancer=self.freelancer,
            total_amount=500.00,
            currency='USD',
            status='funded',
            blockchain_transaction_hash='0x1234567890abcdef'
        )
        
        self.assertTrue(escrow.is_funded)


class PaymentScheduleTests(TestCase):
    """Test cases for PaymentSchedule model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123'
        )
        
        # Create freelancer profile
        from apps.freelancers.models import Freelancer
        self.freelancer = Freelancer.objects.create(
            user=self.user,
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
        
        self.payment_method = PaymentMethod.objects.create(
            name='Bank Transfer',
            payment_type='bank_transfer'
        )
    
    def test_payment_schedule_creation(self):
        """Test creating a payment schedule."""
        schedule = PaymentSchedule.objects.create(
            freelancer=self.freelancer,
            schedule_type='weekly',
            next_payment_date=datetime.now(timezone.utc),
            payment_method=self.payment_method,
            fixed_amount=500.00,
            currency='USD'
        )
        
        self.assertEqual(schedule.freelancer, self.freelancer)
        self.assertEqual(schedule.schedule_type, 'weekly')
        self.assertEqual(schedule.fixed_amount, Decimal('500.00'))
        self.assertTrue(schedule.is_active)


class DisputeResolutionTests(TestCase):
    """Test cases for DisputeResolution model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123'
        )
        
        self.disputer = User.objects.create_user(
            username='disputer',
            email='disputer@test.com',
            password='testpass123'
        )
        
        # Create freelancer profile
        from apps.freelancers.models import Freelancer
        self.freelancer = Freelancer.objects.create(
            user=self.user,
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
        
        self.payment_method = PaymentMethod.objects.create(
            name='Bank Transfer',
            payment_type='bank_transfer'
        )
        
        self.payment = ContractorPayment.objects.create(
            freelancer=self.freelancer,
            payment_method=self.payment_method,
            amount=200.00,
            currency='USD',
            payment_trigger='job_completion',
            status='completed'
        )
    
    def test_dispute_creation(self):
        """Test creating a dispute resolution."""
        dispute = DisputeResolution.objects.create(
            payment=self.payment,
            dispute_type='payment_quality',
            description='Payment amount does not match work quality',
            raised_by=self.disputer
        )
        
        self.assertEqual(dispute.payment, self.payment)
        self.assertEqual(dispute.raised_by, self.disputer)
        self.assertEqual(dispute.dispute_type, 'payment_quality')
        self.assertEqual(dispute.status, 'submitted')


@pytest.mark.django_db
class PaymentIntegrationTests:
    """Integration tests for payment workflows."""
    
    def test_complete_payment_flow(self, freelancer_profile, payment_method):
        """Test complete payment creation and processing flow."""
        client = APIClient()
        
        # Authenticate freelancer
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(freelancer_profile.user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Create payment
        payment_data = {
            'payment_method': payment_method.id,
            'amount': 250.00,
            'currency': 'USD',
            'payment_trigger': 'job_completion',
            'scheduled_date': '2024-01-15T10:00:00Z'
        }
        
        response = client.post('/api/v1/contractor-payments/payments/', payment_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify payment was created
        from apps.contractor_payments.models import ContractorPayment
        payment = ContractorPayment.objects.get(freelancer=freelancer_profile)
        assert payment.amount == payment_data['amount']
        assert payment.status == 'pending'
        
        # Test payment statistics
        stats_response = client.get(f'/api/v1/contractor-payments/freelancers/{freelancer_profile.id}/stats/')
        assert stats_response.status_code == status.HTTP_200_OK
        assert stats_response.data['pending_amount'] == float(payment_data['amount'])
    
    def test_escrow_account_lifecycle(self, freelancer_profile, client_user, gig_job):
        """Test escrow account from creation to release."""
        from apps.contractor_payments.models import EscrowAccount
        
        # Create escrow account
        escrow = EscrowAccount.objects.create(
            job=gig_job,
            client=client_user,
            freelancer=freelancer_profile,
            total_amount=1000.00,
            currency='USD',
            platform_fee=50.00,
            status='pending_deposit'
        )
        
        assert escrow.status == 'pending_deposit'
        assert escrow.net_amount == 950.00
        
        # Fund escrow
        escrow.status = 'funded'
        escrow.blockchain_transaction_hash = '0x1234567890abcdef'
        escrow.funded_date = datetime.now(timezone.utc)
        escrow.save()
        
        assert escrow.is_funded
        
        # Release escrow
        escrow.status = 'released'
        escrow.release_date = datetime.now(timezone.utc)
        escrow.save()
        
        assert escrow.status == 'released'
