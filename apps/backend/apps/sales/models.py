"""
Sales and client management models for TidyGen ERP platform.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel

User = get_user_model()


class Client(BaseModel):
    """
    Base client model that supports both individual and corporate clients.
    """
    CLIENT_TYPES = [
        ('individual', 'Individual'),
        ('corporate', 'Corporate'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('prospect', 'Prospect'),
        ('suspended', 'Suspended'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('vip', 'VIP'),
    ]
    
    client_type = models.CharField(max_length=20, choices=CLIENT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='prospect')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Common fields for both types
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True, validators=[
        RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )
    ])
    website = models.URLField(blank=True)
    
    # Address information
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Financial information
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_terms = models.IntegerField(default=30)  # days
    tax_id = models.CharField(max_length=50, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    
    # Business information
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(
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
    
    # Relationship management
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_clients'
    )
    source = models.CharField(max_length=100, blank=True)  # How they found us
    notes = models.TextField(blank=True)
    
    # Social media and communication preferences
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('sms', 'SMS'),
            ('whatsapp', 'WhatsApp'),
        ],
        default='email'
    )
    marketing_consent = models.BooleanField(default=False)
    newsletter_subscription = models.BooleanField(default=False)
    
    # Tracking
    last_contact_date = models.DateTimeField(null=True, blank=True)
    last_activity_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_clients'
    )
    
    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['client_type', 'status']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['last_contact_date']),
        ]
    
    def __str__(self):
        if self.client_type == 'individual':
            return f"{self.individual_client.first_name} {self.individual_client.last_name}"
        else:
            return self.corporate_client.company_name
    
    @property
    def display_name(self):
        """Get display name based on client type."""
        if self.client_type == 'individual':
            individual = getattr(self, 'individual_client', None)
            if individual:
                return f"{individual.first_name} {individual.last_name}"
        else:
            corporate = getattr(self, 'corporate_client', None)
            if corporate:
                return corporate.company_name
        return "Unknown Client"
    
    @property
    def full_address(self):
        """Get formatted full address."""
        address_parts = [
            self.address_line1,
            self.address_line2,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ', '.join(filter(None, address_parts))


class IndividualClient(BaseModel):
    """
    Individual client specific information.
    """
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='individual_client')
    
    # Personal information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
            ('prefer_not_to_say', 'Prefer not to say'),
        ],
        blank=True
    )
    
    # Professional information
    job_title = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=200, blank=True)
    
    # Emergency contact
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)
    
    # Additional personal details
    nationality = models.CharField(max_length=100, blank=True)
    language_preference = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    
    class Meta:
        verbose_name = 'Individual Client'
        verbose_name_plural = 'Individual Clients'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class CorporateClient(BaseModel):
    """
    Corporate client specific information.
    """
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='corporate_client')
    
    # Company information
    company_name = models.CharField(max_length=200)
    legal_name = models.CharField(max_length=200, blank=True)
    registration_number = models.CharField(max_length=100, blank=True)
    tax_registration_number = models.CharField(max_length=100, blank=True)
    
    # Business details
    business_type = models.CharField(
        max_length=50,
        choices=[
            ('corporation', 'Corporation'),
            ('llc', 'Limited Liability Company'),
            ('partnership', 'Partnership'),
            ('sole_proprietorship', 'Sole Proprietorship'),
            ('non_profit', 'Non-Profit'),
            ('government', 'Government'),
            ('other', 'Other'),
        ],
        blank=True
    )
    founded_year = models.IntegerField(null=True, blank=True)
    annual_revenue = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Key personnel
    ceo_name = models.CharField(max_length=200, blank=True)
    cfo_name = models.CharField(max_length=200, blank=True)
    cto_name = models.CharField(max_length=200, blank=True)
    
    # Additional company details
    parent_company = models.CharField(max_length=200, blank=True)
    subsidiaries = models.TextField(blank=True)
    business_description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Corporate Client'
        verbose_name_plural = 'Corporate Clients'
    
    def __str__(self):
        return self.company_name


class ClientContact(BaseModel):
    """
    Additional contacts for corporate clients.
    """
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contacts')
    
    # Contact information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    
    # Professional information
    job_title = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    
    # Contact preferences
    is_primary = models.BooleanField(default=False)
    is_decision_maker = models.BooleanField(default=False)
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('mobile', 'Mobile'),
            ('sms', 'SMS'),
        ],
        default='email'
    )
    
    # Additional information
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Client Contact'
        verbose_name_plural = 'Client Contacts'
        ordering = ['-is_primary', 'first_name', 'last_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.client.display_name}"


class ClientNote(BaseModel):
    """
    Notes and communication history for clients.
    """
    NOTE_TYPES = [
        ('general', 'General Note'),
        ('meeting', 'Meeting'),
        ('call', 'Phone Call'),
        ('email', 'Email'),
        ('proposal', 'Proposal'),
        ('contract', 'Contract'),
        ('issue', 'Issue/Problem'),
        ('follow_up', 'Follow Up'),
        ('other', 'Other'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='notes')
    note_type = models.CharField(max_length=20, choices=NOTE_TYPES, default='general')
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    # Related information
    related_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='client_notes'
    )
    related_date = models.DateTimeField(null=True, blank=True)
    is_private = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Client Note'
        verbose_name_plural = 'Client Notes'
        ordering = ['-created']
    
    def __str__(self):
        return f"{self.title} - {self.client.display_name}"


class ClientDocument(BaseModel):
    """
    Document attachments for clients.
    """
    DOCUMENT_TYPES = [
        ('contract', 'Contract'),
        ('proposal', 'Proposal'),
        ('invoice', 'Invoice'),
        ('receipt', 'Receipt'),
        ('id_document', 'ID Document'),
        ('business_license', 'Business License'),
        ('tax_certificate', 'Tax Certificate'),
        ('other', 'Other'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, default='other')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='client_documents/')
    file_size = models.IntegerField(null=True, blank=True)
    
    # Document metadata
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_client_documents'
    )
    is_public = models.BooleanField(default=False)
    expiry_date = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Client Document'
        verbose_name_plural = 'Client Documents'
        ordering = ['-created']
    
    def __str__(self):
        return f"{self.title} - {self.client.display_name}"


class ClientTag(BaseModel):
    """
    Tags for categorizing and organizing clients.
    """
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#007bff')  # Hex color code
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Client Tag'
        verbose_name_plural = 'Client Tags'
        unique_together = ['name']
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ClientTagAssignment(BaseModel):
    """
    Many-to-many relationship between clients and tags.
    """
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='tag_assignments')
    tag = models.ForeignKey(ClientTag, on_delete=models.CASCADE, related_name='client_assignments')
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_client_tags'
    )
    
    class Meta:
        verbose_name = 'Client Tag Assignment'
        verbose_name_plural = 'Client Tag Assignments'
        unique_together = ['client', 'tag']
    
    def __str__(self):
        return f"{self.client.display_name} - {self.tag.name}"


class ClientInteraction(BaseModel):
    """
    Track all interactions with clients.
    """
    INTERACTION_TYPES = [
        ('email_sent', 'Email Sent'),
        ('email_received', 'Email Received'),
        ('phone_call', 'Phone Call'),
        ('meeting', 'Meeting'),
        ('proposal_sent', 'Proposal Sent'),
        ('contract_signed', 'Contract Signed'),
        ('payment_received', 'Payment Received'),
        ('support_ticket', 'Support Ticket'),
        ('website_visit', 'Website Visit'),
        ('other', 'Other'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    subject = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Interaction details
    initiated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='initiated_interactions'
    )
    duration_minutes = models.IntegerField(null=True, blank=True)
    outcome = models.CharField(max_length=200, blank=True)
    
    # Follow-up information
    requires_follow_up = models.BooleanField(default=False)
    follow_up_date = models.DateTimeField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Client Interaction'
        verbose_name_plural = 'Client Interactions'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['client', 'interaction_type']),
            models.Index(fields=['created']),
        ]
    
    def __str__(self):
        return f"{self.get_interaction_type_display()} - {self.client.display_name}"


class ClientSegment(BaseModel):
    """
    Client segmentation for marketing and sales purposes.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Segmentation criteria
    criteria = models.JSONField(default=dict)  # Store segmentation rules
    
    # Segment properties
    color = models.CharField(max_length=7, default='#007bff')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Client Segment'
        verbose_name_plural = 'Client Segments'
        unique_together = ['name']
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ClientSegmentAssignment(BaseModel):
    """
    Assignment of clients to segments.
    """
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='segment_assignments')
    segment = models.ForeignKey(ClientSegment, on_delete=models.CASCADE, related_name='client_assignments')
    assigned_date = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_client_segments'
    )
    
    class Meta:
        verbose_name = 'Client Segment Assignment'
        verbose_name_plural = 'Client Segment Assignments'
        unique_together = ['client', 'segment']
    
    def __str__(self):
        return f"{self.client.display_name} - {self.segment.name}"
