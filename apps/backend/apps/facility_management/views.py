"""
Views for Facility Management models.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum, F
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Facility, Vehicle, Equipment, MaintenanceRecord, Asset
from .serializers import (
    FacilitySerializer, VehicleSerializer, EquipmentSerializer,
    MaintenanceRecordSerializer, AssetSerializer, FacilitySummarySerializer,
    VehicleSummarySerializer, EquipmentSummarySerializer
)


class FacilityViewSet(viewsets.ModelViewSet):
    """ViewSet for Facility model."""
    
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['facility_type', 'is_active', 'city', 'state']
    search_fields = ['name', 'address', 'city', 'state', 'contact_person']
    ordering_fields = ['name', 'created', 'modified']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FacilitySummarySerializer
        return FacilitySerializer
    
    @action(detail=True, methods=['get'])
    def vehicles(self, request, pk=None):
        """Get vehicles for a specific facility."""
        facility = self.get_object()
        vehicles = facility.vehicles.all()
        serializer = VehicleSummarySerializer(vehicles, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def equipment(self, request, pk=None):
        """Get equipment for a specific facility."""
        facility = self.get_object()
        equipment = facility.equipment.all()
        serializer = EquipmentSummarySerializer(equipment, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def dashboard_summary(self, request):
        """Get dashboard summary for facilities."""
        total_facilities = Facility.objects.count()
        active_facilities = Facility.objects.filter(is_active=True).count()
        total_vehicles = Vehicle.objects.count()
        total_equipment = Equipment.objects.count()
        
        # Facility types distribution
        facility_types = Facility.objects.values('facility_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total_facilities': total_facilities,
            'active_facilities': active_facilities,
            'total_vehicles': total_vehicles,
            'total_equipment': total_equipment,
            'facility_types': list(facility_types)
        })


class VehicleViewSet(viewsets.ModelViewSet):
    """ViewSet for Vehicle model."""
    
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['vehicle_type', 'fuel_type', 'status', 'home_facility']
    search_fields = ['make', 'model', 'license_plate', 'vin']
    ordering_fields = ['make', 'model', 'year', 'current_mileage']
    ordering = ['make', 'model']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return VehicleSummarySerializer
        return VehicleSerializer
    
    @action(detail=True, methods=['get'])
    def maintenance_records(self, request, pk=None):
        """Get maintenance records for a specific vehicle."""
        vehicle = self.get_object()
        records = vehicle.maintenance_records.all()
        serializer = MaintenanceRecordSerializer(records, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def schedule_maintenance(self, request, pk=None):
        """Schedule maintenance for a vehicle."""
        vehicle = self.get_object()
        data = request.data.copy()
        data['vehicle'] = vehicle.id
        
        serializer = MaintenanceRecordSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def dashboard_summary(self, request):
        """Get dashboard summary for vehicles."""
        total_vehicles = Vehicle.objects.count()
        active_vehicles = Vehicle.objects.filter(status='active').count()
        maintenance_due = Vehicle.objects.filter(
            next_service_mileage__lte=F('current_mileage')
        ).count()
        
        # Vehicle types distribution
        vehicle_types = Vehicle.objects.values('vehicle_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Status distribution
        status_distribution = Vehicle.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total_vehicles': total_vehicles,
            'active_vehicles': active_vehicles,
            'maintenance_due': maintenance_due,
            'vehicle_types': list(vehicle_types),
            'status_distribution': list(status_distribution)
        })


class EquipmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Equipment model."""
    
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['equipment_type', 'status', 'condition', 'current_facility', 'assigned_to']
    search_fields = ['name', 'brand', 'model', 'serial_number']
    ordering_fields = ['name', 'purchase_date', 'last_maintenance']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EquipmentSummarySerializer
        return EquipmentSerializer
    
    @action(detail=True, methods=['get'])
    def maintenance_records(self, request, pk=None):
        """Get maintenance records for specific equipment."""
        equipment = self.get_object()
        records = equipment.maintenance_records.all()
        serializer = MaintenanceRecordSerializer(records, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def schedule_maintenance(self, request, pk=None):
        """Schedule maintenance for equipment."""
        equipment = self.get_object()
        data = request.data.copy()
        data['equipment'] = equipment.id
        
        serializer = MaintenanceRecordSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def dashboard_summary(self, request):
        """Get dashboard summary for equipment."""
        total_equipment = Equipment.objects.count()
        active_equipment = Equipment.objects.filter(status='active').count()
        maintenance_due = Equipment.objects.filter(
            next_maintenance__lte=timezone.now().date()
        ).count()
        
        # Equipment types distribution
        equipment_types = Equipment.objects.values('equipment_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Status distribution
        status_distribution = Equipment.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total_equipment': total_equipment,
            'active_equipment': active_equipment,
            'maintenance_due': maintenance_due,
            'equipment_types': list(equipment_types),
            'status_distribution': list(status_distribution)
        })


class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for MaintenanceRecord model."""
    
    queryset = MaintenanceRecord.objects.all()
    serializer_class = MaintenanceRecordSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['maintenance_type', 'priority', 'status', 'assigned_to', 'performed_by']
    search_fields = ['title', 'description']
    ordering_fields = ['scheduled_date', 'completed_date', 'priority']
    ordering = ['-scheduled_date']
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Mark maintenance record as completed."""
        record = self.get_object()
        if record.status == 'completed':
            return Response(
                {'error': 'Maintenance record is already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        record.status = 'completed'
        record.completed_date = timezone.now()
        record.save()
        
        serializer = self.get_serializer(record)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def dashboard_summary(self, request):
        """Get dashboard summary for maintenance records."""
        total_records = MaintenanceRecord.objects.count()
        scheduled = MaintenanceRecord.objects.filter(status='scheduled').count()
        in_progress = MaintenanceRecord.objects.filter(status='in_progress').count()
        completed = MaintenanceRecord.objects.filter(status='completed').count()
        
        # Maintenance types distribution
        maintenance_types = MaintenanceRecord.objects.values('maintenance_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Priority distribution
        priority_distribution = MaintenanceRecord.objects.values('priority').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total_records': total_records,
            'scheduled': scheduled,
            'in_progress': in_progress,
            'completed': completed,
            'maintenance_types': list(maintenance_types),
            'priority_distribution': list(priority_distribution)
        })


class AssetViewSet(viewsets.ModelViewSet):
    """ViewSet for Asset model."""
    
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['asset_type', 'location', 'is_tokenized']
    search_fields = ['name', 'serial_number', 'model_number', 'manufacturer']
    ordering_fields = ['name', 'purchase_price', 'current_value']
    ordering = ['name']
    
    @action(detail=True, methods=['post'])
    def tokenize(self, request, pk=None):
        """Tokenize an asset as NFT."""
        asset = self.get_object()
        if asset.is_tokenized:
            return Response(
                {'error': 'Asset is already tokenized'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Here you would integrate with your smart contract
        # For now, we'll just mark it as tokenized
        asset.is_tokenized = True
        asset.nft_token_id = f"TGA-{asset.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        asset.save()
        
        serializer = self.get_serializer(asset)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def dashboard_summary(self, request):
        """Get dashboard summary for assets."""
        total_assets = Asset.objects.count()
        tokenized_assets = Asset.objects.filter(is_tokenized=True).count()
        total_value = Asset.objects.aggregate(
            total=Sum('current_value')
        )['total'] or 0
        
        # Asset types distribution
        asset_types = Asset.objects.values('asset_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total_assets': total_assets,
            'tokenized_assets': tokenized_assets,
            'total_value': total_value,
            'asset_types': list(asset_types)
        })
