"""
Smart Contract Ledger URL Configuration

This module defines the URL patterns for the Smart Contract Ledger API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    LedgerTransactionViewSet,
    LedgerPushView,
    LedgerVerifyView,
    LedgerAuditTrailView,
    LedgerBatchViewSet,
    LedgerEventViewSet,
    LedgerConfigurationViewSet
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'transactions', LedgerTransactionViewSet, basename='ledger-transaction')
router.register(r'batches', LedgerBatchViewSet, basename='ledger-batch')
router.register(r'events', LedgerEventViewSet, basename='ledger-event')
router.register(r'configurations', LedgerConfigurationViewSet, basename='ledger-configuration')

app_name = 'ledger'

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Main ledger endpoints
    path('push/', LedgerPushView.as_view(), name='ledger-push'),
    path('verify/<uuid:transaction_id>/', LedgerVerifyView.as_view(), name='ledger-verify'),
    path('audit/', LedgerAuditTrailView.as_view(), name='ledger-audit'),
]
