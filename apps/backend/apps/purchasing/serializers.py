"""
Purchasing Management Serializers

This module contains all the serializers for the purchasing management system,
providing API communication for purchase orders, suppliers, procurement, and analytics.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.purchasing.models import (
    PurchaseOrder, PurchaseOrderItem, PurchaseReceipt, PurchaseReceiptItem,
    ProcurementRequest, ProcurementRequestItem, SupplierPerformance, PurchaseAnalytics
)
from apps.inventory.models import Product, Supplier
from decimal import Decimal

User = get_user_model()


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    """Serializer for purchase order items."""
    product_name = serializers.CharField(read_only=True)
    product_sku = serializers.CharField(read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    quantity_pending = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = PurchaseOrderItem
        fields = [
            'id', 'product', 'product_name', 'product_sku', 'product_description',
            'quantity_ordered', 'quantity_received', 'quantity_pending',
            'unit_price', 'total_price', 'notes', 'expected_delivery_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """Serializer for purchase orders."""
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'po_number', 'organization', 'supplier', 'supplier_name',
            'requested_by', 'requested_by_name', 'approved_by', 'approved_by_name',
            'status', 'status_display', 'priority', 'priority_display',
            'order_date', 'expected_delivery_date', 'actual_delivery_date', 'approval_date',
            'subtotal', 'tax_amount', 'shipping_cost', 'discount_amount', 'total_amount',
            'notes', 'supplier_notes', 'terms_conditions', 'reference_number',
            'tracking_number', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'po_number', 'order_date', 'total_amount', 'created_at', 'updated_at']


class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating purchase orders with items."""
    items = PurchaseOrderItemSerializer(many=True)
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'organization', 'supplier', 'requested_by', 'status', 'priority',
            'expected_delivery_date', 'subtotal', 'tax_amount', 'shipping_cost',
            'discount_amount', 'notes', 'supplier_notes', 'terms_conditions',
            'reference_number', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        purchase_order = PurchaseOrder.objects.create(**validated_data)
        
        for item_data in items_data:
            PurchaseOrderItem.objects.create(purchase_order=purchase_order, **item_data)
        
        # Calculate total amount
        purchase_order.calculate_totals()
        return purchase_order


class PurchaseReceiptItemSerializer(serializers.ModelSerializer):
    """Serializer for purchase receipt items."""
    purchase_order_item_name = serializers.CharField(source='purchase_order_item.product_name', read_only=True)
    purchase_order_item_sku = serializers.CharField(source='purchase_order_item.product_sku', read_only=True)
    
    class Meta:
        model = PurchaseReceiptItem
        fields = [
            'id', 'purchase_order_item', 'purchase_order_item_name', 'purchase_order_item_sku',
            'quantity_received', 'condition', 'notes', 'batch_number', 'expiry_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PurchaseReceiptSerializer(serializers.ModelSerializer):
    """Serializer for purchase receipts."""
    items = PurchaseReceiptItemSerializer(many=True, read_only=True)
    purchase_order_number = serializers.CharField(source='purchase_order.po_number', read_only=True)
    received_by_name = serializers.CharField(source='received_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = PurchaseReceipt
        fields = [
            'id', 'receipt_number', 'purchase_order', 'purchase_order_number',
            'received_by', 'received_by_name', 'status', 'status_display',
            'receipt_date', 'notes', 'condition_notes', 'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'receipt_number', 'receipt_date', 'created_at', 'updated_at']


class PurchaseReceiptCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating purchase receipts with items."""
    items = PurchaseReceiptItemSerializer(many=True)
    
    class Meta:
        model = PurchaseReceipt
        fields = [
            'purchase_order', 'received_by', 'status', 'notes', 'condition_notes', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        receipt = PurchaseReceipt.objects.create(**validated_data)
        
        for item_data in items_data:
            PurchaseReceiptItem.objects.create(receipt=receipt, **item_data)
        
        # Update purchase order status
        receipt.update_purchase_order_status()
        return receipt


class ProcurementRequestItemSerializer(serializers.ModelSerializer):
    """Serializer for procurement request items."""
    product_name = serializers.CharField(read_only=True)
    product_sku = serializers.CharField(read_only=True)
    estimated_total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = ProcurementRequestItem
        fields = [
            'id', 'product', 'product_name', 'product_sku', 'product_description',
            'quantity', 'estimated_unit_price', 'estimated_total_price',
            'notes', 'specifications', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProcurementRequestSerializer(serializers.ModelSerializer):
    """Serializer for procurement requests."""
    items = ProcurementRequestItemSerializer(many=True, read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = ProcurementRequest
        fields = [
            'id', 'request_number', 'organization', 'requested_by', 'requested_by_name',
            'reviewed_by', 'reviewed_by_name', 'status', 'status_display',
            'priority', 'priority_display', 'request_date', 'required_date',
            'review_date', 'title', 'description', 'justification',
            'estimated_cost', 'budget_code', 'notes', 'rejection_reason',
            'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'request_number', 'request_date', 'created_at', 'updated_at']


class ProcurementRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating procurement requests with items."""
    items = ProcurementRequestItemSerializer(many=True)
    
    class Meta:
        model = ProcurementRequest
        fields = [
            'organization', 'requested_by', 'status', 'priority', 'required_date',
            'title', 'description', 'justification', 'estimated_cost',
            'budget_code', 'notes', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        request = ProcurementRequest.objects.create(**validated_data)
        
        for item_data in items_data:
            ProcurementRequestItem.objects.create(request=request, **item_data)
        
        # Calculate estimated cost
        request.calculate_estimated_cost()
        return request


class SupplierPerformanceSerializer(serializers.ModelSerializer):
    """Serializer for supplier performance records."""
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    evaluated_by_name = serializers.CharField(source='evaluated_by.get_full_name', read_only=True)
    overall_rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    
    class Meta:
        model = SupplierPerformance
        fields = [
            'id', 'supplier', 'supplier_name', 'organization', 'evaluated_by',
            'evaluated_by_name', 'on_time_delivery_rate', 'quality_rating',
            'communication_rating', 'price_competitiveness', 'overall_rating',
            'notes', 'evaluation_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'overall_rating', 'evaluation_date', 'created_at', 'updated_at']


class PurchaseAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for purchase analytics."""
    top_supplier_name = serializers.CharField(source='top_supplier.name', read_only=True)
    
    class Meta:
        model = PurchaseAnalytics
        fields = [
            'id', 'organization', 'period_start', 'period_end', 'total_orders',
            'total_value', 'average_order_value', 'active_suppliers',
            'top_supplier', 'top_supplier_name', 'top_supplier_value',
            'on_time_delivery_rate', 'average_processing_time',
            'total_savings', 'cost_reduction_percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PurchaseOrderSummarySerializer(serializers.ModelSerializer):
    """Simplified serializer for purchase order summaries."""
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'po_number', 'supplier_name', 'status', 'status_display',
            'priority', 'priority_display', 'order_date', 'expected_delivery_date',
            'total_amount', 'items_count'
        ]
    
    def get_items_count(self, obj):
        return obj.items.count()


class ProcurementRequestSummarySerializer(serializers.ModelSerializer):
    """Simplified serializer for procurement request summaries."""
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProcurementRequest
        fields = [
            'id', 'request_number', 'title', 'requested_by_name', 'status',
            'status_display', 'priority', 'priority_display', 'request_date',
            'required_date', 'estimated_cost', 'items_count'
        ]
    
    def get_items_count(self, obj):
        return obj.items.count()


class SupplierPerformanceSummarySerializer(serializers.ModelSerializer):
    """Simplified serializer for supplier performance summaries."""
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    
    class Meta:
        model = SupplierPerformance
        fields = [
            'id', 'supplier_name', 'on_time_delivery_rate', 'quality_rating',
            'communication_rating', 'price_competitiveness', 'overall_rating',
            'evaluation_date'
        ]


class PurchaseOrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating purchase order status."""
    
    class Meta:
        model = PurchaseOrder
        fields = ['status', 'approved_by', 'approval_date', 'actual_delivery_date', 'notes']
    
    def update(self, instance, validated_data):
        # Set approval date if status is being changed to approved
        if validated_data.get('status') == 'approved' and not instance.approval_date:
            from django.utils import timezone
            validated_data['approval_date'] = timezone.now()
        
        return super().update(instance, validated_data)


class ProcurementRequestStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating procurement request status."""
    
    class Meta:
        model = ProcurementRequest
        fields = ['status', 'reviewed_by', 'review_date', 'rejection_reason', 'notes']
    
    def update(self, instance, validated_data):
        # Set review date if status is being changed
        if validated_data.get('status') in ['approved', 'rejected'] and not instance.review_date:
            from django.utils import timezone
            validated_data['review_date'] = timezone.now()
        
        return super().update(instance, validated_data)
