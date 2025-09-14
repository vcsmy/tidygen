"""
Sales and client management URL configuration for TidyGen ERP platform.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.sales.views import (
    ClientViewSet, IndividualClientViewSet, CorporateClientViewSet,
    ClientContactViewSet, ClientNoteViewSet, ClientDocumentViewSet,
    ClientTagViewSet, ClientTagAssignmentViewSet, ClientInteractionViewSet,
    ClientSegmentViewSet, ClientSegmentAssignmentViewSet, ClientDashboardViewSet
)

router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'individual-clients', IndividualClientViewSet)
router.register(r'corporate-clients', CorporateClientViewSet)
router.register(r'client-contacts', ClientContactViewSet)
router.register(r'client-notes', ClientNoteViewSet)
router.register(r'client-documents', ClientDocumentViewSet)
router.register(r'client-tags', ClientTagViewSet)
router.register(r'client-tag-assignments', ClientTagAssignmentViewSet)
router.register(r'client-interactions', ClientInteractionViewSet)
router.register(r'client-segments', ClientSegmentViewSet)
router.register(r'client-segment-assignments', ClientSegmentAssignmentViewSet)
router.register(r'dashboard', ClientDashboardViewSet, basename='client-dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
