"""
Admin configuration for gig_management app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    GigCategory, GigJob, GigApplication, JobMilestone, 
    JobPhoto, JobMessage, JobReview
)


@admin.register(GigCategory)
class GigCategoryAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'is_active', 'default_hourly_rate_min', 
        'default_hourly_rate_max', 'job_count'
    ]
    list_filter = ['is_active', 'created']
    search_fields = ['name', 'description']
    readonly_fields = ['created', 'modified']
    
    def job_count(self, obj):
        return obj.jobs.count()
    job_count.short_description = 'Jobs'


@admin.register(GigJob)
class GigJobAdmin(admin.ModelAdmin):
    list_display = [
        'job_id', 'title', 'client', 'category', 'status', 'priority',
        'city', 'assigned_freelancer', 'created_date'
    ]
    list_filter = [
        'status', 'priority', 'payment_method', 'category', 'city', 'state', 'created'
    ]
    search_fields = [
        'job_id', 'title', 'client__first_name', 'client__last_name',
        'assigned_freelancer__first_name', 'assigned_freelancer__last_name'
    ]
    readonly_fields = ['job_id', 'created', 'modified']
    
    fieldsets = (
        ('Job Information', {
            'fields': (
                'job_id', 'title', 'description', 'category', 'status', 'priority'
            )
        }),
        ('Client Information', {
            'fields': (
                'client', 'client_type', 'service_address', 'city', 'state', 
                'postal_code', 'country'
            )
        }),
        ('Service Details', {
            'fields': (
                'service_type', 'property_type', 'property_size',
                'required_skills', 'required_certifications', 'special_requirements'
            )
        }),
        ('Scheduling', {
            'fields': (
                'preferred_start_date', 'preferred_end_date', 'actual_start_date',
                'actual_end_date', 'estimated_duration_hours', 'actual_duration_hours'
            )
        }),
        ('Pricing & Payment', {
            'fields': (
                'payment_method', 'hourly_rate', 'fixed_price', 'currency'
            )
        }),
        ('Assignment', {
            'fields': (
                'assigned_freelancer', 'assigned_at', 'assigned_by'
            )
        }),
        ('Reviews & Ratings', {
            'fields': (
                'client_rating', 'client_feedback', 'freelancer_rating', 'freelancer_feedback'
            ),
            'classes': ('collapse',)
        }),
        ('Web3 Integration', {
            'fields': (
                'smart_contract_address', 'blockchain_transaction_hash', 'nft_job_badge'
            ),
            'classes': ('collapse',)
        }),
        ('Additional Options', {
            'fields': (
                'is_urgent', 'requires_background_check', 'allows_multiple_freelancers',
                'max_freelancers', 'created', 'modified'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def created_date(self, obj):
        return obj.created.strftime('%Y-%m-%d')
    created_date.short_description = 'Created'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'client', 'category', 'assigned_freelancer', 'assigned_by'
        )


@admin.register(GigApplication)
class GigApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'freelancer_name', 'job_title', 'status', 'proposed_rate',
        'estimated_completion_time', 'created_date'
    ]
    list_filter = [
        'status', 'job__category', 'created'
    ]
    search_fields = [
        'job__title', 'freelancer__first_name', 'freelancer__last_name'
    ]
    readonly_fields = ['created', 'modified']
    
    def freelancer_name(self, obj):
        return obj.freelancer.full_name
    freelancer_name.short_description = 'Freelancer'
    
    def job_title(self, obj):
        return obj.job.title
    job_title.short_description = 'Job'
    
    def created_date(self, obj):
        return obj.created.strftime('%Y-%m-%d')
    created_date.short_description = 'Applied'


@admin.register(JobMilestone)
class JobMilestoneAdmin(admin.ModelAdmin):
    list_display = [
        'job_job_id', 'milestone_type', 'title', 'is_completed',
        'expected_date', 'actual_date', 'payment_amount'
    ]
    list_filter = [
        'milestone_type', 'is_completed', 'payment_released', 'created'
    ]
    search_fields = [
        'job__job_id', 'job__title', 'title', 'description'
    ]
    readonly_fields = ['created', 'modified']
    
    def job_job_id(self, obj):
        return obj.job.job_id
    job_job_id.short_description = 'Job ID'


@admin.register(JobPhoto)
class JobPhotoAdmin(admin.ModelAdmin):
    list_display = [
        'job_job_id', 'photo_type', 'title', 'uploaded_by', 'taken_at_date'
    ]
    list_filter = [
        'photo_type', 'created'
    ]
    search_fields = [
        'job__job_id', 'title', 'uploaded_by__first_name', 'uploaded_by__last_name'
    ]
    readonly_fields = ['uploaded_by', 'taken_at', 'created', 'modified']
    
    def job_job_id(self, obj):
        return obj.job.job_id
    job_job_id.short_description = 'Job ID'
    
    def taken_at_date(self, obj):
        return obj.taken_at.strftime('%Y-%m-%d %H:%M')
    taken_at_date.short_description = 'Taken At'


@admin.register(JobMessage)
class JobMessageAdmin(admin.ModelAdmin):
    list_display = [
        'job_job_id', 'sender_name', 'message_type', 'subject', 'is_read', 'created_date'
    ]
    list_filter = [
        'message_type', 'is_read', 'created'
    ]
    search_fields = [
        'job__job_id', 'subject', 'content', 'sender__first_name', 'sender__last_name'
    ]
    readonly_fields = ['created', 'modified']
    
    def job_job_id(self, obj):
        return obj.job.job_id
    job_job_id.short_description = 'Job ID'
    
    def sender_name(self, obj):
        return obj.sender.get_full_name()
    sender_name.short_description = 'Sender'
    
    def created_date(self, obj):
        return obj.created.strftime('%Y-%m-%d')
    created_date.short_description = 'Sent'


@admin.register(JobReview)
class JobReviewAdmin(admin.ModelAdmin):
    list_display = [
        'job_job_id', 'reviewer_name', 'overall_rating', 'average_rating_display',
        'would_recommend', 'created_date'
    ]
    list_filter = [
        'overall_rating', 'would_recommend', 'created'
    ]
    search_fields = [
        'job__job_id', 'job__title', 'reviewer__first_name', 'reviewer__last_name'
    ]
    readonly_fields = ['created', 'modified', 'response_at']
    
    def job_job_id(self, obj):
        return obj.job.job_id
    job_job_id.short_description = 'Job ID'
    
    def reviewer_name(self, obj):
        return obj.reviewer.get_full_name()
    reviewer_name.short_description = 'Reviewer'
    
    def average_rating_display(self, obj):
        return f"{obj.average_rating:.2f}"
    average_rating_display.short_description = 'Average Rating'
    
    def created_date(self, obj):
        return obj.created.strftime('%Y-%m-%d')
    created_date.short_description = 'Reviewed'
