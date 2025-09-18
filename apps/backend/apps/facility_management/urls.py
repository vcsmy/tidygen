"""
URL configuration for Facility Management app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FacilityViewSet, VehicleViewSet, EquipmentViewSet,
    MaintenanceRecordViewSet, AssetViewSet
)

router = DefaultRouter()
router.register(r'facilities', FacilityViewSet)
router.register(r'vehicles', VehicleViewSet)
router.register(r'equipment', EquipmentViewSet)
router.register(r'maintenance-records', MaintenanceRecordViewSet)
router.register(r'assets', AssetViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
