"""
Sales and client management filters for TidyGen ERP platform.
"""
import django_filters
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from apps.sales.models import (
    Client, IndividualClient, CorporateClient, ClientContact, ClientNote,
    ClientDocument, ClientTag, ClientInteraction, ClientSegment
)


class ClientFilter(django_filters.FilterSet):
    """Filter for Client model."""
    # Basic filters
    client_type = django_filters.ChoiceFilter(choices=Client.CLIENT_TYPES)
    status = django_filters.ChoiceFilter(choices=Client.STATUS_CHOICES)
    priority = django_filters.ChoiceFilter(choices=Client.PRIORITY_CHOICES)
    
    # Contact information filters
    email = django_filters.CharFilter(lookup_expr='icontains')
    phone = django_filters.CharFilter(lookup_expr='icontains')
    
    # Address filters
    city = django_filters.CharFilter(lookup_expr='icontains')
    state = django_filters.CharFilter(lookup_expr='icontains')
    country = django_filters.CharFilter(lookup_expr='icontains')
    postal_code = django_filters.CharFilter(lookup_expr='icontains')
    
    # Business filters
    industry = django_filters.CharFilter(lookup_expr='icontains')
    company_size = django_filters.ChoiceFilter(choices=Client._meta.get_field('company_size').choices)
    source = django_filters.CharFilter(lookup_expr='icontains')
    
    # Assignment filters
    assigned_to = django_filters.ModelChoiceFilter(queryset=Client._meta.get_field('assigned_to').related_model.objects.all())
    created_by = django_filters.ModelChoiceFilter(queryset=Client._meta.get_field('created_by').related_model.objects.all())
    
    # Financial filters
    credit_limit_min = django_filters.NumberFilter(field_name='credit_limit', lookup_expr='gte')
    credit_limit_max = django_filters.NumberFilter(field_name='credit_limit', lookup_expr='lte')
    payment_terms_min = django_filters.NumberFilter(field_name='payment_terms', lookup_expr='gte')
    payment_terms_max = django_filters.NumberFilter(field_name='payment_terms', lookup_expr='lte')
    
    # Date range filters
    created_after = django_filters.DateFilter(field_name='created', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created', lookup_expr='lte')
    last_contact_after = django_filters.DateFilter(field_name='last_contact_date', lookup_expr='gte')
    last_contact_before = django_filters.DateFilter(field_name='last_contact_date', lookup_expr='lte')
    last_activity_after = django_filters.DateFilter(field_name='last_activity_date', lookup_expr='gte')
    last_activity_before = django_filters.DateFilter(field_name='last_activity_date', lookup_expr='lte')
    
    # Preference filters
    preferred_contact_method = django_filters.ChoiceFilter(choices=Client._meta.get_field('preferred_contact_method').choices)
    marketing_consent = django_filters.BooleanFilter()
    newsletter_subscription = django_filters.BooleanFilter()
    
    # Tag filters
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=ClientTag.objects.all(),
        field_name='tag_assignments__tag',
        to_field_name='id'
    )
    
    # Segment filters
    segments = django_filters.ModelMultipleChoiceFilter(
        queryset=ClientSegment.objects.all(),
        field_name='segment_assignments__segment',
        to_field_name='id'
    )
    
    # Interaction filters
    has_interactions = django_filters.BooleanFilter(method='filter_has_interactions')
    interaction_type = django_filters.ChoiceFilter(
        choices=ClientInteraction.INTERACTION_TYPES,
        field_name='interactions__interaction_type'
    )
    last_interaction_after = django_filters.DateFilter(
        field_name='interactions__created',
        lookup_expr='gte'
    )
    last_interaction_before = django_filters.DateFilter(
        field_name='interactions__created',
        lookup_expr='lte'
    )
    
    # Document filters
    has_documents = django_filters.BooleanFilter(method='filter_has_documents')
    document_type = django_filters.ChoiceFilter(
        choices=ClientDocument.DOCUMENT_TYPES,
        field_name='documents__document_type'
    )
    
    # Notes filters
    has_notes = django_filters.BooleanFilter(method='filter_has_notes')
    note_type = django_filters.ChoiceFilter(
        choices=ClientNote.NOTE_TYPES,
        field_name='notes__note_type'
    )
    
    def filter_has_interactions(self, queryset, name, value):
        if value:
            return queryset.filter(interactions__isnull=False).distinct()
        return queryset.filter(interactions__isnull=True)
    
    def filter_has_documents(self, queryset, name, value):
        if value:
            return queryset.filter(documents__isnull=False).distinct()
        return queryset.filter(documents__isnull=True)
    
    def filter_has_notes(self, queryset, name, value):
        if value:
            return queryset.filter(notes__isnull=False).distinct()
        return queryset.filter(notes__isnull=True)
    
    class Meta:
        model = Client
        fields = [
            'client_type', 'status', 'priority', 'email', 'phone', 'city', 'state',
            'country', 'postal_code', 'industry', 'company_size', 'source',
            'assigned_to', 'created_by', 'preferred_contact_method',
            'marketing_consent', 'newsletter_subscription'
        ]


class IndividualClientFilter(django_filters.FilterSet):
    """Filter for IndividualClient model."""
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    gender = django_filters.ChoiceFilter(choices=IndividualClient._meta.get_field('gender').choices)
    job_title = django_filters.CharFilter(lookup_expr='icontains')
    department = django_filters.CharFilter(lookup_expr='icontains')
    company = django_filters.CharFilter(lookup_expr='icontains')
    nationality = django_filters.CharFilter(lookup_expr='icontains')
    language_preference = django_filters.CharFilter(lookup_expr='icontains')
    timezone = django_filters.CharFilter(lookup_expr='icontains')
    
    # Date filters
    date_of_birth_after = django_filters.DateFilter(field_name='date_of_birth', lookup_expr='gte')
    date_of_birth_before = django_filters.DateFilter(field_name='date_of_birth', lookup_expr='lte')
    
    class Meta:
        model = IndividualClient
        fields = [
            'first_name', 'last_name', 'gender', 'job_title', 'department',
            'company', 'nationality', 'language_preference', 'timezone'
        ]


class CorporateClientFilter(django_filters.FilterSet):
    """Filter for CorporateClient model."""
    company_name = django_filters.CharFilter(lookup_expr='icontains')
    legal_name = django_filters.CharFilter(lookup_expr='icontains')
    registration_number = django_filters.CharFilter(lookup_expr='icontains')
    tax_registration_number = django_filters.CharFilter(lookup_expr='icontains')
    business_type = django_filters.ChoiceFilter(choices=CorporateClient._meta.get_field('business_type').choices)
    parent_company = django_filters.CharFilter(lookup_expr='icontains')
    
    # Financial filters
    annual_revenue_min = django_filters.NumberFilter(field_name='annual_revenue', lookup_expr='gte')
    annual_revenue_max = django_filters.NumberFilter(field_name='annual_revenue', lookup_expr='lte')
    
    # Date filters
    founded_year_min = django_filters.NumberFilter(field_name='founded_year', lookup_expr='gte')
    founded_year_max = django_filters.NumberFilter(field_name='founded_year', lookup_expr='lte')
    
    # Personnel filters
    ceo_name = django_filters.CharFilter(lookup_expr='icontains')
    cfo_name = django_filters.CharFilter(lookup_expr='icontains')
    cto_name = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = CorporateClient
        fields = [
            'company_name', 'legal_name', 'registration_number', 'tax_registration_number',
            'business_type', 'parent_company', 'ceo_name', 'cfo_name', 'cto_name'
        ]


class ClientContactFilter(django_filters.FilterSet):
    """Filter for ClientContact model."""
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    phone = django_filters.CharFilter(lookup_expr='icontains')
    mobile = django_filters.CharFilter(lookup_expr='icontains')
    job_title = django_filters.CharFilter(lookup_expr='icontains')
    department = django_filters.CharFilter(lookup_expr='icontains')
    preferred_contact_method = django_filters.ChoiceFilter(choices=ClientContact._meta.get_field('preferred_contact_method').choices)
    
    # Boolean filters
    is_primary = django_filters.BooleanFilter()
    is_decision_maker = django_filters.BooleanFilter()
    
    # Client filter
    client = django_filters.ModelChoiceFilter(queryset=Client.objects.all())
    
    class Meta:
        model = ClientContact
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'mobile', 'job_title',
            'department', 'is_primary', 'is_decision_maker', 'preferred_contact_method'
        ]


class ClientNoteFilter(django_filters.FilterSet):
    """Filter for ClientNote model."""
    note_type = django_filters.ChoiceFilter(choices=ClientNote.NOTE_TYPES)
    title = django_filters.CharFilter(lookup_expr='icontains')
    content = django_filters.CharFilter(lookup_expr='icontains')
    is_private = django_filters.BooleanFilter()
    
    # User filters
    related_user = django_filters.ModelChoiceFilter(queryset=ClientNote._meta.get_field('related_user').related_model.objects.all())
    
    # Date filters
    related_date_after = django_filters.DateTimeFilter(field_name='related_date', lookup_expr='gte')
    related_date_before = django_filters.DateTimeFilter(field_name='related_date', lookup_expr='lte')
    created_after = django_filters.DateTimeFilter(field_name='created', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created', lookup_expr='lte')
    
    # Client filter
    client = django_filters.ModelChoiceFilter(queryset=Client.objects.all())
    
    class Meta:
        model = ClientNote
        fields = ['note_type', 'title', 'is_private', 'related_user']


class ClientDocumentFilter(django_filters.FilterSet):
    """Filter for ClientDocument model."""
    document_type = django_filters.ChoiceFilter(choices=ClientDocument.DOCUMENT_TYPES)
    title = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    is_public = django_filters.BooleanFilter()
    
    # User filters
    uploaded_by = django_filters.ModelChoiceFilter(queryset=ClientDocument._meta.get_field('uploaded_by').related_model.objects.all())
    
    # Date filters
    expiry_date_after = django_filters.DateFilter(field_name='expiry_date', lookup_expr='gte')
    expiry_date_before = django_filters.DateFilter(field_name='expiry_date', lookup_expr='lte')
    created_after = django_filters.DateTimeFilter(field_name='created', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created', lookup_expr='lte')
    
    # File size filters
    file_size_min = django_filters.NumberFilter(field_name='file_size', lookup_expr='gte')
    file_size_max = django_filters.NumberFilter(field_name='file_size', lookup_expr='lte')
    
    # Client filter
    client = django_filters.ModelChoiceFilter(queryset=Client.objects.all())
    
    class Meta:
        model = ClientDocument
        fields = ['document_type', 'title', 'is_public', 'uploaded_by']


class ClientInteractionFilter(django_filters.FilterSet):
    """Filter for ClientInteraction model."""
    interaction_type = django_filters.ChoiceFilter(choices=ClientInteraction.INTERACTION_TYPES)
    subject = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    outcome = django_filters.CharFilter(lookup_expr='icontains')
    requires_follow_up = django_filters.BooleanFilter()
    
    # User filters
    initiated_by = django_filters.ModelChoiceFilter(queryset=ClientInteraction._meta.get_field('initiated_by').related_model.objects.all())
    
    # Duration filters
    duration_minutes_min = django_filters.NumberFilter(field_name='duration_minutes', lookup_expr='gte')
    duration_minutes_max = django_filters.NumberFilter(field_name='duration_minutes', lookup_expr='lte')
    
    # Date filters
    created_after = django_filters.DateTimeFilter(field_name='created', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created', lookup_expr='lte')
    follow_up_date_after = django_filters.DateTimeFilter(field_name='follow_up_date', lookup_expr='gte')
    follow_up_date_before = django_filters.DateTimeFilter(field_name='follow_up_date', lookup_expr='lte')
    
    # Client filter
    client = django_filters.ModelChoiceFilter(queryset=Client.objects.all())
    
    class Meta:
        model = ClientInteraction
        fields = [
            'interaction_type', 'subject', 'requires_follow_up', 'initiated_by'
        ]


class ClientTagFilter(django_filters.FilterSet):
    """Filter for ClientTag model."""
    name = django_filters.CharFilter(lookup_expr='icontains')
    color = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = ClientTag
        fields = ['name', 'color']


class ClientSegmentFilter(django_filters.FilterSet):
    """Filter for ClientSegment model."""
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    
    class Meta:
        model = ClientSegment
        fields = ['name', 'is_active']


# Advanced filters for analytics and reporting
class ClientAnalyticsFilter(django_filters.FilterSet):
    """Advanced filter for client analytics."""
    date_range = django_filters.ChoiceFilter(
        choices=[
            ('today', 'Today'),
            ('yesterday', 'Yesterday'),
            ('this_week', 'This Week'),
            ('last_week', 'Last Week'),
            ('this_month', 'This Month'),
            ('last_month', 'Last Month'),
            ('this_quarter', 'This Quarter'),
            ('last_quarter', 'Last Quarter'),
            ('this_year', 'This Year'),
            ('last_year', 'Last Year'),
            ('custom', 'Custom Range'),
        ],
        method='filter_date_range'
    )
    
    start_date = django_filters.DateFilter(field_name='created', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='created', lookup_expr='lte')
    
    def filter_date_range(self, queryset, name, value):
        today = timezone.now().date()
        
        if value == 'today':
            return queryset.filter(created__date=today)
        elif value == 'yesterday':
            yesterday = today - timedelta(days=1)
            return queryset.filter(created__date=yesterday)
        elif value == 'this_week':
            start_of_week = today - timedelta(days=today.weekday())
            return queryset.filter(created__date__gte=start_of_week)
        elif value == 'last_week':
            start_of_last_week = today - timedelta(days=today.weekday() + 7)
            end_of_last_week = start_of_last_week + timedelta(days=6)
            return queryset.filter(created__date__gte=start_of_last_week, created__date__lte=end_of_last_week)
        elif value == 'this_month':
            start_of_month = today.replace(day=1)
            return queryset.filter(created__date__gte=start_of_month)
        elif value == 'last_month':
            if today.month == 1:
                start_of_last_month = today.replace(year=today.year - 1, month=12, day=1)
            else:
                start_of_last_month = today.replace(month=today.month - 1, day=1)
            end_of_last_month = today.replace(day=1) - timedelta(days=1)
            return queryset.filter(created__date__gte=start_of_last_month, created__date__lte=end_of_last_month)
        elif value == 'this_quarter':
            quarter = (today.month - 1) // 3 + 1
            start_of_quarter = today.replace(month=(quarter - 1) * 3 + 1, day=1)
            return queryset.filter(created__date__gte=start_of_quarter)
        elif value == 'last_quarter':
            quarter = (today.month - 1) // 3 + 1
            if quarter == 1:
                start_of_last_quarter = today.replace(year=today.year - 1, month=10, day=1)
            else:
                start_of_last_quarter = today.replace(month=(quarter - 2) * 3 + 1, day=1)
            end_of_last_quarter = today.replace(month=(quarter - 1) * 3 + 1, day=1) - timedelta(days=1)
            return queryset.filter(created__date__gte=start_of_last_quarter, created__date__lte=end_of_last_quarter)
        elif value == 'this_year':
            start_of_year = today.replace(month=1, day=1)
            return queryset.filter(created__date__gte=start_of_year)
        elif value == 'last_year':
            start_of_last_year = today.replace(year=today.year - 1, month=1, day=1)
            end_of_last_year = today.replace(year=today.year - 1, month=12, day=31)
            return queryset.filter(created__date__gte=start_of_last_year, created__date__lte=end_of_last_year)
        
        return queryset
    
    class Meta:
        model = Client
        fields = ['date_range', 'start_date', 'end_date']


class ClientInteractionAnalyticsFilter(django_filters.FilterSet):
    """Advanced filter for client interaction analytics."""
    date_range = django_filters.ChoiceFilter(
        choices=[
            ('today', 'Today'),
            ('yesterday', 'Yesterday'),
            ('this_week', 'This Week'),
            ('last_week', 'Last Week'),
            ('this_month', 'This Month'),
            ('last_month', 'Last Month'),
            ('this_quarter', 'This Quarter'),
            ('last_quarter', 'Last Quarter'),
            ('this_year', 'This Year'),
            ('last_year', 'Last Year'),
            ('custom', 'Custom Range'),
        ],
        method='filter_date_range'
    )
    
    start_date = django_filters.DateTimeFilter(field_name='created', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='created', lookup_expr='lte')
    
    def filter_date_range(self, queryset, name, value):
        today = timezone.now().date()
        
        if value == 'today':
            return queryset.filter(created__date=today)
        elif value == 'yesterday':
            yesterday = today - timedelta(days=1)
            return queryset.filter(created__date=yesterday)
        elif value == 'this_week':
            start_of_week = today - timedelta(days=today.weekday())
            return queryset.filter(created__date__gte=start_of_week)
        elif value == 'last_week':
            start_of_last_week = today - timedelta(days=today.weekday() + 7)
            end_of_last_week = start_of_last_week + timedelta(days=6)
            return queryset.filter(created__date__gte=start_of_last_week, created__date__lte=end_of_last_week)
        elif value == 'this_month':
            start_of_month = today.replace(day=1)
            return queryset.filter(created__date__gte=start_of_month)
        elif value == 'last_month':
            if today.month == 1:
                start_of_last_month = today.replace(year=today.year - 1, month=12, day=1)
            else:
                start_of_last_month = today.replace(month=today.month - 1, day=1)
            end_of_last_month = today.replace(day=1) - timedelta(days=1)
            return queryset.filter(created__date__gte=start_of_last_month, created__date__lte=end_of_last_month)
        elif value == 'this_quarter':
            quarter = (today.month - 1) // 3 + 1
            start_of_quarter = today.replace(month=(quarter - 1) * 3 + 1, day=1)
            return queryset.filter(created__date__gte=start_of_quarter)
        elif value == 'last_quarter':
            quarter = (today.month - 1) // 3 + 1
            if quarter == 1:
                start_of_last_quarter = today.replace(year=today.year - 1, month=10, day=1)
            else:
                start_of_last_quarter = today.replace(month=(quarter - 2) * 3 + 1, day=1)
            end_of_last_quarter = today.replace(month=(quarter - 1) * 3 + 1, day=1) - timedelta(days=1)
            return queryset.filter(created__date__gte=start_of_last_quarter, created__date__lte=end_of_last_quarter)
        elif value == 'this_year':
            start_of_year = today.replace(month=1, day=1)
            return queryset.filter(created__date__gte=start_of_year)
        elif value == 'last_year':
            start_of_last_year = today.replace(year=today.year - 1, month=1, day=1)
            end_of_last_year = today.replace(year=today.year - 1, month=12, day=31)
            return queryset.filter(created__date__gte=start_of_last_year, created__date__lte=end_of_last_year)
        
        return queryset
    
    class Meta:
        model = ClientInteraction
        fields = ['date_range', 'start_date', 'end_date']
