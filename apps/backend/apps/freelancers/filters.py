"""
Filters for freelancers app.
"""
import django_filters
from django.db.models import Q
from .models import Freelancer, FreelancerSkill


class FreelancerFilter(django_filters.FilterSet):
    """
    Filter set for freelancer list view.
    """
    search = django_filters.CharFilter(method='filter_search')
    city = django_filters.CharFilter(field_name='city', lookup_expr='icontains')
    state = django_filters.CharFilter(field_name='state', lookup_expr='icontains')
    cleaning_types = django_filters.CharFilter(method='filter_cleaning_types')
    skills = django_filters.CharFilter(method='filter_skills')
    min_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    max_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='lte')
    min_rate = django_filters.NumberFilter(field_name='hourly_rate', lookup_expr='gte')
    max_rate = django_filters.NumberFilter(field_name='hourly_rate', lookup_expr='lte')
    is_available = django_filters.BooleanFilter(field_name='is_available')
    status = django_filters.ChoiceFilter(choices=Freelancer.STATUS_CHOICES)
    verification_status = django_filters.ChoiceFilter(choices=Freelancer.VERIFICATION_STATUS_CHOICES)
    background_check = django_filters.BooleanFilter(field_name='background_check_completed')
    blockchain_verified = django_filters.BooleanFilter(field_name='blockchain_verified')
    
    class Meta:
        model = Freelancer
        fields = [
            'search', 'city', 'state', 'cleaning_types', 'skills',
            'min_rating', 'max_rating', 'min_rate', 'max_rate',
            'is_available', 'status', 'verification_status',
            'background_check', 'blockchain_verified'
        ]
    
    def filter_search(self, queryset, name, value):
        """
        Search across multiple fields.
        """
        if not value:
            return queryset
            
        return queryset.filter(
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(freelancer_id__icontains=value) |
            Q(special_skills__icontains=value) |
            Q(city__icontains=value) |
            Q(state__icontains=value) |
            Q(bio__icontains=value)
        )
    
    def filter_cleaning_types(self, queryset, name, value):
        """
        Filter by cleaning types (supports multiple comma-separated values).
        """
        if not value:
            return queryset
            
        types = [t.strip() for t in value.split(',')]
        q_objects = Q()
        for cleaning_type in types:
            q_objects |= Q(cleaning_types__contains=[cleaning_type])
        
        return queryset.filter(q_objects)
    
    def filter_skills(self, queryset, name, value):
        """
        Filter by skills (supports multiple comma-separated skill IDs).
        """
        if not value:
            return queryset
            
        skill_ids = [s.strip() for s in value.split(',')]
        try:
            skill_ids = [int(s) for s in skill_ids]
        except ValueError:
            return queryset
            
        return queryset.filter(skill_assignments__skill_id__in=skill_ids).distinct()
