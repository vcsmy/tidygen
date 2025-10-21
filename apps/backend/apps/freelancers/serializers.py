"""
Serializers for freelancers app API.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Freelancer, FreelancerDocument, FreelancerAvailability,
    FreelancerSkill, FreelancerSkillAssignment, FreelancerReview
)

User = get_user_model()


class FreelancerDocumentSerializer(serializers.ModelSerializer):
    """Serializer for freelancer documents."""
    
    class Meta:
        model = FreelancerDocument
        fields = [
            'id', 'document_type', 'title', 'description', 'file',
            'file_size', 'is_verified', 'verified_by', 'verified_at',
            'verification_notes', 'expiry_date', 'is_expired',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'file_size', 'verified_by', 'verified_at', 'created', 'modified']


class FreelancerAvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for freelancer availability."""
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = FreelancerAvailability
        fields = [
            'id', 'day_of_week', 'day_of_week_display', 'start_time', 'end_time',
            'is_available', 'notes', 'is_recurring', 'specific_dates',
            'created', 'modified'
        ]


class FreelancerSkillSerializer(serializers.ModelSerializer):
    """Serializer for freelancer skills."""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = FreelancerSkill
        fields = [
            'id', 'name', 'category', 'category_display', 'description',
            'is_certification_required', 'created', 'modified'
        ]


class FreelancerSkillAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for freelancer skill assignments."""
    skill = FreelancerSkillSerializer(read_only=True)
    skill_id = serializers.IntegerField(write_only=True)
    proficiency_level_display = serializers.CharField(source='get_proficiency_level_display', read_only=True)
    
    class Meta:
        model = FreelancerSkillAssignment
        fields = [
            'id', 'skill', 'skill_id', 'proficiency_level', 'proficiency_level_display',
            'years_of_experience', 'certification_date', 'certification_body',
            'certification_number', 'notes', 'created', 'modified'
        ]


class FreelancerReviewSerializer(serializers.ModelSerializer):
    """Serializer for freelancer reviews."""
    reviewer_name = serializers.CharField(source='reviewer.get_full_name', read_only=True)
    average_rating = serializers.ReadOnlyField()
    
    class Meta:
        model = FreelancerReview
        fields = [
            'id', 'reviewer', 'reviewer_name', 'overall_rating', 'quality_rating',
            'punctuality_rating', 'communication_rating', 'professionalism_rating',
            'title', 'comment', 'would_recommend', 'job_reference', 'average_rating',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'reviewer', 'created', 'modified']


class FreelancerListSerializer(serializers.ModelSerializer):
    """Serializer for freelancer list view (minimal data)."""
    full_name = serializers.ReadOnlyField()
    city_state = serializers.SerializerMethodField()
    cleaning_types_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Freelancer
        fields = [
            'id', 'freelancer_id', 'full_name', 'city_state', 'rating',
            'total_jobs_completed', 'cleaning_types', 'cleaning_types_display',
            'hourly_rate', 'currency', 'is_available', 'status', 'profile_picture'
        ]
    
    def get_city_state(self, obj):
        return f"{obj.city}, {obj.state}"
    
    def get_cleaning_types_display(self, obj):
        return ', '.join(obj.cleaning_types) if obj.cleaning_types else ''


class FreelancerDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed freelancer view."""
    full_name = serializers.ReadOnlyField()
    full_address = serializers.ReadOnlyField()
    is_eligible_for_jobs = serializers.ReadOnlyField()
    
    # Related data
    documents = FreelancerDocumentSerializer(many=True, read_only=True)
    availability_slots = FreelancerAvailabilitySerializer(many=True, read_only=True)
    skill_assignments = FreelancerSkillAssignmentSerializer(many=True, read_only=True)
    reviews = FreelancerReviewSerializer(many=True, read_only=True)
    
    # User information
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    class Meta:
        model = Freelancer
        fields = [
            'id', 'freelancer_id', 'user', 'user_email', 'user_first_name', 'user_last_name',
            'first_name', 'last_name', 'middle_name', 'full_name', 'date_of_birth',
            'gender', 'nationality', 'personal_email', 'personal_phone',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
            'full_address', 'service_areas', 'max_travel_distance', 'cleaning_types',
            'special_skills', 'certifications', 'years_of_experience',
            'availability_schedule', 'is_available', 'last_activity',
            'rating', 'total_jobs_completed', 'on_time_percentage', 'completion_rate',
            'hourly_rate', 'currency', 'payment_method', 'wallet_address',
            'blockchain_verified', 'nft_badge_id', 'status', 'verification_status',
            'background_check_completed', 'background_check_date', 'background_check_reference',
            'insurance_provider', 'insurance_policy_number', 'insurance_expiry_date',
            'bio', 'profile_picture', 'preferred_language', 'timezone',
            'is_eligible_for_jobs', 'documents', 'availability_slots', 'skill_assignments', 'reviews',
            'created', 'modified'
        ]
        read_only_fields = [
            'id', 'freelancer_id', 'created', 'modified', 'last_activity',
            'rating', 'total_jobs_completed', 'on_time_percentage', 'completion_rate'
        ]


class FreelancerCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new freelancers."""
    
    class Meta:
        model = Freelancer
        fields = [
            'user', 'first_name', 'last_name', 'middle_name', 'date_of_birth',
            'gender', 'nationality', 'personal_email', 'personal_phone',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
            'service_areas', 'max_travel_distance', 'cleaning_types', 'special_skills',
            'certifications', 'years_of_experience', 'availability_schedule',
            'hourly_rate', 'currency', 'payment_method', 'wallet_address',
            'bio', 'profile_picture', 'preferred_language', 'timezone'
        ]
    
    def create(self, validated_data):
        # Generate freelancer ID
        validated_data['freelancer_id'] = self._generate_freelancer_id()
        return super().create(validated_data)
    
    def _generate_freelancer_id(self):
        """Generate a unique freelancer ID."""
        import uuid
        return f"FL{str(uuid.uuid4())[:8].upper()}"


class FreelancerUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating freelancer information."""
    
    class Meta:
        model = Freelancer
        fields = [
            'first_name', 'last_name', 'middle_name', 'date_of_birth',
            'gender', 'nationality', 'personal_email', 'personal_phone',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
            'service_areas', 'max_travel_distance', 'cleaning_types', 'special_skills',
            'certifications', 'years_of_experience', 'availability_schedule',
            'is_available', 'hourly_rate', 'currency', 'payment_method', 'wallet_address',
            'bio', 'profile_picture', 'preferred_language', 'timezone',
            'insurance_provider', 'insurance_policy_number', 'insurance_expiry_date'
        ]


class FreelancerAvailabilityUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating freelancer availability."""
    
    class Meta:
        model = FreelancerAvailability
        fields = [
            'day_of_week', 'start_time', 'end_time', 'is_available',
            'notes', 'is_recurring', 'specific_dates'
        ]
    
    def validate(self, data):
        """Validate availability time ranges."""
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("Start time must be before end time.")
        return data


class FreelancerDocumentUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading freelancer documents."""
    
    class Meta:
        model = FreelancerDocument
        fields = [
            'document_type', 'title', 'description', 'file', 'expiry_date'
        ]
    
    def create(self, validated_data):
        # Associate with the current freelancer from context
        freelancer = self.context.get('freelancer')
        if freelancer:
            validated_data['freelancer'] = freelancer
        return super().create(validated_data)
