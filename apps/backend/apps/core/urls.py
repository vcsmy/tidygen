"""
Core URL configuration for TidyGen ERP platform.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for viewsets
router = DefaultRouter()

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/password/change/', views.PasswordChangeView.as_view(), name='password-change'),
    
    # User endpoints
    path('users/', views.UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/profile/', views.UserProfileView.as_view(), name='user-profile'),
    
    # Web3 endpoints
    path('web3/wallet/connect/', views.Web3WalletConnectView.as_view(), name='web3-wallet-connect'),
    
    # Permission endpoints
    path('permissions/', views.PermissionListView.as_view(), name='permission-list'),
    
    # Role endpoints
    path('roles/', views.RoleListCreateView.as_view(), name='role-list-create'),
    path('roles/<int:pk>/', views.RoleDetailView.as_view(), name='role-detail'),
    
    # System endpoints
    path('settings/', views.SystemSettingsListView.as_view(), name='system-settings-list'),
    path('audit-logs/', views.AuditLogListView.as_view(), name='audit-log-list'),
    path('health/', views.health_check, name='health-check'),
]