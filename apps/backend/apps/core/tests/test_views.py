import pytest
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.core.models import User, Permission, Role, SystemSettings

User = get_user_model()


class TestViews(TestCase):
    """Test cases for core views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )

    def test_user_list_view_unauthenticated(self):
        """Test user list view without authentication."""
        url = reverse('user-list-create')
        
        # Without authentication, should get 401
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_list_view_authenticated(self):
        """Test user list view with authentication."""
        # Use admin user since UserListCreateView requires IsSystemAdmin permission
        self.client.force_authenticate(user=self.admin_user)
        
        # Test the user list endpoint
        url = reverse('user-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_user_create_view(self):
        """Test user creation endpoint."""
        # Use admin user for user creation (as it might require admin permissions)
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('user-list-create')
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123',
            'password_confirm': 'newpass123'  # Add required password_confirm field
        }
        
        response = self.client.post(url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'newuser')

    def test_permission_list_view(self):
        """Test permission list view."""
        # Create a permission first
        permission = Permission.objects.create(
            name='Test Permission',
            codename='test_perm',
            description='Test permission description'
        )
        
        # Use admin user since PermissionListView requires IsSystemAdmin permission
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('permission-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_role_list_view(self):
        """Test role list view."""
        # Create a role first
        role = Role.objects.create(
            name='Test Role',
            description='Test role description'
        )
        
        # Use admin user since RoleListCreateView requires IsSystemAdmin permission
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('role-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_system_settings_view(self):
        """Test system settings view."""
        # Create a system setting first
        setting = SystemSettings.objects.create(
            key='test_setting',
            value={'enabled': True, 'count': 10},
            description='Test setting',
            is_public=False
        )
        
        # Use admin user since SystemSettingsListView requires IsSystemAdmin permission
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('system-settings-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_health_check_view(self):
        """Test health check endpoint."""
        # Health check requires authentication according to the view
        self.client.force_authenticate(user=self.user)
        
        url = reverse('health-check')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)