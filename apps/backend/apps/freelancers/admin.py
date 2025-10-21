"""
Admin configuration for freelancers app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Freelancer, FreelancerDocument, FreelancerAvailability,
    FreelancerSkill, FreelancerSkillAssignment, FreelancerReview
)


@admin.register(Freelancer)
class FreelancerAdmin(admin.ModelAdmin):
    list_display = [
        'freelancer_id', 'full_name', 'status', 'verification_status', 
        'rating', 'city', 'is_available', 'background_check_completed'
    ]
    list_filter = [
        'status', 'verification_status', 'background_check_completed',
        'is_available', 'city', 'state', 'created'
    ]
    search_fields = [
        'freelancer_id', 'first_name', 'last_name', 'personal_email',
        'personal_phone', 'city', 'state'
    ]
    readonly_fields = ['freelancer_id', 'created', 'modified', 'last_activity']
    
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'user', 'freelancer_id', 'first_name', 'last_name', 'middle_name',
                'date_of_birth', 'gender', 'nationality'
            )
        }),
        ('Contact Information', {
            'fields': (
                'personal_email', 'personal_phone', 'emergency_contact_name',
                'emergency_contact_phone', 'emergency_contact_relationship'
            )
        }),
        ('Location & Service Areas', {
            'fields': (
                'address_line1', 'address_line2', 'city', 'state', 'postal_code',
                'country', 'service_areas', 'max_travel_distance'
            )
        }),
        ('Services & Skills', {
            'fields': (
                'cleaning_types', 'special_skills', 'certifications',
                'years_of_experience'
            )
        }),
        ('Availability & Performance', {
            'fields': (
                'availability_schedule', 'is_available', 'rating',
                'total_jobs_completed', 'on_time_percentage', 'completion_rate'
            )
        }),
        ('Financial', {
            'fields': (
                'hourly_rate', 'currency', 'payment_method'
            )
        }),
        ('Web3 Integration', {
            'fields': (
                'wallet_address', 'blockchain_verified', 'nft_badge_id'
            ),
            'classes': ('collapse',)
        }),
        ('Verification & Status', {
            'fields': (
                'status', 'verification_status', 'background_check_completed',
                'background_check_date', 'background_check_reference'
            )
        }),
        ('Insurance', {
            'fields': (
                'insurance_provider', 'insurance_policy_number', 'insurance_expiry_date'
            ),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': (
                'bio', 'profile_picture', 'preferred_language', 'timezone',
                'created', 'modified', 'last_activity'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(FreelancerDocument)
class FreelancerDocumentAdmin(admin.ModelAdmin):
    list_display = [
        'freelancer', 'document_type', 'title', 'is_verified', 
        'expiry_date', 'uploaded_date'
    ]
    list_filter = [
        'document_type', 'is_verified', 'is_expired', 'created'
    ]
    search_fields = [
        'freelancer__first_name', 'freelancer__last_name', 'title'
    ]
    readonly_fields = ['created', 'modified']
    
    def uploaded_date(self, obj):
        return obj.created.strftime('%Y-%m-%d')
    uploaded_date.short_description = 'Uploaded Date'


@admin.register(FreelancerAvailability)
class FreelancerAvailabilityAdmin(admin.ModelAdmin):
    list_display = [
        'freelancer', 'day_of_week_name', 'time_range', 'is_available'
    ]
    list_filter = [
        'day_of_week', 'is_available', 'is_recurring'
    ]
    search_fields = [
        'freelancer__first_name', 'freelancer__last_name'
    ]
    
    def day_of_week_name(self, obj):
        return obj.get_day_of_week_display()
    day_of_week_name.short_description = 'Day'
    
    def time_range(self, obj):
        return f"{obj.start_time} - {obj.end_time}"
    time_range.short_description = 'Time Range'


@admin.register(FreelancerSkill)
class FreelancerSkillAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'is_certification_required'
    ]
    list_filter = [
        'category', 'is_certification_required'
    ]
    search_fields = ['name', 'description']


@admin.register(FreelancerSkillAssignment)
class FreelancerSkillAssignmentAdmin(admin.ModelAdmin):
    list_display = [
        'freelancer', 'skill', 'proficiency_level', 'years_of_experience'
    ]
    list_filter = [
        'proficiency_level', 'skill__category'
    ]
    search_fields = [
        'freelancer__first_name', 'freelancer__last_name', 'skill__name'
    ]


@admin.register(FreelancerReview)
class FreelancerReviewAdmin(admin.ModelAdmin):
    list_display = [
        'freelancer', 'reviewer', 'overall_rating', 'average_rating_display',
        'would_recommend', 'created'
    ]
    list_filter = [
        'overall_rating', 'would_recommend', 'created'
    ]
    search_fields = [
        'freelancer__first_name', 'freelancer__last_name',
        'reviewer__first_name', 'reviewer__last_name'
    ]
    readonly_fields = ['created', 'modified']
    
    def average_rating_display(self, obj):
        return f"{obj.average_rating:.2f}"
    average_rating_display.short_description = 'Average Rating'
