"""
Freelancers and individual contractor models for TidyGen ERP Community Edition.
Handles domestic individual cleaners and gig-based service providers.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel

User = get_user_model()


class Freelancer(BaseModel):
    """
    Individual domestic cleaner/contractor profile for community version.
    """
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]
    
    STATUS_CHOICES = [
        ('pending_verification', 'Pending Verification'),
        ('verified', 'Verified'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('rejected', 'Rejected'),
    ]
    
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('document_review', 'Document Review'),
        ('background_check', 'Background Check'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('bank_transfer', 'Bank Transfer'),
        ('crypto_wallet', 'Crypto Wallet'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('cash', 'Cash'),
    ]
    
    # User relationship
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='freelancer_profile')
    
    # Freelancer identification
    freelancer_id = models.CharField(_('freelancer ID'), max_length=50, unique=True)
    
    # Personal Information
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100)
    middle_name = models.CharField(_('middle name'), max_length=100, blank=True)
    date_of_birth = models.DateField(_('date of birth'))
    gender = models.CharField(_('gender'), max_length=20, choices=GENDER_CHOICES, blank=True)
    nationality = models.CharField(_('nationality'), max_length=100, blank=True)
    
    # Contact Information
    personal_email = models.EmailField(_('personal email'))
    personal_phone = models.CharField(_('personal phone'), max_length=20)
    emergency_contact_name = models.CharField(_('emergency contact name'), max_length=200)
    emergency_contact_phone = models.CharField(_('emergency contact phone'), max_length=20)
    emergency_contact_relationship = models.CharField(_('emergency contact relationship'), max_length=50, blank=True)
    
    # Address Information
    address_line1 = models.CharField(_('address line 1'), max_length=200)
    address_line2 = models.CharField(_('address line 2'), max_length=200, blank=True)
    city = models.CharField(_('city'), max_length=100)
    state = models.CharField(_('state'), max_length=100)
    postal_code = models.CharField(_('postal code'), max_length=20)
    country = models.CharField(_('country'), max_length=100)
    
    # Service Areas
    service_areas = models.JSONField(_('service areas'), default=list)  # List of postal codes/areas
    max_travel_distance = models.IntegerField(_('max travel distance (miles)'), default=25)
    
    # Service Specializations
    cleaning_types = models.JSONField(_('cleaning types'), default=list)  # ['residential', 'commercial', 'deep_cleaning']
    special_skills = models.TextField(_('special skills'), blank=True)
    certifications = models.JSONField(_('certifications'), default=list)
    years_of_experience = models.IntegerField(_('years of experience'), default=0)
    
    # Availability
    availability_schedule = models.JSONField(_('availability schedule'), default=dict)  # Weekly schedule
    is_available = models.BooleanField(_('is available'), default=True)
    last_activity = models.DateTimeField(_('last activity'), auto_now=True)
    
    # Performance Metrics
    rating = models.DecimalField(_('rating'), max_digits=3, decimal_places=2, default=0, 
                                validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_jobs_completed = models.IntegerField(_('total jobs completed'), default=0)
    on_time_percentage = models.DecimalField(_('on time percentage'), max_digits=5, decimal_places=2, default=0)
    completion_rate = models.DecimalField(_('completion rate'), max_digits=5, decimal_places=2, default=0)
    
    # Financial Information
    hourly_rate = models.DecimalField(_('hourly rate'), max_digits=8, decimal_places=2, 
                                     validators=[MinValueValidator(0)])
    currency = models.CharField(_('currency'), max_length=3, default='USD')
    payment_method = models.CharField(_('payment method'), max_length=20, choices=PAYMENT_METHOD_CHOICES, default='bank_transfer')
    
    # Web3 Integration
    wallet_address = models.CharField(_('wallet address'), max_length=42, blank=True)
    blockchain_verified = models.BooleanField(_('blockchain verified'), default=False)
    nft_badge_id = models.CharField(_('NFT badge ID'), max_length=100, blank=True)
    
    # Status and Verification
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending_verification')
    verification_status = models.CharField(_('verification status'), max_length=20, choices=VERIFICATION_STATUS_CHOICES, default='pending')
    
    # Background Check
    background_check_completed = models.BooleanField(_('background check completed'), default=False)
    background_check_date = models.DateField(_('background check date'), null=True, blank=True)
    background_check_reference = models.CharField(_('background check reference'), max_length=200, blank=True)
    
    # Insurance
    insurance_provider = models.CharField(_('insurance provider'), max_length=200, blank=True)
    insurance_policy_number = models.CharField(_('insurance policy number'), max_length=100, blank=True)
    insurance_expiry_date = models.DateField(_('insurance expiry date'), null=True, blank=True)
    
    # Additional Information
    bio = models.TextField(_('bio'), blank=True)
    profile_picture = models.ImageField(_('profile picture'), upload_to='freelancer_profiles/', blank=True, null=True)
    preferred_language = models.CharField(_('preferred language'), max_length=10, default='en')
    timezone = models.CharField(_('timezone'), max_length=50, default='UTC')
    
    class Meta:
        verbose_name = _('Freelancer')
        verbose_name_plural = _('Freelancers')
        ordering = ['-created']
        indexes = [
            models.Index(fields=['freelancer_id']),
            models.Index(fields=['status', 'is_available']),
            models.Index(fields=['city', 'state']),
            models.Index(fields=['rating']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.freelancer_id})"
    
    @property
    def full_name(self):
        """Get full name of the freelancer."""
        return f"{self.first_name} {self.last_name}".strip()
    
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
    
    @property
    def is_eligible_for_jobs(self):
        """Check if freelancer is eligible for new job assignments."""
        return (
            self.status == 'active' and 
            self.is_available and 
            self.background_check_completed
        )


class FreelancerDocument(BaseModel):
    """
    Documents for freelancer verification and compliance.
    """
    DOCUMENT_TYPES = [
        ('id_copy', 'ID Copy'),
        ('passport', 'Passport'),
        ('drivers_license', 'Driver\'s License'),
        ('background_check', 'Background Check'),
        ('insurance_certificate', 'Insurance Certificate'),
        ('certification', 'Professional Certification'),
        ('tax_document', 'Tax Document'),
        ('bank_statement', 'Bank Statement'),
        ('reference_letter', 'Reference Letter'),
        ('other', 'Other'),
    ]
    
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(_('document type'), max_length=30, choices=DOCUMENT_TYPES)
    title = models.CharField(_('title'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    file = models.FileField(_('file'), upload_to='freelancer_documents/')
    file_size = models.IntegerField(_('file size'), null=True, blank=True)
    
    # Verification
    is_verified = models.BooleanField(_('is verified'), default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='verified_freelancer_documents')
    verified_at = models.DateTimeField(_('verified at'), null=True, blank=True)
    verification_notes = models.TextField(_('verification notes'), blank=True)
    
    # Expiry
    expiry_date = models.DateField(_('expiry date'), null=True, blank=True)
    is_expired = models.BooleanField(_('is expired'), default=False)
    
    class Meta:
        verbose_name = _('Freelancer Document')
        verbose_name_plural = _('Freelancer Documents')
        ordering = ['-created']
    
    def __str__(self):
        return f"{self.freelancer.full_name} - {self.title}"


class FreelancerAvailability(BaseModel):
    """
    Freelancer availability schedule for job matching.
    """
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, related_name='availability_slots')
    day_of_week = models.IntegerField(_('day of week'), choices=DAY_CHOICES)
    start_time = models.TimeField(_('start time'))
    end_time = models.TimeField(_('end time'))
    is_available = models.BooleanField(_('is available'), default=True)
    notes = models.TextField(_('notes'), blank=True)
    
    # Recurring availability
    is_recurring = models.BooleanField(_('is recurring'), default=True)
    specific_dates = models.JSONField(_('specific dates'), default=list)  # For non-recurring availability
    
    class Meta:
        verbose_name = _('Freelancer Availability')
        verbose_name_plural = _('Freelancer Availability')
        ordering = ['day_of_week', 'start_time']
        unique_together = ['freelancer', 'day_of_week', 'start_time']
    
    def __str__(self):
        day_name = dict(self.DAY_CHOICES)[self.day_of_week]
        return f"{self.freelancer.full_name} - {day_name} {self.start_time}-{self.end_time}"


class FreelancerSkill(BaseModel):
    """
    Skills and certifications for freelancers.
    """
    SKILL_CATEGORIES = [
        ('cleaning', 'Cleaning'),
        ('maintenance', 'Maintenance'),
        ('specialized', 'Specialized Services'),
        ('equipment', 'Equipment Operation'),
        ('safety', 'Safety'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(_('skill name'), max_length=100, unique=True)
    category = models.CharField(_('category'), max_length=20, choices=SKILL_CATEGORIES)
    description = models.TextField(_('description'), blank=True)
    is_certification_required = models.BooleanField(_('certification required'), default=False)
    
    class Meta:
        verbose_name = _('Freelancer Skill')
        verbose_name_plural = _('Freelancer Skills')
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class FreelancerSkillAssignment(BaseModel):
    """
    Freelancer skill assignments and proficiency levels.
    """
    PROFICIENCY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, related_name='skill_assignments')
    skill = models.ForeignKey(FreelancerSkill, on_delete=models.CASCADE, related_name='freelancer_assignments')
    proficiency_level = models.CharField(_('proficiency level'), max_length=20, choices=PROFICIENCY_LEVELS)
    years_of_experience = models.IntegerField(_('years of experience'), default=0)
    certification_date = models.DateField(_('certification date'), null=True, blank=True)
    certification_body = models.CharField(_('certification body'), max_length=200, blank=True)
    certification_number = models.CharField(_('certification number'), max_length=100, blank=True)
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        verbose_name = _('Freelancer Skill Assignment')
        verbose_name_plural = _('Freelancer Skill Assignments')
        unique_together = ['freelancer', 'skill']
        ordering = ['skill__category', 'skill__name']
    
    def __str__(self):
        return f"{self.freelancer.full_name} - {self.skill.name} ({self.get_proficiency_level_display()})"


class FreelancerReview(BaseModel):
    """
    Reviews and ratings from clients for freelancers.
    """
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='freelancer_reviews_given')
    
    # Rating (1-5 scale)
    overall_rating = models.IntegerField(_('overall rating'), 
                                        validators=[MinValueValidator(1), MaxValueValidator(5)])
    quality_rating = models.IntegerField(_('quality rating'), 
                                        validators=[MinValueValidator(1), MaxValueValidator(5)])
    punctuality_rating = models.IntegerField(_('punctuality rating'), 
                                            validators=[MinValueValidator(1), MaxValueValidator(5)])
    communication_rating = models.IntegerField(_('communication rating'), 
                                              validators=[MinValueValidator(1), MaxValueValidator(5)])
    professionalism_rating = models.IntegerField(_('professionalism rating'), 
                                                validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Review content
    title = models.CharField(_('review title'), max_length=200)
    comment = models.TextField(_('comment'))
    would_recommend = models.BooleanField(_('would recommend'), default=True)
    
    # Related job/service
    job_reference = models.CharField(_('job reference'), max_length=100, blank=True)
    
    class Meta:
        verbose_name = _('Freelancer Review')
        verbose_name_plural = _('Freelancer Reviews')
        ordering = ['-created']
        indexes = [
            models.Index(fields=['freelancer', 'overall_rating']),
        ]
    
    def __str__(self):
        return f"Review for {self.freelancer.full_name} by {self.reviewer.get_full_name()}"
    
    @property
    def average_rating(self):
        """Calculate average rating across all criteria."""
        ratings = [
            self.overall_rating,
            self.quality_rating,
            self.punctuality_rating,
            self.communication_rating,
            self.professionalism_rating
        ]
        return sum(ratings) / len(ratings)
