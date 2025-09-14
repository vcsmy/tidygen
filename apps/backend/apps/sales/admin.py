"""
Django admin configuration for sales and client management models.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from apps.sales.models import (
    Client, IndividualClient, CorporateClient, ClientContact, ClientNote,
    ClientDocument, ClientTag, ClientTagAssignment, ClientInteraction,
    ClientSegment, ClientSegmentAssignment
)


class ClientContactInline(admin.TabularInline):
    model = ClientContact
    extra = 0
    fields = ['first_name', 'last_name', 'email', 'phone', 'job_title', 'is_primary', 'is_decision_maker']


class ClientNoteInline(admin.TabularInline):
    model = ClientNote
    extra = 0
    fields = ['note_type', 'title', 'content', 'related_user', 'is_private']
    readonly_fields = ['created']


class ClientDocumentInline(admin.TabularInline):
    model = ClientDocument
    extra = 0
    fields = ['document_type', 'title', 'file', 'is_public', 'expiry_date']
    readonly_fields = ['created']


class ClientTagAssignmentInline(admin.TabularInline):
    model = ClientTagAssignment
    extra = 0
    fields = ['tag', 'assigned_by']


class ClientSegmentAssignmentInline(admin.TabularInline):
    model = ClientSegmentAssignment
    extra = 0
    fields = ['segment', 'assigned_by', 'assigned_date']
    readonly_fields = ['assigned_date']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = [
        'display_name', 'client_type', 'status', 'priority', 'email', 'phone',
        'city', 'assigned_to', 'last_contact_date', 'created'
    ]
    list_filter = [
        'client_type', 'status', 'priority', 'industry', 'company_size',
        'assigned_to', 'created_by', 'marketing_consent', 'newsletter_subscription'
    ]
    search_fields = [
        'email', 'phone', 'city', 'state', 'country', 'industry', 'source'
    ]
    ordering = ['-created']
    list_editable = ['status', 'priority']
    inlines = [ClientContactInline, ClientNoteInline, ClientDocumentInline, ClientTagAssignmentInline, ClientSegmentAssignmentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('client_type', 'status', 'priority', 'assigned_to', 'created_by')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'website', 'preferred_contact_method')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Business Information', {
            'fields': ('industry', 'company_size', 'source', 'notes')
        }),
        ('Financial Information', {
            'fields': ('credit_limit', 'payment_terms', 'tax_id', 'currency')
        }),
        ('Preferences', {
            'fields': ('marketing_consent', 'newsletter_subscription')
        }),
        ('Tracking', {
            'fields': ('last_contact_date', 'last_activity_date'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['last_contact_date', 'last_activity_date']
    
    def display_name(self, obj):
        return obj.display_name
    display_name.short_description = 'Name'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'assigned_to', 'created_by', 'individual_client', 'corporate_client'
        )


@admin.register(IndividualClient)
class IndividualClientAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'client', 'date_of_birth', 'gender', 'job_title',
        'company', 'nationality'
    ]
    list_filter = ['gender', 'nationality', 'language_preference', 'timezone']
    search_fields = ['first_name', 'last_name', 'job_title', 'company']
    ordering = ['last_name', 'first_name']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('client', 'first_name', 'last_name', 'middle_name', 'date_of_birth', 'gender')
        }),
        ('Professional Information', {
            'fields': ('job_title', 'department', 'company')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship')
        }),
        ('Additional Information', {
            'fields': ('nationality', 'language_preference', 'timezone')
        }),
    )
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Full Name'


@admin.register(CorporateClient)
class CorporateClientAdmin(admin.ModelAdmin):
    list_display = [
        'company_name', 'client', 'business_type', 'founded_year',
        'annual_revenue', 'ceo_name'
    ]
    list_filter = ['business_type', 'founded_year']
    search_fields = ['company_name', 'legal_name', 'ceo_name', 'cfo_name', 'cto_name']
    ordering = ['company_name']
    
    fieldsets = (
        ('Company Information', {
            'fields': ('client', 'company_name', 'legal_name', 'registration_number', 'tax_registration_number')
        }),
        ('Business Details', {
            'fields': ('business_type', 'founded_year', 'annual_revenue', 'business_description')
        }),
        ('Key Personnel', {
            'fields': ('ceo_name', 'cfo_name', 'cto_name')
        }),
        ('Corporate Structure', {
            'fields': ('parent_company', 'subsidiaries')
        }),
    )


@admin.register(ClientContact)
class ClientContactAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'client', 'email', 'phone', 'job_title',
        'is_primary', 'is_decision_maker'
    ]
    list_filter = ['is_primary', 'is_decision_maker', 'preferred_contact_method']
    search_fields = ['first_name', 'last_name', 'email', 'job_title']
    ordering = ['-is_primary', 'last_name', 'first_name']
    list_editable = ['is_primary', 'is_decision_maker']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('client', 'first_name', 'last_name', 'email', 'phone', 'mobile')
        }),
        ('Professional Information', {
            'fields': ('job_title', 'department')
        }),
        ('Contact Preferences', {
            'fields': ('is_primary', 'is_decision_maker', 'preferred_contact_method', 'notes')
        }),
    )
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Full Name'


@admin.register(ClientNote)
class ClientNoteAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'client', 'note_type', 'related_user', 'is_private', 'created'
    ]
    list_filter = ['note_type', 'is_private', 'related_user', 'created']
    search_fields = ['title', 'content', 'client__email']
    ordering = ['-created']
    
    fieldsets = (
        ('Note Information', {
            'fields': ('client', 'note_type', 'title', 'content')
        }),
        ('Related Information', {
            'fields': ('related_user', 'related_date', 'is_private')
        }),
    )
    
    readonly_fields = ['created']


@admin.register(ClientDocument)
class ClientDocumentAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'client', 'document_type', 'file_size_mb', 'uploaded_by',
        'is_public', 'expiry_date', 'created'
    ]
    list_filter = ['document_type', 'is_public', 'uploaded_by', 'created']
    search_fields = ['title', 'description', 'client__email']
    ordering = ['-created']
    
    fieldsets = (
        ('Document Information', {
            'fields': ('client', 'document_type', 'title', 'description')
        }),
        ('File Information', {
            'fields': ('file', 'file_size', 'is_public', 'expiry_date')
        }),
        ('Upload Information', {
            'fields': ('uploaded_by',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['file_size', 'created']
    
    def file_size_mb(self, obj):
        if obj.file_size:
            return f"{round(obj.file_size / (1024 * 1024), 2)} MB"
        return "Unknown"
    file_size_mb.short_description = 'File Size'


@admin.register(ClientTag)
class ClientTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_display', 'description', 'created']
    list_filter = ['created']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    fieldsets = (
        ('Tag Information', {
            'fields': ('name', 'color', 'description')
        }),
    )
    
    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px;">{}</span>',
            obj.color,
            obj.color
        )
    color_display.short_description = 'Color'


@admin.register(ClientTagAssignment)
class ClientTagAssignmentAdmin(admin.ModelAdmin):
    list_display = ['client', 'tag', 'assigned_by', 'created']
    list_filter = ['tag', 'assigned_by', 'created']
    search_fields = ['client__email', 'tag__name']
    ordering = ['-created']
    
    fieldsets = (
        ('Assignment Information', {
            'fields': ('client', 'tag', 'assigned_by')
        }),
    )


@admin.register(ClientInteraction)
class ClientInteractionAdmin(admin.ModelAdmin):
    list_display = [
        'subject', 'client', 'interaction_type', 'initiated_by',
        'duration_minutes', 'requires_follow_up', 'created'
    ]
    list_filter = [
        'interaction_type', 'initiated_by', 'requires_follow_up', 'created'
    ]
    search_fields = ['subject', 'description', 'client__email']
    ordering = ['-created']
    
    fieldsets = (
        ('Interaction Information', {
            'fields': ('client', 'interaction_type', 'subject', 'description')
        }),
        ('Interaction Details', {
            'fields': ('initiated_by', 'duration_minutes', 'outcome')
        }),
        ('Follow-up Information', {
            'fields': ('requires_follow_up', 'follow_up_date', 'follow_up_notes')
        }),
    )


@admin.register(ClientSegment)
class ClientSegmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_display', 'is_active', 'client_count', 'created']
    list_filter = ['is_active', 'created']
    search_fields = ['name', 'description']
    ordering = ['name']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Segment Information', {
            'fields': ('name', 'description', 'color', 'is_active')
        }),
        ('Segmentation Criteria', {
            'fields': ('criteria',),
            'classes': ('collapse',)
        }),
    )
    
    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px;">{}</span>',
            obj.color,
            obj.color
        )
    color_display.short_description = 'Color'
    
    def client_count(self, obj):
        return obj.client_assignments.count()
    client_count.short_description = 'Clients'


@admin.register(ClientSegmentAssignment)
class ClientSegmentAssignmentAdmin(admin.ModelAdmin):
    list_display = ['client', 'segment', 'assigned_by', 'assigned_date']
    list_filter = ['segment', 'assigned_by', 'assigned_date']
    search_fields = ['client__email', 'segment__name']
    ordering = ['-assigned_date']
    
    fieldsets = (
        ('Assignment Information', {
            'fields': ('client', 'segment', 'assigned_by', 'assigned_date')
        }),
    )
    
    readonly_fields = ['assigned_date']


# Customize admin site
admin.site.site_header = "TidyGen ERP Client Management"
admin.site.site_title = "TidyGen Client Admin"
admin.site.index_title = "Client Management Administration"
