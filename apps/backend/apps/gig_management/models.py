"""
Gig Management models for TidyGen ERP Community Edition.
Handles job posting, assignment, and tracking for individual contractors.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel

User = get_user_model()


class GigCategory(BaseModel):
    """
    Categories for gigs/jobs (e.g., residential cleaning, commercial cleaning, etc.).
    """
    name = models.CharField(_('category name'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    icon = models.CharField(_('icon'), max_length=50, blank=True)
    color = models.CharField(_('color'), max_length=7, blank=True)  # Hex color
    is_active = models.BooleanField(_('is active'), default=True)
    
    # Pricing defaults for this category
    default_hourly_rate_min = models.DecimalField(_('default min hourly rate'), max_digits=8, decimal_places=2, default=0)
    default_hourly_rate_max = models.DecimalField(_('default max hourly rate'), max_digits=8, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = _('Gig Category')
        verbose_name_plural = _('Gig Categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class GigJob(BaseModel):
    """
    Individual cleaning jobs/gigs posted by clients or the company.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('disputed', 'Disputed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('hourly', 'Hourly Rate'),
        ('fixed', 'Fixed Price'),
        ('performance', 'Performance Based'),
    ]
    
    CLIENT_TYPES = [
        ('individual', 'Individual'),
        ('corporate', 'Corporate'),
    ]
    
    # Job identification
    job_id = models.CharField(_('job ID'), max_length=50, unique=True)
    title = models.CharField(_('job title'), max_length=200)
    description = models.TextField(_('job description'))
    
    # Category and classification
    category = models.ForeignKey(GigCategory, on_delete=models.PROTECT, related_name='jobs')
    
    # Client information
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_gigs')
    client_type = models.CharField(_('client type'), max_length=20, choices=CLIENT_TYPES, default='individual')
    
    # Location and service area
    service_address = models.CharField(_('service address'), max_length=500)
    city = models.CharField(_('city'), max_length=100)
    state = models.CharField(_('state'), max_length=100)
    postal_code = models.CharField(_('postal code'), max_length=20)
    country = models.CharField(_('country'), max_length=100, default='US')
    
    # Service details
    service_type = models.CharField(_('service type'), max_length=100)  # e.g., 'deep_cleaning', 'regular_cleaning'
    property_type = models.CharField(_('property type'), max_length=50)  # e.g., 'apartment', 'house', 'office'
    property_size = models.CharField(_('property size'), max_length=100, blank=True)  # e.g., '2 bedroom', '1500 sq ft'
    
    # Scheduling
    preferred_start_date = models.DateTimeField(_('preferred start date'), null=True, blank=True)
    preferred_end_date = models.DateTimeField(_('preferred end date'), null=True, blank=True)
    actual_start_date = models.DateTimeField(_('actual start date'), null=True, blank=True)
    actual_end_date = models.DateTimeField(_('actual end date'), null=True, blank=True)
    estimated_duration_hours = models.DecimalField(_('estimated duration hours'), max_digits=6, decimal_places=2, default=0)
    actual_duration_hours = models.DecimalField(_('actual duration hours'), max_digits=6, decimal_places=2, default=0)
    
    # Pricing and payment
    payment_method = models.CharField(_('payment method'), max_length=20, choices=PAYMENT_METHOD_CHOICES, default='hourly')
    hourly_rate = models.DecimalField(_('hourly rate'), max_digits=8, decimal_places=2, null=True, blank=True)
    fixed_price = models.DecimalField(_('fixed price'), max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(_('currency'), max_length=3, default='USD')
    
    # Requirements and skills needed
    required_skills = models.JSONField(_('required skills'), default=list)
    required_certifications = models.JSONField(_('required certifications'), default=list)
    special_requirements = models.TextField(_('special requirements'), blank=True)
    
    # Assignment information
    assigned_freelancer = models.ForeignKey('freelancers.Freelancer', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_jobs')
    assigned_at = models.DateTimeField(_('assigned at'), null=True, blank=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_gigs')
    
    # Status and workflow
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(_('priority'), max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Ratings and reviews
    client_rating = models.IntegerField(_('client rating'), null=True, blank=True, 
                                       validators=[MinValueValidator(1), MaxValueValidator(5)])
    client_feedback = models.TextField(_('client feedback'), blank=True)
    freelancer_rating = models.IntegerField(_('freelancer rating'), null=True, blank=True,
                                           validators=[MinValueValidator(1), MaxValueValidator(5)])
    freelancer_feedback = models.TextField(_('freelancer feedback'), blank=True)
    
    # Web3 integration
    smart_contract_address = models.CharField(_('smart contract address'), max_length=42, blank=True)
    blockchain_transaction_hash = models.CharField(_('blockchain transaction hash'), max_length=66, blank=True)
    nft_job_badge = models.CharField(_('NFT job badge'), max_length=100, blank=True)
    
    # Additional metadata
    is_urgent = models.BooleanField(_('is urgent'), default=False)
    requires_background_check = models.BooleanField(_('requires background check'), default=True)
    allows_multiple_freelancers = models.BooleanField(_('allows multiple freelancers'), default=False)
    max_freelancers = models.IntegerField(_('max freelancers'), default=1, validators=[MinValueValidator(1)])
    
    class Meta:
        verbose_name = _('Gig Job')
        verbose_name_plural = _('Gig Jobs')
        ordering = ['-created']
        indexes = [
            models.Index(fields=['job_id']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['city', 'state']),
            models.Index(fields=['preferred_start_date']),
            models.Index(fields=['assigned_freelancer']),
        ]
    
    def __str__(self):
        return f"{self.job_id}: {self.title}"
    
    @property
    def full_address(self):
        """Get formatted full address."""
        address_parts = [
            self.service_address,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ', '.join(filter(None, address_parts))
    
    @property
    def total_cost(self):
        """Calculate total cost based on payment method."""
        if self.payment_method == 'hourly' and self.hourly_rate and self.estimated_duration_hours:
            return self.hourly_rate * self.estimated_duration_hours
        elif self.payment_method == 'fixed' and self.fixed_price:
            return self.fixed_price
        return 0


class GigApplication(BaseModel):
    """
    Applications by freelancers for specific gigs.
    """
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('reviewing', 'Reviewing'),
        ('shortlisted', 'Shortlisted'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    job = models.ForeignKey(GigJob, on_delete=models.CASCADE, related_name='applications')
    freelancer = models.ForeignKey('freelancers.Freelancer', on_delete=models.CASCADE, related_name='job_applications')
    
    # Application details
    cover_letter = models.TextField(_('cover letter'), blank=True)
    proposed_rate = models.DecimalField(_('proposed rate'), max_digits=8, decimal_places=2, null=True, blank=True)
    estimated_completion_time = models.DecimalField(_('estimated completion time hours'), max_digits=6, decimal_places=2, null=True, blank=True)
    availability_start = models.DateTimeField(_('availability start'), null=True, blank=True)
    availability_end = models.DateTimeField(_('availability end'), null=True, blank=True)
    
    # Status tracking
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='submitted')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications')
    reviewed_at = models.DateTimeField(_('reviewed at'), null=True, blank=True)
    review_notes = models.TextField(_('review notes'), blank=True)
    
    class Meta:
        verbose_name = _('Gig Application')
        verbose_name_plural = _('Gig Applications')
        ordering = ['-created']
        unique_together = ['job', 'freelancer']
        indexes = [
            models.Index(fields=['job', 'status']),
            models.Index(fields=['freelancer', 'status']),
        ]
    
    def __str__(self):
        return f"{self.freelancer.full_name} applied for {self.job.title}"


class JobMilestone(BaseModel):
    """
    Milestones for tracking job progress and payments.
    """
    MILESTONE_TYPES = [
        ('start', 'Job Started'),
        ('in_progress', 'In Progress'),
        ('quality_check', 'Quality Check'),
        ('completion', 'Job Completed'),
        ('payment', 'Payment Released'),
    ]
    
    job = models.ForeignKey(GigJob, on_delete=models.CASCADE, related_name='milestones')
    milestone_type = models.CharField(_('milestone type'), max_length=20, choices=MILESTONE_TYPES)
    title = models.CharField(_('title'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    
    # Milestone details
    expected_date = models.DateTimeField(_('expected date'), null=True, blank=True)
    actual_date = models.DateTimeField(_('actual date'), null=True, blank=True)
    is_completed = models.BooleanField(_('is completed'), default=False)
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='completed_milestones')
    
    # Quality metrics
    quality_score = models.IntegerField(_('quality score'), null=True, blank=True,
                                       validators=[MinValueValidator(1), MaxValueValidator(10)])
    quality_notes = models.TextField(_('quality notes'), blank=True)
    
    # Payment information (if milestone triggers payment)
    payment_amount = models.DecimalField(_('payment amount'), max_digits=10, decimal_places=2, null=True, blank=True)
    payment_released = models.BooleanField(_('payment released'), default=False)
    payment_date = models.DateTimeField(_('payment date'), null=True, blank=True)
    
    # Web3 integration
    milestone_hash = models.CharField(_('milestone hash'), max_length=66, blank=True)
    
    class Meta:
        verbose_name = _('Job Milestone')
        verbose_name_plural = _('Job Milestones')
        ordering = ['expected_date', 'created']
    
    def __str__(self):
        return f"{self.job.job_id}: {self.title}"


class JobPhoto(BaseModel):
    """
    Photos for job documentation and progress tracking.
    """
    PHOTO_TYPES = [
        ('before', 'Before'),
        ('during', 'During'),
        ('after', 'After'),
        ('quality_check', 'Quality Check'),
        ('issue', 'Issue Documentation'),
    ]
    
    job = models.ForeignKey(GigJob, on_delete=models.CASCADE, related_name='photos')
    milestone = models.ForeignKey(JobMilestone, on_delete=models.CASCADE, null=True, blank=True, related_name='photos')
    photo_type = models.CharField(_('photo type'), max_length=20, choices=PHOTO_TYPES)
    title = models.CharField(_('title'), max_length=200, blank=True)
    description = models.TextField(_('description'), blank=True)
    
    # Photo file
    image = models.ImageField(_('image'), upload_to='job_photos/')
    
    # Metadata
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_job_photos')
    taken_at = models.DateTimeField(_('taken at'), auto_now_add=True)
    latitude = models.DecimalField(_('latitude'), max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(_('longitude'), max_digits=11, decimal_places=8, null=True, blank=True)
    
    # Web3 integration for photo authenticity
    photo_hash = models.CharField(_('photo hash'), max_length=66, blank=True)
    
    class Meta:
        verbose_name = _('Job Photo')
        verbose_name_plural = _('Job Photos')
        ordering = ['-taken_at']
    
    def __str__(self):
        return f"{self.job.job_id}: {self.photo_type} - {self.title or 'Untitled'}"


class JobMessage(BaseModel):
    """
    Messaging system for job-related communication between clients and freelancers.
    """
    MESSAGE_TYPES = [
        ('general', 'General'),
        ('question', 'Question'),
        ('update', 'Update'),
        ('issue', 'Issue'),
        ('requirement', 'Requirement'),
        ('feedback', 'Feedback'),
    ]
    
    job = models.ForeignKey(GigJob, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_job_messages')
    message_type = models.CharField(_('message type'), max_length=20, choices=MESSAGE_TYPES, default='general')
    
    # Message content
    subject = models.CharField(_('subject'), max_length=200, blank=True)
    content = models.TextField(_('content'))
    
    # Status
    is_read = models.BooleanField(_('is read'), default=False)
    read_at = models.DateTimeField(_('read at'), null=True, blank=True)
    
    # Attachments
    attachments = models.JSONField(_('attachments'), default=list)  # List of file URLs/paths
    
    class Meta:
        verbose_name = _('Job Message')
        verbose_name_plural = _('Job Messages')
        ordering = ['-created']
    
    def __str__(self):
        return f"{self.job.job_id}: {self.subject or 'No Subject'}"


class JobReview(BaseModel):
    """
    Reviews and ratings for completed jobs.
    """
    job = models.ForeignKey(GigJob, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_reviews_given')
    
    # Multi-criteria ratings (1-5 scale)
    overall_rating = models.IntegerField(_('overall rating'), 
                                        validators=[MinValueValidator(1), MaxValueValidator(5)])
    quality_rating = models.IntegerField(_('quality rating'), 
                                        validators=[MinValueValidator(1), MaxValueValidator(5)])
    timeliness_rating = models.IntegerField(_('timeliness rating'), 
                                           validators=[MinValueValidator(1), MaxValueValidator(5)])
    communication_rating = models.IntegerField(_('communication rating'), 
                                              validators=[MinValueValidator(1), MaxValueValidator(5)])
    professionalism_rating = models.IntegerField(_('professionalism rating'), 
                                                validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Review content
    title = models.CharField(_('review title'), max_length=200)
    comment = models.TextField(_('comment'))
    would_recommend = models.BooleanField(_('would recommend'), default=True)
    
    # Response from freelancer/client
    response = models.TextField(_('response'), blank=True)
    response_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='job_review_responses')
    response_at = models.DateTimeField(_('response at'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Job Review')
        verbose_name_plural = _('Job Reviews')
        ordering = ['-created']
        unique_together = ['job', 'reviewer']
        indexes = [
            models.Index(fields=['job', 'overall_rating']),
        ]
    
    def __str__(self):
        return f"Review for {self.job.title} by {self.reviewer.get_full_name()}"
    
    @property
    def average_rating(self):
        """Calculate average rating across all criteria."""
        ratings = [
            self.overall_rating,
            self.quality_rating,
            self.timeliness_rating,
            self.communication_rating,
            self.professionalism_rating
        ]
        return sum(ratings) / len(ratings)
