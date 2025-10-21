import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.core.models import User, Permission, Role, SystemSettings, Organization, AuditLog


class TestUserModel(TestCase):
    """Test cases for the User model."""

    def test_user_creation(self):
        """Test creating a user with required fields."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        
        assert user.email == 'test@example.com'
        assert user.username == 'testuser'
        assert user.first_name == 'Test'
        assert user.last_name == 'User'
        assert user.is_active == True
        assert user.is_staff == False

    def test_user_full_name_property(self):
        """Test the full_name property returns correct name."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            password='testpass123'
        )
        
        assert user.full_name == 'John Doe'
        assert str(user) == 'John Doe (test@example.com)'

    def test_user_email_unique(self):
        """Test that email field is unique."""
        User.objects.create_user(
            username='user1',
            email='test@example.com',
            first_name='User',
            last_name='One',
            password='testpass123'
        )
        
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                username='user2',
                email='test@example.com',  # Duplicate email
                first_name='User',
                last_name='Two',
                password='testpass123'
            )


class TestPermissionModel(TestCase):
    """Test cases for the Permission model."""

    def test_permission_creation(self):
        """Test creating a permission."""
        permission = Permission.objects.create(
            name='Test Permission',
            codename='test_permission',
            description='A test permission',
            module='test_module'
        )
        
        assert permission.name == 'Test Permission'
        assert permission.codename == 'test_permission'
        assert permission.module == 'test_module'
        assert str(permission) == 'test_module: Test Permission'

    def test_permission_codename_unique(self):
        """Test that codename is unique."""
        Permission.objects.create(
            name='Permission 1',
            codename='test_code',
            description='First permission'
        )
        
        with pytest.raises(IntegrityError):
            Permission.objects.create(
                name='Permission 2',
                codename='test_code',  # Duplicate codename
                description='Second permission'
            )


class TestRoleModel(TestCase):
    """Test cases for the Role model."""

    def test_role_creation(self):
        """Test creating a role."""
        role = Role.objects.create(
            name='Test Role',
            description='A test role',
            is_system=False,
            is_active=True
        )
        
        assert role.name == 'Test Role'
        assert role.is_active == True
        assert str(role) == 'Test Role'

    def test_role_permissions_relationship(self):
        """Test role-permission relationship."""
        role = Role.objects.create(name='Test Role')
        permission = Permission.objects.create(
            name='Test Permission',
            codename='test_perm',
            description='Test permission'
        )
        
        role.permissions.add(permission)
        
        assert permission in role.permissions.all()
        assert role in permission.roles.all()


class TestOrganizationModel(TestCase):
    """Test cases for the Organization model."""

    def test_organization_creation(self):
        """Test creating an organization."""
        org = Organization.objects.create(
            name='Test Organization',
            description='A test organization',
            email='contact@testorg.com'
        )
        
        assert org.name == 'Test Organization'
        assert org.is_active == True
        assert str(org) == 'Test Organization'

    def test_single_organization_constraint(self):
        """Test that only one organization can be created in community edition."""
        Organization.objects.create(
            name='First Organization',
            description='First org'
        )
        
        with pytest.raises(ValueError, match="Only one organization is allowed"):
            Organization.objects.create(
                name='Second Organization',
                description='Second org'
            )


class TestSystemSettingsModel(TestCase):
    """Test cases for the SystemSettings model."""

    def test_system_settings_creation(self):
        """Test creating system settings."""
        setting = SystemSettings.objects.create(
            key='test_setting',
            value={'enabled': True, 'count': 10},
            description='A test setting',
            is_public=False
        )
        
        assert setting.key == 'test_setting'
        assert setting.value == {'enabled': True, 'count': 10}
        assert setting.is_public == False
        assert str(setting) == 'test_setting: {\'enabled\': True, \'count\': 10}'


class TestAuditLogModel(TestCase):
    """Test cases for the AuditLog model."""

    def test_audit_log_creation(self):
        """Test creating an audit log entry."""
        user = User.objects.create_user(
            username='audituser',
            email='audit@example.com',
            first_name='Audit',
            last_name='User',
            password='testpass123'
        )
        
        audit_log = AuditLog.objects.create(
            user=user,
            action='create',
            model_name='TestModel',
            object_id='123',
            object_repr='Test Object',
            changes={'field': 'old_value', 'field': 'new_value'},
            ip_address='127.0.0.1'
        )
        
        assert audit_log.user == user
        assert audit_log.action == 'create'
        assert audit_log.model_name == 'TestModel'
        assert str(audit_log) == f'{user} - create - TestModel'
