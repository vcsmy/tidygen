"""
Finance management serializers for iNEAT ERP platform.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.finance.models import (
    Account, Customer, Vendor, Invoice, InvoiceItem, Payment, Expense,
    Budget, BudgetItem, FinancialReport, TaxRate, RecurringInvoice, RecurringInvoiceItem
)

User = get_user_model()


class AccountSerializer(serializers.ModelSerializer):
    """Serializer for Account model."""
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = Account
        fields = [
            'id', 'name', 'code', 'account_type', 'account_type_display',
            'parent', 'parent_name', 'description', 'is_active', 'balance',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model."""
    total_invoices = serializers.SerializerMethodField()
    total_paid = serializers.SerializerMethodField()
    outstanding_balance = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'email', 'phone', 'address_line1', 'address_line2',
            'city', 'state', 'postal_code', 'country', 'credit_limit',
            'payment_terms', 'tax_id', 'is_active', 'total_invoices',
            'total_paid', 'outstanding_balance', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']
    
    def get_total_invoices(self, obj):
        return obj.invoices.count()
    
    def get_total_paid(self, obj):
        return sum(payment.amount for payment in obj.payments.all())
    
    def get_outstanding_balance(self, obj):
        total_invoiced = sum(invoice.total_amount for invoice in obj.invoices.all())
        total_paid = sum(payment.amount for payment in obj.payments.all())
        return total_invoiced - total_paid


class VendorSerializer(serializers.ModelSerializer):
    """Serializer for Vendor model."""
    total_expenses = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Vendor
        fields = [
            'id', 'name', 'contact_person', 'email', 'phone', 'address_line1',
            'address_line2', 'city', 'state', 'postal_code', 'country',
            'payment_terms', 'tax_id', 'is_active', 'total_expenses',
            'total_amount', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']
    
    def get_total_expenses(self, obj):
        return obj.expenses.count()
    
    def get_total_amount(self, obj):
        return sum(expense.total_amount for expense in obj.expenses.all())


class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer for InvoiceItem model."""
    
    class Meta:
        model = InvoiceItem
        fields = [
            'id', 'description', 'quantity', 'unit_price', 'total_price',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice model."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    balance_due = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'customer', 'customer_name', 'invoice_number', 'status',
            'status_display', 'issue_date', 'due_date', 'sent_date', 'paid_date',
            'subtotal', 'tax_rate', 'tax_amount', 'discount_amount', 'total_amount',
            'paid_amount', 'balance_due', 'is_overdue', 'notes', 'terms_conditions',
            'created_by', 'created_by_name', 'items', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified', 'paid_amount']
    
    def create(self, validated_data):
        # Auto-generate invoice number if not provided
        if not validated_data.get('invoice_number'):
            validated_data['invoice_number'] = self._generate_invoice_number()
        
        # Calculate totals
        invoice = super().create(validated_data)
        self._calculate_totals(invoice)
        return invoice
    
    def update(self, instance, validated_data):
        invoice = super().update(instance, validated_data)
        self._calculate_totals(invoice)
        return invoice
    
    def _generate_invoice_number(self):
        """Generate unique invoice number."""
        from django.utils import timezone
        year = timezone.now().year
        month = timezone.now().month
        
        # Get the last invoice number for this year/month
        last_invoice = Invoice.objects.filter(
            invoice_number__startswith=f"INV-{year}{month:02d}"
        ).order_by('-invoice_number').first()
        
        if last_invoice:
            try:
                last_number = int(last_invoice.invoice_number.split('-')[-1])
                next_number = last_number + 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1
        
        return f"INV-{year}{month:02d}{next_number:04d}"
    
    def _calculate_totals(self, invoice):
        """Calculate invoice totals."""
        # Calculate subtotal from items
        subtotal = sum(item.total_price for item in invoice.items.all())
        invoice.subtotal = subtotal
        
        # Calculate tax amount
        tax_amount = (subtotal * invoice.tax_rate) / 100
        invoice.tax_amount = tax_amount
        
        # Calculate total amount
        invoice.total_amount = subtotal + tax_amount - invoice.discount_amount
        invoice.save()


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    received_by_name = serializers.CharField(source='received_by.get_full_name', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'invoice', 'invoice_number', 'customer', 'customer_name',
            'payment_number', 'amount', 'payment_method', 'payment_method_display',
            'payment_date', 'reference_number', 'notes', 'bank_name', 'account_number',
            'received_by', 'received_by_name', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']
    
    def create(self, validated_data):
        # Auto-generate payment number if not provided
        if not validated_data.get('payment_number'):
            validated_data['payment_number'] = self._generate_payment_number()
        
        payment = super().create(validated_data)
        
        # Update invoice paid amount
        if payment.invoice:
            payment.invoice.paid_amount += payment.amount
            payment.invoice.save()
        
        return payment
    
    def _generate_payment_number(self):
        """Generate unique payment number."""
        from django.utils import timezone
        year = timezone.now().year
        month = timezone.now().month
        
        # Get the last payment number for this year/month
        last_payment = Payment.objects.filter(
            payment_number__startswith=f"PAY-{year}{month:02d}"
        ).order_by('-payment_number').first()
        
        if last_payment:
            try:
                last_number = int(last_payment.payment_number.split('-')[-1])
                next_number = last_number + 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1
        
        return f"PAY-{year}{month:02d}{next_number:04d}"


class ExpenseSerializer(serializers.ModelSerializer):
    """Serializer for Expense model."""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    submitted_by_name = serializers.CharField(source='submitted_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = Expense
        fields = [
            'id', 'vendor', 'vendor_name', 'category', 'category_display',
            'status', 'status_display', 'amount', 'tax_amount', 'total_amount',
            'description', 'expense_date', 'receipt_number', 'receipt_image',
            'submitted_by', 'submitted_by_name', 'approved_by', 'approved_by_name',
            'approved_at', 'rejection_reason', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified', 'approved_by', 'approved_at']
    
    def create(self, validated_data):
        expense = super().create(validated_data)
        # Calculate total amount
        expense.total_amount = expense.amount + expense.tax_amount
        expense.save()
        return expense


class BudgetItemSerializer(serializers.ModelSerializer):
    """Serializer for BudgetItem model."""
    remaining_amount = serializers.SerializerMethodField()
    spent_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = BudgetItem
        fields = [
            'id', 'category', 'description', 'budgeted_amount', 'spent_amount',
            'remaining_amount', 'spent_percentage', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']
    
    def get_remaining_amount(self, obj):
        return obj.budgeted_amount - obj.spent_amount
    
    def get_spent_percentage(self, obj):
        if obj.budgeted_amount > 0:
            return (obj.spent_amount / obj.budgeted_amount) * 100
        return 0


class BudgetSerializer(serializers.ModelSerializer):
    """Serializer for Budget model."""
    items = BudgetItemSerializer(many=True, read_only=True)
    remaining_budget = serializers.ReadOnlyField()
    spent_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Budget
        fields = [
            'id', 'name', 'description', 'start_date', 'end_date',
            'total_budget', 'spent_amount', 'remaining_budget', 'spent_percentage',
            'is_active', 'items', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class TaxRateSerializer(serializers.ModelSerializer):
    """Serializer for TaxRate model."""
    
    class Meta:
        model = TaxRate
        fields = [
            'id', 'name', 'rate', 'description', 'is_active',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class RecurringInvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer for RecurringInvoiceItem model."""
    
    class Meta:
        model = RecurringInvoiceItem
        fields = [
            'id', 'description', 'quantity', 'unit_price', 'total_price',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class RecurringInvoiceSerializer(serializers.ModelSerializer):
    """Serializer for RecurringInvoice model."""
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    items = RecurringInvoiceItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = RecurringInvoice
        fields = [
            'id', 'customer', 'customer_name', 'name', 'description',
            'frequency', 'frequency_display', 'interval', 'start_date',
            'end_date', 'subtotal', 'tax_rate', 'total_amount', 'is_active',
            'last_generated', 'next_generation', 'items', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified', 'last_generated', 'next_generation']


class FinancialReportSerializer(serializers.ModelSerializer):
    """Serializer for FinancialReport model."""
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)
    
    class Meta:
        model = FinancialReport
        fields = [
            'id', 'report_type', 'report_type_display', 'name', 'start_date',
            'end_date', 'report_data', 'generated_by', 'generated_by_name',
            'generated_at', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified', 'generated_at']


# Dashboard and Analytics Serializers
class FinanceDashboardSerializer(serializers.Serializer):
    """Serializer for finance dashboard data."""
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=15, decimal_places=2)
    net_profit = serializers.DecimalField(max_digits=15, decimal_places=2)
    outstanding_invoices = serializers.DecimalField(max_digits=15, decimal_places=2)
    overdue_invoices = serializers.DecimalField(max_digits=15, decimal_places=2)
    pending_expenses = serializers.DecimalField(max_digits=15, decimal_places=2)
    monthly_revenue = serializers.ListField(child=serializers.DictField())
    monthly_expenses = serializers.ListField(child=serializers.DictField())
    top_customers = serializers.ListField(child=serializers.DictField())
    expense_categories = serializers.ListField(child=serializers.DictField())


class InvoiceAnalyticsSerializer(serializers.Serializer):
    """Serializer for invoice analytics."""
    total_invoices = serializers.IntegerField()
    paid_invoices = serializers.IntegerField()
    overdue_invoices = serializers.IntegerField()
    draft_invoices = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_invoice_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    payment_trends = serializers.ListField(child=serializers.DictField())


class ExpenseAnalyticsSerializer(serializers.Serializer):
    """Serializer for expense analytics."""
    total_expenses = serializers.IntegerField()
    approved_expenses = serializers.IntegerField()
    pending_expenses = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_expense_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    category_breakdown = serializers.ListField(child=serializers.DictField())
    monthly_trends = serializers.ListField(child=serializers.DictField())
