"""
Wallet URL Configuration

This module defines URL patterns for wallet-related API endpoints,
including wallet management, authentication, and transaction signing.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'wallets', views.WalletViewSet, basename='wallet')
router.register(r'signatures', views.WalletSignatureViewSet, basename='wallet-signature')
router.register(r'permissions', views.WalletPermissionViewSet, basename='wallet-permission')
router.register(r'sessions', views.WalletSessionViewSet, basename='wallet-session')

app_name = 'wallet'

urlpatterns = [
    # Router URLs for ViewSets
    path('', include(router.urls)),
    
    # Wallet connection and authentication
    path('connect/', views.WalletConnectView.as_view(), name='wallet-connect'),
    path('auth/', views.WalletAuthenticationView.as_view(), name='wallet-auth'),
    
    # Transaction signing
    path('sign/', views.TransactionSignatureView.as_view(), name='wallet-sign'),
    
    # Supported wallets and network info
    path('supported/', views.SupportedWalletsView.as_view(), name='supported-wallets'),
    path('network/<str:wallet_type>/', views.WalletNetworkInfoView.as_view(), name='wallet-network-info'),
    
    # Account information
    path('account/<uuid:wallet_id>/', views.WalletAccountInfoView.as_view(), name='wallet-account-info'),
]
