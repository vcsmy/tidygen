"""
Purchasing Management Tests

This module contains comprehensive tests for the purchasing management system,
including unit tests, integration tests, and API tests for all purchasing functionality.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from datetime import datetime, timedelta
import json

from apps.purchasing.models import (
    PurchaseOrder, PurchaseOrderItem, PurchaseReceipt, PurchaseReceiptItem,
    ProcurementRequest, ProcurementRequestItem, SupplierPerformance, PurchaseAnalytics
)
from apps.inventory.models import Product, Supplier, Category

User = get_user_model()


class PurchaseOrderModelTest(TestCase):
    """Test cases for PurchaseOrder model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.organization
        )
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            email="supplier@example.com",
            phone="1234567890",
            organization=self.organization
        )
        self.category = Category.objects.create(
            name="Test Category",
            organization=self.organization
        )
        self.product = Product.objects.create(
            name="Test Product",
            sku="TEST001",
            description="Test product description",
            category=self.category,
            organization=self.organization
        )
    
    def test_purchase_order_creation(self):
        """Test creating a purchase order."""
        po = PurchaseOrder.objects.create(
            organization=self.organization,
            supplier=self.supplier,
            requested_by=self.user,
            status='draft',
            priority='medium'
        )
        
        self.assertEqual(po.organization, self.organization)
        self.assertEqual(po.supplier, self.supplier)
        self.assertEqual(po.requested_by, self.user)
        self.assertEqual(po.status, 'draft')
        self.assertEqual(po.priority, 'medium')
        self.assertTrue(po.po_number)  # Should be auto-generated
    
    def test_purchase_order_po_number_generation(self):
        """Test automatic PO number generation."""
        po1 = PurchaseOrder.objects.create(
            organization=self.organization,
            supplier=self.supplier,
            requested_by=self.user
        )
        po2 = PurchaseOrder.objects.create(
            organization=self.organization,
            supplier=self.supplier,
            requested_by=self.user
        )
        
        self.assertNotEqual(po1.po_number, po2.po_number)
        self.assertTrue(po1.po_number.startswith('PO'))
        self.assertTrue(po2.po_number.startswith('PO'))
    
    def test_purchase_order_str_representation(self):
        """Test string representation of purchase order."""
        po = PurchaseOrder.objects.create(
            organization=self.organization,
            supplier=self.supplier,
            requested_by=self.user
        )
        
        expected = f"PO-{po.po_number} - {self.supplier.name}"
        self.assertEqual(str(po), expected)


class PurchaseOrderItemModelTest(TestCase):
    """Test cases for PurchaseOrderItem model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.organization
        )
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            email="supplier@example.com",
            phone="1234567890",
            organization=self.organization
        )
        self.category = Category.objects.create(
            name="Test Category",
            organization=self.organization
        )
        self.product = Product.objects.create(
            name="Test Product",
            sku="TEST001",
            description="Test product description",
            category=self.category,
            organization=self.organization
        )
        self.purchase_order = PurchaseOrder.objects.create(
            organization=self.organization,
            supplier=self.supplier,
            requested_by=self.user
        )
    
    def test_purchase_order_item_creation(self):
        """Test creating a purchase order item."""
        item = PurchaseOrderItem.objects.create(
            purchase_order=self.purchase_order,
            product=self.product,
            quantity_ordered=10,
            unit_price=Decimal('25.00')
        )
        
        self.assertEqual(item.purchase_order, self.purchase_order)
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.quantity_ordered, 10)
        self.assertEqual(item.unit_price, Decimal('25.00'))
        self.assertEqual(item.total_price, Decimal('250.00'))
        self.assertEqual(item.quantity_pending, 10)  # Initially all pending
    
    def test_purchase_order_item_calculations(self):
        """Test automatic calculations in purchase order item."""
        item = PurchaseOrderItem.objects.create(
            purchase_order=self.purchase_order,
            product=self.product,
            quantity_ordered=5,
            unit_price=Decimal('20.00'),
            quantity_received=2
        )
        
        self.assertEqual(item.total_price, Decimal('100.00'))  # 5 * 20
        self.assertEqual(item.quantity_pending, 3)  # 5 - 2
    
    def test_purchase_order_item_product_details_storage(self):
        """Test that product details are stored at time of order."""
        item = PurchaseOrderItem.objects.create(
            purchase_order=self.purchase_order,
            product=self.product,
            quantity_ordered=1,
            unit_price=Decimal('10.00')
        )
        
        # Change the product name
        self.product.name = "Updated Product Name"
        self.product.save()
        
        # Item should still have original name
        item.refresh_from_db()
        self.assertEqual(item.product_name, "Test Product")


class PurchaseReceiptModelTest(TestCase):
    """Test cases for PurchaseReceipt model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.organization
        )
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            email="supplier@example.com",
            phone="1234567890",
            organization=self.organization
        )
        self.purchase_order = PurchaseOrder.objects.create(
            organization=self.organization,
            supplier=self.supplier,
            requested_by=self.user
        )
    
    def test_purchase_receipt_creation(self):
        """Test creating a purchase receipt."""
        receipt = PurchaseReceipt.objects.create(
            purchase_order=self.purchase_order,
            received_by=self.user,
            status='pending'
        )
        
        self.assertEqual(receipt.purchase_order, self.purchase_order)
        self.assertEqual(receipt.received_by, self.user)
        self.assertEqual(receipt.status, 'pending')
        self.assertTrue(receipt.receipt_number)  # Should be auto-generated
    
    def test_purchase_receipt_number_generation(self):
        """Test automatic receipt number generation."""
        receipt1 = PurchaseReceipt.objects.create(
            purchase_order=self.purchase_order,
            received_by=self.user
        )
        receipt2 = PurchaseReceipt.objects.create(
            purchase_order=self.purchase_order,
            received_by=self.user
        )
        
        self.assertNotEqual(receipt1.receipt_number, receipt2.receipt_number)
        self.assertTrue(receipt1.receipt_number.startswith('REC'))
        self.assertTrue(receipt2.receipt_number.startswith('REC'))


class ProcurementRequestModelTest(TestCase):
    """Test cases for ProcurementRequest model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.organization
        )
    
    def test_procurement_request_creation(self):
        """Test creating a procurement request."""
        request = ProcurementRequest.objects.create(
            organization=self.organization,
            requested_by=self.user,
            title="Test Request",
            description="Test description",
            justification="Test justification",
            status='draft',
            priority='medium'
        )
        
        self.assertEqual(request.organization, self.organization)
        self.assertEqual(request.requested_by, self.user)
        self.assertEqual(request.title, "Test Request")
        self.assertEqual(request.status, 'draft')
        self.assertEqual(request.priority, 'medium')
        self.assertTrue(request.request_number)  # Should be auto-generated
    
    def test_procurement_request_number_generation(self):
        """Test automatic request number generation."""
        request1 = ProcurementRequest.objects.create(
            organization=self.organization,
            requested_by=self.user,
            title="Request 1",
            description="Description 1",
            justification="Justification 1"
        )
        request2 = ProcurementRequest.objects.create(
            organization=self.organization,
            requested_by=self.user,
            title="Request 2",
            description="Description 2",
            justification="Justification 2"
        )
        
        self.assertNotEqual(request1.request_number, request2.request_number)
        self.assertTrue(request1.request_number.startswith('REQ'))
        self.assertTrue(request2.request_number.startswith('REQ'))


class SupplierPerformanceModelTest(TestCase):
    """Test cases for SupplierPerformance model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.organization
        )
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            email="supplier@example.com",
            phone="1234567890",
            organization=self.organization
        )
    
    def test_supplier_performance_creation(self):
        """Test creating a supplier performance record."""
        performance = SupplierPerformance.objects.create(
            supplier=self.supplier,
            organization=self.organization,
            evaluated_by=self.user,
            on_time_delivery_rate=Decimal('95.00'),
            quality_rating=Decimal('4.5'),
            communication_rating=Decimal('4.0'),
            price_competitiveness=Decimal('3.5')
        )
        
        self.assertEqual(performance.supplier, self.supplier)
        self.assertEqual(performance.organization, self.organization)
        self.assertEqual(performance.evaluated_by, self.user)
        self.assertEqual(performance.overall_rating, Decimal('4.0'))  # (4.5 + 4.0 + 3.5) / 3
    
    def test_supplier_performance_overall_rating_calculation(self):
        """Test automatic overall rating calculation."""
        performance = SupplierPerformance.objects.create(
            supplier=self.supplier,
            organization=self.organization,
            evaluated_by=self.user,
            quality_rating=Decimal('5.0'),
            communication_rating=Decimal('4.0'),
            price_competitiveness=Decimal('3.0')
        )
        
        expected_rating = (Decimal('5.0') + Decimal('4.0') + Decimal('3.0')) / 3
        self.assertEqual(performance.overall_rating, expected_rating)


class PurchaseOrderAPITest(APITestCase):
    """Test cases for PurchaseOrder API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.organization
        )
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            email="supplier@example.com",
            phone="1234567890",
            organization=self.organization
        )
        self.category = Category.objects.create(
            name="Test Category",
            organization=self.organization
        )
        self.product = Product.objects.create(
            name="Test Product",
            sku="TEST001",
            description="Test product description",
            category=self.category,
            organization=self.organization
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_create_purchase_order(self):
        """Test creating a purchase order via API."""
        url = reverse('purchaseorder-list')
        data = {
            'organization': self.organization.id,
            'supplier': self.supplier.id,
            'status': 'draft',
            'priority': 'medium',
            'notes': 'Test purchase order',
            'items': [
                {
                    'product': self.product.id,
                    'quantity_ordered': 10,
                    'unit_price': '25.00'
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PurchaseOrder.objects.count(), 1)
        
        po = PurchaseOrder.objects.first()
        self.assertEqual(po.supplier, self.supplier)
        self.assertEqual(po.items.count(), 1)
    
    def test_list_purchase_orders(self):
        """Test listing purchase orders via API."""
        # Create a purchase order
        PurchaseOrder.objects.create(
            organization=self.organization,
            supplier=self.supplier,
            requested_by=self.user
        )
        
        url = reverse('purchaseorder-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_retrieve_purchase_order(self):
        """Test retrieving a specific purchase order via API."""
        po = PurchaseOrder.objects.create(
            organization=self.organization,
            supplier=self.supplier,
            requested_by=self.user
        )
        
        url = reverse('purchaseorder-detail', kwargs={'pk': po.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['po_number'], po.po_number)
    
    def test_update_purchase_order_status(self):
        """Test updating purchase order status via API."""
        po = PurchaseOrder.objects.create(
            organization=self.organization,
            supplier=self.supplier,
            requested_by=self.user,
            status='draft'
        )
        
        url = reverse('purchaseorder-update-status', kwargs={'pk': po.pk})
        data = {'status': 'pending_approval'}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        po.refresh_from_db()
        self.assertEqual(po.status, 'pending_approval')
    
    def test_approve_purchase_order(self):
        """Test approving a purchase order via API."""
        po = PurchaseOrder.objects.create(
            organization=self.organization,
            supplier=self.supplier,
            requested_by=self.user,
            status='pending_approval'
        )
        
        url = reverse('purchaseorder-approve', kwargs={'pk': po.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        po.refresh_from_db()
        self.assertEqual(po.status, 'approved')
        self.assertEqual(po.approved_by, self.user)
        self.assertIsNotNone(po.approval_date)
    
    def test_purchase_order_analytics(self):
        """Test purchase order analytics endpoint."""
        # Create some purchase orders
        for i in range(3):
            PurchaseOrder.objects.create(
                organization=self.organization,
                supplier=self.supplier,
                requested_by=self.user,
                total_amount=Decimal('100.00')
            )
        
        url = reverse('purchaseorder-analytics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_orders'], 3)
        self.assertEqual(response.data['total_value'], '300.00')


class ProcurementRequestAPITest(APITestCase):
    """Test cases for ProcurementRequest API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.organization
        )
        self.category = Category.objects.create(
            name="Test Category",
            organization=self.organization
        )
        self.product = Product.objects.create(
            name="Test Product",
            sku="TEST001",
            description="Test product description",
            category=self.category,
            organization=self.organization
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_create_procurement_request(self):
        """Test creating a procurement request via API."""
        url = reverse('procurementrequest-list')
        data = {
            'organization': self.organization.id,
            'title': 'Test Request',
            'description': 'Test description',
            'justification': 'Test justification',
            'status': 'draft',
            'priority': 'medium',
            'items': [
                {
                    'product': self.product.id,
                    'quantity': 5,
                    'estimated_unit_price': '20.00'
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProcurementRequest.objects.count(), 1)
        
        request = ProcurementRequest.objects.first()
        self.assertEqual(request.title, "Test Request")
        self.assertEqual(request.items.count(), 1)
    
    def test_approve_procurement_request(self):
        """Test approving a procurement request via API."""
        request = ProcurementRequest.objects.create(
            organization=self.organization,
            requested_by=self.user,
            title="Test Request",
            description="Test description",
            justification="Test justification",
            status='under_review'
        )
        
        url = reverse('procurementrequest-approve', kwargs={'pk': request.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        request.refresh_from_db()
        self.assertEqual(request.status, 'approved')
        self.assertEqual(request.reviewed_by, self.user)
        self.assertIsNotNone(request.review_date)
    
    def test_reject_procurement_request(self):
        """Test rejecting a procurement request via API."""
        request = ProcurementRequest.objects.create(
            organization=self.organization,
            requested_by=self.user,
            title="Test Request",
            description="Test description",
            justification="Test justification",
            status='under_review'
        )
        
        url = reverse('procurementrequest-reject', kwargs={'pk': request.pk})
        data = {'rejection_reason': 'Not justified'}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        request.refresh_from_db()
        self.assertEqual(request.status, 'rejected')
        self.assertEqual(request.rejection_reason, 'Not justified')


class SupplierPerformanceAPITest(APITestCase):
    """Test cases for SupplierPerformance API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.organization
        )
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            email="supplier@example.com",
            phone="1234567890",
            organization=self.organization
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_create_supplier_performance(self):
        """Test creating a supplier performance record via API."""
        url = reverse('supplierperformance-list')
        data = {
            'supplier': self.supplier.id,
            'organization': self.organization.id,
            'on_time_delivery_rate': '95.00',
            'quality_rating': '4.5',
            'communication_rating': '4.0',
            'price_competitiveness': '3.5',
            'notes': 'Good supplier overall'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SupplierPerformance.objects.count(), 1)
        
        performance = SupplierPerformance.objects.first()
        self.assertEqual(performance.supplier, self.supplier)
        self.assertEqual(performance.overall_rating, Decimal('4.0'))
    
    def test_top_performers_endpoint(self):
        """Test top performers endpoint."""
        # Create some performance records
        for rating in [4.5, 3.5, 4.8]:
            SupplierPerformance.objects.create(
                supplier=self.supplier,
                organization=self.organization,
                evaluated_by=self.user,
                quality_rating=Decimal(str(rating)),
                communication_rating=Decimal('4.0'),
                price_competitiveness=Decimal('3.5')
            )
        
        url = reverse('supplierperformance-top-performers')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)


class PurchaseAnalyticsAPITest(APITestCase):
    """Test cases for PurchaseAnalytics API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.organization
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_analytics_dashboard(self):
        """Test analytics dashboard endpoint."""
        # Create some analytics data
        PurchaseAnalytics.objects.create(
            organization=self.organization,
            period_start=timezone.now() - timedelta(days=30),
            period_end=timezone.now(),
            total_orders=10,
            total_value=Decimal('1000.00'),
            average_order_value=Decimal('100.00')
        )
        
        url = reverse('purchaseanalytics-dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('current_period', response.data)
        self.assertIn('trends', response.data)
        self.assertIn('alerts', response.data)


class PurchasingIntegrationTest(TestCase):
    """Integration tests for purchasing workflow."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.organization
        )
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            email="supplier@example.com",
            phone="1234567890",
            organization=self.organization
        )
        self.category = Category.objects.create(
            name="Test Category",
            organization=self.organization
        )
        self.product = Product.objects.create(
            name="Test Product",
            sku="TEST001",
            description="Test product description",
            category=self.category,
            organization=self.organization
        )
    
    def test_complete_purchasing_workflow(self):
        """Test complete purchasing workflow from request to receipt."""
        # 1. Create procurement request
        request = ProcurementRequest.objects.create(
            organization=self.organization,
            requested_by=self.user,
            title="Test Request",
            description="Test description",
            justification="Test justification"
        )
        
        ProcurementRequestItem.objects.create(
            request=request,
            product=self.product,
            quantity=10,
            estimated_unit_price=Decimal('25.00')
        )
        
        # 2. Approve request
        request.status = 'approved'
        request.reviewed_by = self.user
        request.review_date = timezone.now()
        request.save()
        
        # 3. Create purchase order
        po = PurchaseOrder.objects.create(
            organization=self.organization,
            supplier=self.supplier,
            requested_by=self.user,
            status='approved'
        )
        
        PurchaseOrderItem.objects.create(
            purchase_order=po,
            product=self.product,
            quantity_ordered=10,
            unit_price=Decimal('25.00')
        )
        
        # 4. Create receipt
        receipt = PurchaseReceipt.objects.create(
            purchase_order=po,
            received_by=self.user,
            status='complete'
        )
        
        PurchaseReceiptItem.objects.create(
            receipt=receipt,
            purchase_order_item=po.items.first(),
            quantity_received=10,
            condition='good'
        )
        
        # Verify final state
        po.refresh_from_db()
        self.assertEqual(po.status, 'fully_received')
        
        item = po.items.first()
        self.assertEqual(item.quantity_received, 10)
        self.assertEqual(item.quantity_pending, 0)
    
    def test_supplier_performance_tracking(self):
        """Test supplier performance tracking workflow."""
        # Create purchase orders
        for i in range(5):
            po = PurchaseOrder.objects.create(
                organization=self.organization,
                supplier=self.supplier,
                requested_by=self.user,
                status='fully_received'
            )
        
        # Create performance evaluation
        performance = SupplierPerformance.objects.create(
            supplier=self.supplier,
            organization=self.organization,
            evaluated_by=self.user,
            on_time_delivery_rate=Decimal('90.00'),
            quality_rating=Decimal('4.2'),
            communication_rating=Decimal('4.0'),
            price_competitiveness=Decimal('3.8')
        )
        
        # Verify overall rating calculation
        expected_rating = (Decimal('4.2') + Decimal('4.0') + Decimal('3.8')) / 3
        self.assertEqual(performance.overall_rating, expected_rating)
