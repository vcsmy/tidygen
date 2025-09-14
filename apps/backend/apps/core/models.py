"""
Core models for TidyGen ERP platform.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from model_utils.models import TimeStampedModel, SoftDeletableModel
from django.utils.translation import gettext_lazy as _


class BaseModel(TimeStampedModel, SoftDeletableModel):
    """
    Base model with common fields for all models.
    """
    class Meta:
        abstract = True


class User(AbstractUser, BaseModel):
    """
    Custom user model extending Django's AbstractUser.
    """
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(_('phone number'), max_length=20, blank=True)
    avatar = models.ImageField(_('avatar'), upload_to='avatars/', blank=True, null=True)
    timezone = models.CharField(_('timezone'), max_length=50, default='UTC')
    language = models.CharField(_('language'), max_length=10, default='en')
    is_verified = models.BooleanField(_('verified'), default=False)
    last_login_ip = models.GenericIPAddressField(_('last login IP'), blank=True, null=True)
    
    # Web3 related fields
    wallet_address = models.CharField(_('wallet address'), max_length=42, blank=True)
    wallet_verified = models.BooleanField(_('wallet verified'), default=False)
    
    # Override inherited fields to add related_name
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to.'),
        related_name='core_users',
        related_query_name='core_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='core_users',
        related_query_name='core_user',
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        db_table = 'core_users'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_organization(self):
        """Get the single organization for community edition."""
        from .models import Organization
        return Organization.objects.first()


class Permission(BaseModel):
    """
    Custom permission model for fine-grained access control.
    """
    name = models.CharField(_('name'), max_length=100, unique=True)
    codename = models.CharField(_('codename'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    module = models.CharField(_('module'), max_length=50, blank=True)
    is_system = models.BooleanField(_('system permission'), default=False)
    
    class Meta:
        verbose_name = _('Permission')
        verbose_name_plural = _('Permissions')
        db_table = 'core_permissions'
        ordering = ['module', 'name']
    
    def __str__(self):
        return f"{self.module}: {self.name}" if self.module else self.name


class Role(BaseModel):
    """
    Role model for role-based access control.
    """
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('permissions'),
        blank=True,
        related_name='roles'
    )
    is_system = models.BooleanField(_('system role'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')
        db_table = 'core_roles'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class SystemSettings(BaseModel):
    """
    System-wide settings and configuration.
    """
    key = models.CharField(_('key'), max_length=100, unique=True)
    value = models.JSONField(_('value'), default=dict)
    description = models.TextField(_('description'), blank=True)
    is_public = models.BooleanField(_('public'), default=False)
    
    class Meta:
        verbose_name = _('System Setting')
        verbose_name_plural = _('System Settings')
        db_table = 'core_system_settings'
        ordering = ['key']
    
    def __str__(self):
        return f"{self.key}: {self.value}"


class Organization(BaseModel):
    """
    Single organization model for community edition.
    This replaces the multi-organization system.
    """
    name = models.CharField(_('organization name'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    
    # Contact information
    email = models.EmailField(_('email'), blank=True)
    phone = models.CharField(_('phone'), max_length=20, blank=True)
    website = models.URLField(_('website'), blank=True)
    
    # Address
    address_line1 = models.CharField(_('address line 1'), max_length=200, blank=True)
    address_line2 = models.CharField(_('address line 2'), max_length=200, blank=True)
    city = models.CharField(_('city'), max_length=100, blank=True)
    state = models.CharField(_('state'), max_length=100, blank=True)
    postal_code = models.CharField(_('postal code'), max_length=20, blank=True)
    country = models.CharField(_('country'), max_length=100, blank=True)
    
    # Organization details
    industry = models.CharField(_('industry'), max_length=100, blank=True)
    size = models.CharField(
        _('size'),
        max_length=20,
        choices=[
            ('1-10', '1-10 employees'),
            ('11-50', '11-50 employees'),
            ('51-200', '51-200 employees'),
            ('201-500', '201-500 employees'),
            ('501-1000', '501-1000 employees'),
            ('1000+', '1000+ employees'),
        ],
        blank=True
    )
    
    # Settings
    timezone = models.CharField(_('timezone'), max_length=50, default='UTC')
    currency = models.CharField(_('currency'), max_length=3, default='USD')
    language = models.CharField(_('language'), max_length=10, default='en')
    
    # Status
    is_active = models.BooleanField(_('active'), default=True)
    
    # Web3 settings
    wallet_address = models.CharField(_('wallet address'), max_length=42, blank=True, null=True)
    blockchain_network = models.CharField(_('blockchain network'), max_length=20, default='ethereum')
    
    class Meta:
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')
        db_table = 'core_organization'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Ensure only one organization exists
        if not self.pk and Organization.objects.exists():
            raise ValueError("Only one organization is allowed in community edition")
        super().save(*args, **kwargs)


class AuditLog(BaseModel):
    """
    Audit log for tracking changes to important models.
    """
    ACTION_CHOICES = [
        ('create', _('Create')),
        ('update', _('Update')),
        ('delete', _('Delete')),
        ('login', _('Login')),
        ('logout', _('Logout')),
        ('permission_denied', _('Permission Denied')),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('user')
    )
    action = models.CharField(_('action'), max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(_('model name'), max_length=100)
    object_id = models.CharField(_('object ID'), max_length=100, blank=True)
    object_repr = models.CharField(_('object representation'), max_length=200, blank=True)
    changes = models.JSONField(_('changes'), default=dict, blank=True)
    ip_address = models.GenericIPAddressField(_('IP address'), blank=True, null=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    
    class Meta:
        verbose_name = _('Audit Log')
        verbose_name_plural = _('Audit Logs')
        db_table = 'core_audit_logs'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['created']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name}"