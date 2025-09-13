"""
Comprehensive tests for finance management functionality.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta

from apps.finance.models import (
    Account, Customer, Vendor, Invoice, InvoiceItem, Payment, Expense,
    Budget, BudgetItem, FinancialReport, TaxRate, RecurringInvoice, RecurringInvoiceItem
)

User = get_user_model()


class FinanceModelTests(TestCase):
    """Test finance models."""
    
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
    
    def test_account_creation(self):
        """Test account creation."""
        account = Account.objects.create(
            organization=self.organization,
            name="Test Account",
            code="1000",
            account_type="asset",
            balance=Decimal('1000.00')
        )
        self.assertEqual(account.name, "Test Account")
        self.assertEqual(account.code, "1000")
        self.assertEqual(account.account_type, "asset")
        self.assertEqual(account.balance, Decimal('1000.00'))
    
    def test_customer_creation(self):
        """Test customer creation."""
        customer = Customer.objects.create(
            organization=self.organization,
            name="Test Customer",
            email="customer@example.com",
            credit_limit=Decimal('5000.00')
        )
        self.assertEqual(customer.name, "Test Customer")
        self.assertEqual(customer.email, "customer@example.com")
        self.assertEqual(customer.credit_limit, Decimal('5000.00'))
    
    def test_invoice_creation(self):
        """Test invoice creation."""
        customer = Customer.objects.create(
            organization=self.organization,
            name="Test Customer"
        )
        invoice = Invoice.objects.create(
            organization=self.organization,
            customer=customer,
            invoice_number="INV-001",
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            subtotal=Decimal('100.00'),
            tax_rate=Decimal('10.00'),
            total_amount=Decimal('110.00'),
            created_by=self.user
        )
        self.assertEqual(invoice.invoice_number, "INV-001")
        self.assertEqual(invoice.customer, customer)
        self.assertEqual(invoice.total_amount, Decimal('110.00'))
    
    def test_invoice_item_creation(self):
        """Test invoice item creation."""
        customer = Customer.objects.create(
            organization=self.organization,
            name="Test Customer"
        )
        invoice = Invoice.objects.create(
            organization=self.organization,
            customer=customer,
            invoice_number="INV-001",
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            created_by=self.user
        )
        item = InvoiceItem.objects.create(
            invoice=invoice,
            description="Test Item",
            quantity=Decimal('2.00'),
            unit_price=Decimal('50.00'),
            total_price=Decimal('100.00')
        )
        self.assertEqual(item.description, "Test Item")
        self.assertEqual(item.quantity, Decimal('2.00'))
        self.assertEqual(item.unit_price, Decimal('50.00'))
        self.assertEqual(item.total_price, Decimal('100.00'))
    
    def test_payment_creation(self):
        """Test payment creation."""
        customer = Customer.objects.create(
            organization=self.organization,
            name="Test Customer"
        )
        invoice = Invoice.objects.create(
            organization=self.organization,
            customer=customer,
            invoice_number="INV-001",
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            total_amount=Decimal('110.00'),
            created_by=self.user
        )
        payment = Payment.objects.create(
            organization=self.organization,
            invoice=invoice,
            customer=customer,
            payment_number="PAY-001",
            amount=Decimal('110.00'),
            payment_method="bank_transfer",
            payment_date=date.today(),
            received_by=self.user
        )
        self.assertEqual(payment.payment_number, "PAY-001")
        self.assertEqual(payment.amount, Decimal('110.00'))
        self.assertEqual(payment.payment_method, "bank_transfer")
    
    def test_expense_creation(self):
        """Test expense creation."""
        vendor = Vendor.objects.create(
            organization=self.organization,
            name="Test Vendor"
        )
        expense = Expense.objects.create(
            organization=self.organization,
            vendor=vendor,
            category="office_supplies",
            amount=Decimal('50.00'),
            total_amount=Decimal('50.00'),
            description="Test Expense",
            expense_date=date.today(),
            submitted_by=self.user
        )
        self.assertEqual(expense.description, "Test Expense")
        self.assertEqual(expense.amount, Decimal('50.00'))
        self.assertEqual(expense.category, "office_supplies")
    
    def test_budget_creation(self):
        """Test budget creation."""
        budget = Budget.objects.create(
            organization=self.organization,
            name="Test Budget",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            total_budget=Decimal('10000.00')
        )
        self.assertEqual(budget.name, "Test Budget")
        self.assertEqual(budget.total_budget, Decimal('10000.00'))
    
    def test_tax_rate_creation(self):
        """Test tax rate creation."""
        tax_rate = TaxRate.objects.create(
            organization=self.organization,
            name="VAT",
            rate=Decimal('20.00')
        )
        self.assertEqual(tax_rate.name, "VAT")
        self.assertEqual(tax_rate.rate, Decimal('20.00'))


class FinanceAPITests(APITestCase):
    """Test finance API endpoints."""
    
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
    
    def test_account_list(self):
        """Test account list endpoint."""
        Account.objects.create(
            organization=self.organization,
            name="Test Account",
            code="1000",
            account_type="asset"
        )
        url = reverse('account-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_account_create(self):
        """Test account creation endpoint."""
        url = reverse('account-list')
        data = {
            'name': 'New Account',
            'code': '2000',
            'account_type': 'liability',
            'description': 'Test account'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Account.objects.count(), 1)
    
    def test_customer_list(self):
        """Test customer list endpoint."""
        Customer.objects.create(
            organization=self.organization,
            name="Test Customer",
            email="customer@example.com"
        )
        url = reverse('customer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_customer_create(self):
        """Test customer creation endpoint."""
        url = reverse('customer-list')
        data = {
            'name': 'New Customer',
            'email': 'newcustomer@example.com',
            'phone': '+1234567890',
            'credit_limit': '5000.00'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 1)
    
    def test_invoice_list(self):
        """Test invoice list endpoint."""
        customer = Customer.objects.create(
            organization=self.organization,
            name="Test Customer"
        )
        Invoice.objects.create(
            organization=self.organization,
            customer=customer,
            invoice_number="INV-001",
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            total_amount=Decimal('100.00'),
            created_by=self.user
        )
        url = reverse('invoice-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_invoice_create(self):
        """Test invoice creation endpoint."""
        customer = Customer.objects.create(
            organization=self.organization,
            name="Test Customer"
        )
        url = reverse('invoice-list')
        data = {
            'customer': customer.id,
            'issue_date': date.today().isoformat(),
            'due_date': (date.today() + timedelta(days=30)).isoformat(),
            'subtotal': '100.00',
            'tax_rate': '10.00',
            'total_amount': '110.00'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Invoice.objects.count(), 1)
    
    def test_payment_list(self):
        """Test payment list endpoint."""
        customer = Customer.objects.create(
            organization=self.organization,
            name="Test Customer"
        )
        Payment.objects.create(
            organization=self.organization,
            customer=customer,
            payment_number="PAY-001",
            amount=Decimal('100.00'),
            payment_method="bank_transfer",
            payment_date=date.today(),
            received_by=self.user
        )
        url = reverse('payment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_payment_create(self):
        """Test payment creation endpoint."""
        customer = Customer.objects.create(
            organization=self.organization,
            name="Test Customer"
        )
        url = reverse('payment-list')
        data = {
            'customer': customer.id,
            'amount': '100.00',
            'payment_method': 'bank_transfer',
            'payment_date': date.today().isoformat()
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), 1)
    
    def test_expense_list(self):
        """Test expense list endpoint."""
        Expense.objects.create(
            organization=self.organization,
            category="office_supplies",
            amount=Decimal('50.00'),
            total_amount=Decimal('50.00'),
            description="Test Expense",
            expense_date=date.today(),
            submitted_by=self.user
        )
        url = reverse('expense-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_expense_create(self):
        """Test expense creation endpoint."""
        url = reverse('expense-list')
        data = {
            'category': 'office_supplies',
            'amount': '50.00',
            'description': 'Test Expense',
            'expense_date': date.today().isoformat()
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Expense.objects.count(), 1)
    
    def test_budget_list(self):
        """Test budget list endpoint."""
        Budget.objects.create(
            organization=self.organization,
            name="Test Budget",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            total_budget=Decimal('10000.00')
        )
        url = reverse('budget-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_budget_create(self):
        """Test budget creation endpoint."""
        url = reverse('budget-list')
        data = {
            'name': 'New Budget',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=365)).isoformat(),
            'total_budget': '10000.00'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Budget.objects.count(), 1)
    
    def test_tax_rate_list(self):
        """Test tax rate list endpoint."""
        TaxRate.objects.create(
            organization=self.organization,
            name="VAT",
            rate=Decimal('20.00')
        )
        url = reverse('taxrate-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_tax_rate_create(self):
        """Test tax rate creation endpoint."""
        url = reverse('taxrate-list')
        data = {
            'name': 'Sales Tax',
            'rate': '8.25',
            'description': 'State sales tax'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TaxRate.objects.count(), 1)
    
    def test_finance_dashboard(self):
        """Test finance dashboard endpoint."""
        url = reverse('finance-dashboard-overview')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_revenue', response.data)
        self.assertIn('total_expenses', response.data)
        self.assertIn('net_profit', response.data)
    
    def test_invoice_analytics(self):
        """Test invoice analytics endpoint."""
        customer = Customer.objects.create(
            organization=self.organization,
            name="Test Customer"
        )
        Invoice.objects.create(
            organization=self.organization,
            customer=customer,
            invoice_number="INV-001",
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            total_amount=Decimal('100.00'),
            created_by=self.user
        )
        url = reverse('invoice-analytics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_invoices', response.data)
        self.assertIn('total_revenue', response.data)
    
    def test_expense_analytics(self):
        """Test expense analytics endpoint."""
        Expense.objects.create(
            organization=self.organization,
            category="office_supplies",
            amount=Decimal('50.00'),
            total_amount=Decimal('50.00'),
            description="Test Expense",
            expense_date=date.today(),
            submitted_by=self.user
        )
        url = reverse('expense-analytics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_expenses', response.data)
        self.assertIn('total_amount', response.data)


class FinanceSignalTests(TestCase):
    """Test finance signals."""
    
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
    
    def test_invoice_item_signal(self):
        """Test invoice item signal updates invoice totals."""
        customer = Customer.objects.create(
            organization=self.organization,
            name="Test Customer"
        )
        invoice = Invoice.objects.create(
            organization=self.organization,
            customer=customer,
            invoice_number="INV-001",
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            tax_rate=Decimal('10.00'),
            created_by=self.user
        )
        
        # Create invoice item
        InvoiceItem.objects.create(
            invoice=invoice,
            description="Test Item",
            quantity=Decimal('2.00'),
            unit_price=Decimal('50.00'),
            total_price=Decimal('100.00')
        )
        
        # Refresh invoice from database
        invoice.refresh_from_db()
        
        # Check if totals were updated
        self.assertEqual(invoice.subtotal, Decimal('100.00'))
        self.assertEqual(invoice.tax_amount, Decimal('10.00'))
        self.assertEqual(invoice.total_amount, Decimal('110.00'))
    
    def test_payment_signal(self):
        """Test payment signal updates invoice paid amount."""
        customer = Customer.objects.create(
            organization=self.organization,
            name="Test Customer"
        )
        invoice = Invoice.objects.create(
            organization=self.organization,
            customer=customer,
            invoice_number="INV-001",
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            total_amount=Decimal('110.00'),
            created_by=self.user
        )
        
        # Create payment
        Payment.objects.create(
            organization=self.organization,
            invoice=invoice,
            customer=customer,
            payment_number="PAY-001",
            amount=Decimal('110.00'),
            payment_method="bank_transfer",
            payment_date=date.today(),
            received_by=self.user
        )
        
        # Refresh invoice from database
        invoice.refresh_from_db()
        
        # Check if paid amount was updated
        self.assertEqual(invoice.paid_amount, Decimal('110.00'))
        self.assertEqual(invoice.status, 'paid')
    
    def test_expense_signal(self):
        """Test expense signal calculates total amount."""
        expense = Expense.objects.create(
            organization=self.organization,
            category="office_supplies",
            amount=Decimal('50.00'),
            tax_amount=Decimal('5.00'),
            description="Test Expense",
            expense_date=date.today(),
            submitted_by=self.user
        )
        
        # Check if total amount was calculated
        self.assertEqual(expense.total_amount, Decimal('55.00'))


class FinanceFilterTests(TestCase):
    """Test finance filters."""
    
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
    
    def test_customer_filter(self):
        """Test customer filtering."""
        Customer.objects.create(
            organization=self.organization,
            name="Test Customer 1",
            email="customer1@example.com",
            city="New York"
        )
        Customer.objects.create(
            organization=self.organization,
            name="Test Customer 2",
            email="customer2@example.com",
            city="Los Angeles"
        )
        
        # Test name filter
        from apps.finance.filters import CustomerFilter
        filter_data = {'name': 'Test Customer 1'}
        filtered_customers = CustomerFilter(filter_data, queryset=Customer.objects.all()).qs
        self.assertEqual(filtered_customers.count(), 1)
        
        # Test city filter
        filter_data = {'city': 'New York'}
        filtered_customers = CustomerFilter(filter_data, queryset=Customer.objects.all()).qs
        self.assertEqual(filtered_customers.count(), 1)
    
    def test_invoice_filter(self):
        """Test invoice filtering."""
        customer = Customer.objects.create(
            organization=self.organization,
            name="Test Customer"
        )
        Invoice.objects.create(
            organization=self.organization,
            customer=customer,
            invoice_number="INV-001",
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            status="draft",
            total_amount=Decimal('100.00'),
            created_by=self.user
        )
        Invoice.objects.create(
            organization=self.organization,
            customer=customer,
            invoice_number="INV-002",
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            status="sent",
            total_amount=Decimal('200.00'),
            created_by=self.user
        )
        
        # Test status filter
        from apps.finance.filters import InvoiceFilter
        filter_data = {'status': 'draft'}
        filtered_invoices = InvoiceFilter(filter_data, queryset=Invoice.objects.all()).qs
        self.assertEqual(filtered_invoices.count(), 1)
        
        # Test amount filter
        filter_data = {'total_amount_min': '150.00'}
        filtered_invoices = InvoiceFilter(filter_data, queryset=Invoice.objects.all()).qs
        self.assertEqual(filtered_invoices.count(), 1)
