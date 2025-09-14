"""
Unit tests for core views.
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.core.models import User, Permission, Role
from apps.organizations.models import Organization, OrganizationMembership

User = get_user_model()


class TestUserViews:
    """Test user-related views."""
    
    def test_user_list_unauthorized(self, api_client):
        """Test user list without authentication."""
        url = reverse('user-list-create')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_user_list_authorized(self, authenticated_client):
        """Test user list with authentication."""
        url = reverse('user-list-create')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
    
    def test_user_create(self, api_client):
        """Test user creation."""
        url = reverse('user-list-create')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['email'] == 'newuser@example.com'
        assert response.data['first_name'] == 'New'
        assert response.data['last_name'] == 'User'
    
    def test_user_create_password_mismatch(self, api_client):
        """Test user creation with password mismatch."""
        url = reverse('user-list-create')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123',
            'password_confirm': 'differentpass'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Passwords don\'t match' in str(response.data)
    
    def test_user_profile(self, authenticated_client, user):
        """Test user profile retrieval."""
        url = reverse('user-profile')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
        assert response.data['username'] == user.username
    
    def test_user_profile_update(self, authenticated_client):
        """Test user profile update."""
        url = reverse('user-profile')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = authenticated_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'
        assert response.data['last_name'] == 'Name'


class TestAuthenticationViews:
    """Test authentication-related views."""
    
    def test_login_success(self, api_client, user):
        """Test successful login."""
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
    
    def test_login_invalid_credentials(self, api_client):
        """Test login with invalid credentials."""
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Invalid credentials' in str(response.data)
    
    def test_logout(self, authenticated_client):
        """Test logout."""
        url = reverse('logout')
        # First get a refresh token
        login_url = reverse('login')
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        login_response = authenticated_client.post(login_url, login_data)
        refresh_token = login_response.data['refresh']
        
        # Now logout
        logout_data = {'refresh': refresh_token}
        response = authenticated_client.post(url, logout_data)
        assert response.status_code == status.HTTP_200_OK
        assert 'Logout successful' in response.data['message']
    
    def test_password_change(self, authenticated_client):
        """Test password change."""
        url = reverse('password-change')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'Password changed successfully' in response.data['message']
    
    def test_password_change_wrong_old_password(self, authenticated_client):
        """Test password change with wrong old password."""
        url = reverse('password-change')
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Old password is incorrect' in str(response.data)


class TestWeb3Views:
    """Test Web3-related views."""
    
    def test_wallet_connect(self, authenticated_client):
        """Test Web3 wallet connection."""
        url = reverse('web3-wallet-connect')
        data = {
            'wallet_address': '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
            'signature': '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1b',
            'message': 'Welcome to TidyGen ERP! Please sign this message to connect your wallet.'
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'Wallet connected successfully' in response.data['message']
        assert response.data['wallet_address'] == '0x742d35cc6634c0532925a3b8d4c9db96c4b4d8b6'  # Lowercase
    
    def test_wallet_connect_invalid_address(self, authenticated_client):
        """Test Web3 wallet connection with invalid address."""
        url = reverse('web3-wallet-connect')
        data = {
            'wallet_address': 'invalid_address',
            'signature': '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1b',
            'message': 'Welcome to TidyGen ERP! Please sign this message to connect your wallet.'
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Invalid wallet address format' in str(response.data)


class TestPermissionViews:
    """Test permission-related views."""
    
    def test_permission_list_unauthorized(self, api_client):
        """Test permission list without authentication."""
        url = reverse('permission-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_permission_list_authorized(self, admin_client):
        """Test permission list with admin authentication."""
        url = reverse('permission-list')
        response = admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data


class TestRoleViews:
    """Test role-related views."""
    
    def test_role_list_unauthorized(self, api_client):
        """Test role list without authentication."""
        url = reverse('role-list-create')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_role_list_authorized(self, admin_client):
        """Test role list with admin authentication."""
        url = reverse('role-list-create')
        response = admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
    
    def test_role_create(self, admin_client, permission):
        """Test role creation."""
        url = reverse('role-list-create')
        data = {
            'name': 'New Role',
            'description': 'A new role',
            'permission_ids': [permission.id]
        }
        response = admin_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Role'
        assert response.data['description'] == 'A new role'
        assert len(response.data['permissions']) == 1


class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_check(self, api_client):
        """Test health check endpoint."""
        url = reverse('health-check')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'healthy'
        assert 'timestamp' in response.data
        assert 'version' in response.data
