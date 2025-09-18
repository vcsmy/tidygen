"""
Purchasing Management Models

This module contains all the models for the purchasing management system,
including purchase orders, suppliers, procurement workflows, and analytics.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from apps.core.models import BaseModel
from apps.inventory.models import Product, Supplier
from decimal import Decimal
import uuid

User = get_user_model()


class PurchaseOrder(BaseModel):
    """
    Purchase Order model for managing procurement requests.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('sent', 'Sent to Supplier'),
        ('partially_received', 'Partially Received'),
        ('fully_received', 'Fully Received'),
        ('cancelled', 'Cancelled'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    po_number = models.CharField(max_length=50, unique=True, help_text="Unique purchase order number")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchasing_orders')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_purchase_orders')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_purchase_orders')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Dates
    order_date = models.DateTimeField(auto_now_add=True)
    expected_delivery_date = models.DateTimeField(null=True, blank=True)
    actual_delivery_date = models.DateTimeField(null=True, blank=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    
    # Financial
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Additional fields
    notes = models.TextField(blank=True, help_text="Internal notes about this purchase order")
    supplier_notes = models.TextField(blank=True, help_text="Notes to be sent to supplier")
    terms_conditions = models.TextField(blank=True, help_text="Terms and conditions")
    
    # Tracking
    reference_number = models.CharField(max_length=100, blank=True, help_text="External reference number")
    tracking_number = models.CharField(max_length=100, blank=True, help_text="Shipping tracking number")
    
    class Meta:
        ordering = ['-created']
        verbose_name = "Purchase Order"
        verbose_name_plural = "Purchase Orders"
    
    def __str__(self):
        return f"PO-{self.po_number} - {self.supplier.name}"
    
    def save(self, *args, **kwargs):
        if not self.po_number:
            self.po_number = self.generate_po_number()
        super().save(*args, **kwargs)
    
    def generate_po_number(self):
        """Generate a unique purchase order number."""
        import datetime
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        count = PurchaseOrder.objects.filter(
            created_at__year=year,
            created_at__month=month
        ).count() + 1
        return f"PO{year}{month:02d}{count:04d}"


class PurchaseOrderItem(BaseModel):
    """
    Individual items within a purchase order.
    """
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchase_order_items')
    
    quantity_ordered = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    quantity_received = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    quantity_pending = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Product details at time of order (for historical accuracy)
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=100)
    product_description = models.TextField(blank=True)
    
    # Additional fields
    notes = models.TextField(blank=True)
    expected_delivery_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['created']
        verbose_name = "Purchase Order Item"
        verbose_name_plural = "Purchase Order Items"
    
    def __str__(self):
        return f"{self.product_name} - {self.quantity_ordered} units"
    
    def save(self, *args, **kwargs):
        # Store product details at time of order
        if self.product:
            self.product_name = self.product.name
            self.product_sku = self.product.sku
            self.product_description = self.product.description
        
        # Calculate total price
        self.total_price = self.quantity_ordered * self.unit_price
        
        # Calculate pending quantity
        self.quantity_pending = self.quantity_ordered - self.quantity_received
        
        super().save(*args, **kwargs)


class PurchaseReceipt(BaseModel):
    """
    Receipt of goods for purchase orders.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('complete', 'Complete'),
        ('discrepancy', 'Discrepancy'),
    ]
    
    receipt_number = models.CharField(max_length=50, unique=True, help_text="Unique receipt number")
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='receipts')
    received_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchase_receipts')
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    receipt_date = models.DateTimeField(auto_now_add=True)
    
    # Additional fields
    notes = models.TextField(blank=True)
    condition_notes = models.TextField(blank=True, help_text="Notes about the condition of received items")
    
    class Meta:
        ordering = ['-receipt_date']
        verbose_name = "Purchase Receipt"
        verbose_name_plural = "Purchase Receipts"
    
    def __str__(self):
        return f"Receipt-{self.receipt_number} for PO-{self.purchase_order.po_number}"
    
    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = self.generate_receipt_number()
        super().save(*args, **kwargs)
    
    def generate_receipt_number(self):
        """Generate a unique receipt number."""
        import datetime
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        count = PurchaseReceipt.objects.filter(
            receipt_date__year=year,
            receipt_date__month=month
        ).count() + 1
        return f"REC{year}{month:02d}{count:04d}"


class PurchaseReceiptItem(BaseModel):
    """
    Individual items within a purchase receipt.
    """
    receipt = models.ForeignKey(PurchaseReceipt, on_delete=models.CASCADE, related_name='items')
    purchase_order_item = models.ForeignKey(PurchaseOrderItem, on_delete=models.CASCADE, related_name='receipt_items')
    
    quantity_received = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    condition = models.CharField(max_length=50, default='good', help_text="Condition of received items")
    
    # Additional fields
    notes = models.TextField(blank=True)
    batch_number = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['created']
        verbose_name = "Purchase Receipt Item"
        verbose_name_plural = "Purchase Receipt Items"
    
    def __str__(self):
        return f"{self.purchase_order_item.product_name} - {self.quantity_received} units"


class ProcurementRequest(BaseModel):
    """
    Internal procurement requests before creating purchase orders.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('converted', 'Converted to PO'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    request_number = models.CharField(max_length=50, unique=True, help_text="Unique request number")
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='procurement_requests')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_procurement_requests')
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Dates
    request_date = models.DateTimeField(auto_now_add=True)
    required_date = models.DateTimeField(null=True, blank=True)
    review_date = models.DateTimeField(null=True, blank=True)
    
    # Details
    title = models.CharField(max_length=200)
    description = models.TextField()
    justification = models.TextField(help_text="Business justification for this request")
    
    # Financial
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    budget_code = models.CharField(max_length=100, blank=True)
    
    # Additional fields
    notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-request_date']
        verbose_name = "Procurement Request"
        verbose_name_plural = "Procurement Requests"
    
    def __str__(self):
        return f"REQ-{self.request_number} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.request_number:
            self.request_number = self.generate_request_number()
        super().save(*args, **kwargs)
    
    def generate_request_number(self):
        """Generate a unique request number."""
        import datetime
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        count = ProcurementRequest.objects.filter(
            request_date__year=year,
            request_date__month=month
        ).count() + 1
        return f"REQ{year}{month:02d}{count:04d}"


class ProcurementRequestItem(BaseModel):
    """
    Individual items within a procurement request.
    """
    request = models.ForeignKey(ProcurementRequest, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='procurement_request_items')
    
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    estimated_unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_total_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Product details at time of request
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=100)
    product_description = models.TextField(blank=True)
    
    # Additional fields
    notes = models.TextField(blank=True)
    specifications = models.TextField(blank=True, help_text="Technical specifications or requirements")
    
    class Meta:
        ordering = ['created']
        verbose_name = "Procurement Request Item"
        verbose_name_plural = "Procurement Request Items"
    
    def __str__(self):
        return f"{self.product_name} - {self.quantity} units"
    
    def save(self, *args, **kwargs):
        # Store product details at time of request
        if self.product:
            self.product_name = self.product.name
            self.product_sku = self.product.sku
            self.product_description = self.product.description
        
        # Calculate estimated total price
        if self.estimated_unit_price:
            self.estimated_total_price = self.quantity * self.estimated_unit_price
        
        super().save(*args, **kwargs)


class SupplierPerformance(BaseModel):
    """
    Track supplier performance metrics.
    """
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='performance_records')
    
    # Performance metrics
    on_time_delivery_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), 
                                               validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))])
    quality_rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'),
                                        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('5.00'))])
    communication_rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'),
                                              validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('5.00'))])
    price_competitiveness = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'),
                                               validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('5.00'))])
    
    # Overall rating
    overall_rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'),
                                        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('5.00'))])
    
    # Additional fields
    notes = models.TextField(blank=True)
    evaluation_date = models.DateTimeField(auto_now_add=True)
    evaluated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='supplier_evaluations')
    
    class Meta:
        ordering = ['-evaluation_date']
        verbose_name = "Supplier Performance"
        verbose_name_plural = "Supplier Performance Records"
    
    def __str__(self):
        return f"{self.supplier.name} - {self.overall_rating}/5.0"
    
    def save(self, *args, **kwargs):
        # Calculate overall rating
        ratings = [
            self.quality_rating,
            self.communication_rating,
            self.price_competitiveness
        ]
        self.overall_rating = sum(ratings) / len(ratings)
        super().save(*args, **kwargs)


class PurchaseAnalytics(BaseModel):
    """
    Analytics and reporting data for purchasing.
    """
    
    # Time period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Metrics
    total_orders = models.IntegerField(default=0)
    total_value = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    average_order_value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Supplier metrics
    active_suppliers = models.IntegerField(default=0)
    top_supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    top_supplier_value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Performance metrics
    on_time_delivery_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    average_processing_time = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    
    # Cost analysis
    total_savings = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    cost_reduction_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    class Meta:
        ordering = ['-period_end']
        verbose_name = "Purchase Analytics"
        verbose_name_plural = "Purchase Analytics"
        unique_together = ['period_start', 'period_end']
    
    def __str__(self):
        return f"Analytics {self.period_start.date()} - {self.period_end.date()}"
