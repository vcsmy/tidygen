"""
Inventory management tests.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta

from .models import (
    Product, ProductCategory, StockMovement, Supplier,
    PurchaseOrder, PurchaseOrderItem
)

User = get_user_model()


class InventoryModelsTestCase(TestCase):
    """Test inventory models."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name='Test Organization',
            slug='test-org'
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            organization=self.organization
        )
        
        self.category = ProductCategory.objects.create(
            name='Electronics',
            description='Electronic products',
            organization=self.organization
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            sku='TEST-001',
            description='A test product',
            category=self.category,
            cost_price=Decimal('10.00'),
            selling_price=Decimal('20.00'),
            current_stock=100,
            min_stock_level=10,
            max_stock_level=200,
            organization=self.organization
        )
        
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            contact_person='John Doe',
            email='john@supplier.com',
            phone='123-456-7890',
            organization=self.organization
        )

    def test_product_creation(self):
        """Test product creation."""
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.sku, 'TEST-001')
        self.assertEqual(self.product.current_stock, 100)
        self.assertEqual(self.product.stock_status, 'normal')

    def test_product_low_stock(self):
        """Test product low stock detection."""
        self.product.current_stock = 5
        self.product.save()
        self.assertEqual(self.product.stock_status, 'low_stock')

    def test_product_out_of_stock(self):
        """Test product out of stock detection."""
        self.product.current_stock = 0
        self.product.save()
        self.assertEqual(self.product.stock_status, 'out_of_stock')

    def test_stock_movement(self):
        """Test stock movement creation."""
        movement = StockMovement.objects.create(
            product=self.product,
            movement_type='in',
            quantity=50,
            reference_number='TEST-001',
            notes='Test stock in'
        )
        
        self.assertEqual(movement.product, self.product)
        self.assertEqual(movement.quantity, 50)
        self.assertEqual(movement.movement_type, 'in')

    def test_purchase_order_creation(self):
        """Test purchase order creation."""
        po = PurchaseOrder.objects.create(
            supplier=self.supplier,
            order_number='PO-000001',
            status='draft',
            order_date=date.today(),
            expected_delivery=date.today() + timedelta(days=7),
            organization=self.organization
        )
        
        self.assertEqual(po.supplier, self.supplier)
        self.assertEqual(po.status, 'draft')
        self.assertEqual(po.total_amount, Decimal('0.00'))


class InventoryAPITestCase(APITestCase):
    """Test inventory API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name='Test Organization',
            slug='test-org'
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            organization=self.organization
        )
        
        self.category = ProductCategory.objects.create(
            name='Electronics',
            description='Electronic products',
            organization=self.organization
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            sku='TEST-001',
            description='A test product',
            category=self.category,
            cost_price=Decimal('10.00'),
            selling_price=Decimal('20.00'),
            current_stock=100,
            min_stock_level=10,
            max_stock_level=200,
            organization=self.organization
        )
        
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            contact_person='John Doe',
            email='john@supplier.com',
            phone='123-456-7890',
            organization=self.organization
        )
        
        self.client.force_authenticate(user=self.user)

    def test_product_list(self):
        """Test product list endpoint."""
        url = reverse('product-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Product')

    def test_product_detail(self):
        """Test product detail endpoint."""
        url = reverse('product-detail', args=[self.product.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product')
        self.assertEqual(response.data['sku'], 'TEST-001')

    def test_product_create(self):
        """Test product creation endpoint."""
        url = reverse('product-list')
        data = {
            'name': 'New Product',
            'sku': 'NEW-001',
            'description': 'A new product',
            'category': self.category.id,
            'cost_price': '15.00',
            'selling_price': '30.00',
            'current_stock': 50,
            'min_stock_level': 5,
            'max_stock_level': 150
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_product_stock_adjustment(self):
        """Test product stock adjustment endpoint."""
        url = reverse('product-adjust-stock', args=[self.product.id])
        data = {
            'quantity': 25,
            'movement_type': 'out',
            'notes': 'Test stock out',
            'reference_number': 'TEST-OUT-001'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if stock was updated
        self.product.refresh_from_db()
        self.assertEqual(self.product.current_stock, 75)
        
        # Check if movement was created
        movement = StockMovement.objects.last()
        self.assertEqual(movement.quantity, 25)
        self.assertEqual(movement.movement_type, 'out')

    def test_category_list(self):
        """Test category list endpoint."""
        url = reverse('product-category-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Electronics')

    def test_category_tree(self):
        """Test category tree endpoint."""
        # Create child category
        child_category = ProductCategory.objects.create(
            name='Smartphones',
            description='Smartphone products',
            parent=self.category,
            organization=self.organization
        )
        
        url = reverse('product-category-tree')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data[0]['children']), 1)
        self.assertEqual(response.data[0]['children'][0]['name'], 'Smartphones')

    def test_supplier_list(self):
        """Test supplier list endpoint."""
        url = reverse('supplier-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Supplier')

    def test_supplier_performance(self):
        """Test supplier performance endpoint."""
        # Create a purchase order
        po = PurchaseOrder.objects.create(
            supplier=self.supplier,
            order_number='PO-000001',
            status='received',
            order_date=date.today(),
            organization=self.organization,
            total_amount=Decimal('100.00')
        )
        
        url = reverse('supplier-performance', args=[self.supplier.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_orders'], 1)
        self.assertEqual(response.data['received_orders'], 1)
        self.assertEqual(float(response.data['total_spent']), 100.00)

    def test_purchase_order_create(self):
        """Test purchase order creation endpoint."""
        url = reverse('purchase-order-list')
        data = {
            'supplier': self.supplier.id,
            'order_date': date.today().isoformat(),
            'expected_delivery': (date.today() + timedelta(days=7)).isoformat(),
            'notes': 'Test purchase order'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PurchaseOrder.objects.count(), 1)
        
        # Check if order number was generated
        po = PurchaseOrder.objects.first()
        self.assertTrue(po.order_number.startswith('PO-'))

    def test_inventory_dashboard_summary(self):
        """Test inventory dashboard summary endpoint."""
        url = reverse('inventory-dashboard-summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_products'], 1)
        self.assertEqual(response.data['total_categories'], 1)
        self.assertEqual(response.data['total_suppliers'], 1)
        self.assertEqual(float(response.data['total_stock_value']), 1000.00)  # 100 * 10.00

    def test_stock_alerts(self):
        """Test stock alerts endpoint."""
        # Create a low stock product
        low_stock_product = Product.objects.create(
            name='Low Stock Product',
            sku='LOW-001',
            category=self.category,
            cost_price=Decimal('5.00'),
            selling_price=Decimal('10.00'),
            current_stock=5,
            min_stock_level=10,
            max_stock_level=100,
            organization=self.organization
        )
        
        url = reverse('inventory-dashboard-stock-alerts')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['product_name'], 'Low Stock Product')
        self.assertEqual(response.data[0]['alert_type'], 'low_stock')

    def test_stock_movement_summary(self):
        """Test stock movement summary endpoint."""
        # Create some stock movements
        StockMovement.objects.create(
            product=self.product,
            movement_type='in',
            quantity=50,
            reference_number='TEST-IN-001'
        )
        
        StockMovement.objects.create(
            product=self.product,
            movement_type='out',
            quantity=25,
            reference_number='TEST-OUT-001'
        )
        
        url = reverse('stock-movement-summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_movements'], 2)
        self.assertEqual(response.data['stock_in'], 50)
        self.assertEqual(response.data['stock_out'], 25)

    def test_unauthorized_access(self):
        """Test unauthorized access to endpoints."""
        self.client.force_authenticate(user=None)
        
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_organization_isolation(self):
        """Test that users can only access their organization's data."""
        # Create another organization and product
        other_org = Organization.objects.create(
            name='Other Organization',
            slug='other-org'
        )
        
        other_product = Product.objects.create(
            name='Other Product',
            sku='OTHER-001',
            category=self.category,
            cost_price=Decimal('20.00'),
            selling_price=Decimal('40.00'),
            organization=other_org
        )
        
        url = reverse('product-list')
        response = self.client.get(url)
        
        # Should only see products from user's organization
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['organization'], self.organization.id)
