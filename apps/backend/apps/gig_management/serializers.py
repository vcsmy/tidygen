"""
Serializers for gig_management app API.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    GigCategory, GigJob, GigApplication, JobMilestone,
    JobPhoto, JobMessage, JobReview
)

User = get_user_model()


class GigCategorySerializer(serializers.ModelSerializer):
    """Serializer for gig categories."""
    job_count = serializers.SerializerMethodField()
    
    class Meta:
        model = GigCategory
        fields = [
            'id', 'name', 'description', 'icon', 'color', 'is_active',
            'default_hourly_rate_min', 'default_hourly_rate_max', 'job_count',
            'created', 'modified'
        ]
    
    def get_job_count(self, obj):
        return obj.jobs.filter(status__in=['published', 'assigned', 'in_progress', 'completed']).count()


class JobPhotoSerializer(serializers.ModelSerializer):
    """Serializer for job photos."""
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    
    class Meta:
        model = JobPhoto
        fields = [
            'id', 'photo_type', 'title', 'description', 'image',
            'uploaded_by', 'uploaded_by_name', 'taken_at', 'latitude', 'longitude',
            'photo_hash', 'created', 'modified'
        ]
        read_only_fields = ['id', 'uploaded_by', 'uploaded_by_name', 'taken_at', 'created', 'modified']


class JobMilestoneSerializer(serializers.ModelSerializer):
    """Serializer for job milestones."""
    milestone_type_display = serializers.CharField(source='get_milestone_type_display', read_only=True)
    completed_by_name = serializers.CharField(source='completed_by.get_full_name', read_only=True)
    photos = JobPhotoSerializer(many=True, read_only=True)
    
    class Meta:
        model = JobMilestone
        fields = [
            'id', 'milestone_type', 'milestone_type_display', 'title', 'description',
            'expected_date', 'actual_date', 'is_completed', 'completed_by', 'completed_by_name',
            'quality_score', 'quality_notes', 'payment_amount', 'payment_released',
            'payment_date', 'milestone_hash', 'photos', 'created', 'modified'
        ]
        read_only_fields = ['id', 'completed_by', 'created', 'modified']


class GigJobListSerializer(serializers.ModelSerializer):
    """Serializer for gig job list view."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    assigned_freelancer_name = serializers.CharField(source='assigned_freelancer.full_name', read_only=True)
    city_state = serializers.SerializerMethodField()
    total_cost = serializers.ReadOnlyField()
    
    class Meta:
        model = GigJob
        fields = [
            'id', 'job_id', 'title', 'category', 'category_name', 'client', 'client_name',
            'client_type', 'city_state', 'service_type', 'property_type',
            'preferred_start_date', 'estimated_duration_hours', 'payment_method',
            'hourly_rate', 'fixed_price', 'currency', 'total_cost', 'status',
            'priority', 'assigned_freelancer', 'assigned_freelancer_name', 'created', 'modified'
        ]
    
    def get_city_state(self, obj):
        return f"{obj.city}, {obj.state}"


class GigJobDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed gig job view."""
    category = GigCategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    assigned_freelancer_name = serializers.CharField(source='assigned_freelancer.full_name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    full_address = serializers.ReadOnlyField()
    total_cost = serializers.ReadOnlyField()
    
    # Related data
    applications = serializers.SerializerMethodField()
    milestones = JobMilestoneSerializer(many=True, read_only=True)
    photos = JobPhotoSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = GigJob
        fields = [
            'id', 'job_id', 'title', 'description', 'category', 'category_id',
            'client', 'client_name', 'client_type', 'service_address', 'city', 'state',
            'postal_code', 'country', 'full_address', 'service_type', 'property_type',
            'property_size', 'preferred_start_date', 'preferred_end_date',
            'actual_start_date', 'actual_end_date', 'estimated_duration_hours',
            'actual_duration_hours', 'payment_method', 'hourly_rate', 'fixed_price',
            'currency', 'total_cost', 'required_skills', 'required_certifications',
            'special_requirements', 'assigned_freelancer', 'assigned_freelancer_name',
            'assigned_at', 'assigned_by', 'assigned_by_name', 'status', 'priority',
            'client_rating', 'client_feedback', 'freelancer_rating', 'freelancer_feedback',
            'smart_contract_address', 'blockchain_transaction_hash', 'nft_job_badge',
            'is_urgent', 'requires_background_check', 'allows_multiple_freelancers',
            'max_freelancers', 'applications', 'milestones', 'photos', 'messages', 'reviews',
            'created', 'modified'
        ]
        read_only_fields = [
            'id', 'job_id', 'created', 'modified', 'assigned_at', 'assigned_by',
            'actual_start_date', 'actual_end_date', 'actual_duration_hours'
        ]
    
    def get_applications(self, obj):
        # Only show applications to job owners and assigned freelancers
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if (request.user == obj.client or 
                (obj.assigned_freelancer and request.user == obj.assigned_freelancer.user)):
                # Avoid circular import - define inline serializer
                return [
                    {
                        'id': app.id,
                        'freelancer': app.freelancer.id,
                        'freelancer_name': app.freelancer.full_name,
                        'cover_letter': app.cover_letter,
                        'proposed_rate': app.proposed_rate,
                        'status': app.status,
                        'created': app.created
                    }
                    for app in obj.applications.all()
                ]
        return []
    
    def get_messages(self, obj):
        # Only show messages to related users
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if (request.user == obj.client or 
                (obj.assigned_freelancer and request.user == obj.assigned_freelancer.user)):
                # Avoid circular import - define inline serializer
                return [
                    {
                        'id': msg.id,
                        'sender': msg.sender.id,
                        'sender_name': msg.sender.get_full_name(),
                        'message_type': msg.message_type,
                        'subject': msg.subject,
                        'content': msg.content,
                        'is_read': msg.is_read,
                        'created': msg.created
                    }
                    for msg in obj.messages.all()[:10]
                ]
        return []
    
    def get_reviews(self, obj):
        # Avoid circular import - define inline serializer
        return [
            {
                'id': review.id,
                'reviewer': review.reviewer.id,
                'reviewer_name': review.reviewer.get_full_name(),
                'overall_rating': review.overall_rating,
                'quality_rating': review.quality_rating,
                'title': review.title,
                'comment': review.comment,
                'would_recommend': review.would_recommend,
                'average_rating': review.average_rating,
                'created': review.created
            }
            for review in obj.reviews.all()
        ]


class GigJobCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new gig jobs."""
    
    class Meta:
        model = GigJob
        fields = [
            'title', 'description', 'category', 'client_type', 'service_address',
            'city', 'state', 'postal_code', 'country', 'service_type', 'property_type',
            'property_size', 'preferred_start_date', 'preferred_end_date',
            'estimated_duration_hours', 'payment_method', 'hourly_rate', 'fixed_price',
            'currency', 'required_skills', 'required_certifications', 'special_requirements',
            'priority', 'is_urgent', 'requires_background_check', 'allows_multiple_freelancers',
            'max_freelancers'
        ]
    
    def create(self, validated_data):
        # Generate job ID
        validated_data['job_id'] = self._generate_job_id()
        return super().create(validated_data)
    
    def _generate_job_id(self):
        """Generate a unique job ID."""
        import uuid
        return f"GIG{str(uuid.uuid4())[:8].upper()}"


class GigApplicationSerializer(serializers.ModelSerializer):
    """Serializer for gig applications."""
    freelancer_name = serializers.CharField(source='freelancer.full_name', read_only=True)
    freelancer_rating = serializers.DecimalField(source='freelancer.rating', max_digits=3, decimal_places=2, read_only=True)
    freelancer_location = serializers.SerializerMethodField()
    job_title = serializers.CharField(source='job.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)
    
    class Meta:
        model = GigApplication
        fields = [
            'id', 'job', 'job_title', 'freelancer', 'freelancer_name', 'freelancer_rating',
            'freelancer_location', 'cover_letter', 'proposed_rate', 'estimated_completion_time',
            'availability_start', 'availability_end', 'status', 'status_display',
            'reviewed_by', 'reviewed_by_name', 'reviewed_at', 'review_notes',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'freelancer', 'job', 'created', 'modified']
    
    def get_freelancer_location(self, obj):
        return f"{obj.freelancer.city}, {obj.freelancer.state}"


class GigApplicationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new gig applications."""
    
    class Meta:
        model = GigApplication
        fields = [
            'job', 'cover_letter', 'proposed_rate', 'estimated_completion_time',
            'availability_start', 'availability_end'
        ]
    
    def create(self, validated_data):
        # Set the freelancer from the current user
        freelancer = self.context['request'].user.freelancer_profile
        validated_data['freelancer'] = freelancer
        return super().create(validated_data)
    
    def validate_job(self, value):
        """Ensure freelancer can apply to this job."""
        if value.status != 'published':
            raise serializers.ValidationError("Can only apply to published jobs.")
        
        # Check if already applied
        freelancer = self.context['request'].user.freelancer_profile
        if GigApplication.objects.filter(job=value, freelancer=freelancer).exists():
            raise serializers.ValidationError("You have already applied to this job.")
        
        return value


class JobMilestoneCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating job milestones."""
    
    class Meta:
        model = JobMilestone
        fields = [
            'job', 'milestone_type', 'title', 'description', 'expected_date'
        ]


class JobPhotoUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading job photos."""
    
    class Meta:
        model = JobPhoto
        fields = [
            'job', 'milestone', 'photo_type', 'title', 'description', 'image',
            'latitude', 'longitude'
        ]
    
    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


class JobMessageSerializer(serializers.ModelSerializer):
    """Serializer for job messages."""
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    message_type_display = serializers.CharField(source='get_message_type_display', read_only=True)
    
    class Meta:
        model = JobMessage
        fields = [
            'id', 'job', 'sender', 'sender_name', 'message_type', 'message_type_display',
            'subject', 'content', 'is_read', 'read_at', 'attachments',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'sender', 'created', 'modified']


class JobMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating job messages."""
    
    class Meta:
        model = JobMessage
        fields = [
            'job', 'message_type', 'subject', 'content', 'attachments'
        ]
    
    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class JobReviewSerializer(serializers.ModelSerializer):
    """Serializer for job reviews."""
    reviewer_name = serializers.CharField(source='reviewer.get_full_name', read_only=True)
    response_by_name = serializers.CharField(source='response_by.get_full_name', read_only=True)
    average_rating = serializers.ReadOnlyField()
    
    class Meta:
        model = JobReview
        fields = [
            'id', 'job', 'reviewer', 'reviewer_name', 'overall_rating', 'quality_rating',
            'timeliness_rating', 'communication_rating', 'professionalism_rating',
            'title', 'comment', 'would_recommend', 'response', 'response_by',
            'response_by_name', 'response_at', 'average_rating', 'created', 'modified'
        ]
        read_only_fields = ['id', 'reviewer', 'created', 'modified', 'response_at']
