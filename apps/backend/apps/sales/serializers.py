"""
Sales and client management serializers for iNEAT ERP platform.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.sales.models import (
    Client, IndividualClient, CorporateClient, ClientContact, ClientNote,
    ClientDocument, ClientTag, ClientTagAssignment, ClientInteraction,
    ClientSegment, ClientSegmentAssignment
)

User = get_user_model()


class ClientTagSerializer(serializers.ModelSerializer):
    """Serializer for ClientTag model."""
    
    class Meta:
        model = ClientTag
        fields = [
            'id', 'name', 'color', 'description', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class ClientTagAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for ClientTagAssignment model."""
    tag_name = serializers.CharField(source='tag.name', read_only=True)
    tag_color = serializers.CharField(source='tag.color', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    
    class Meta:
        model = ClientTagAssignment
        fields = [
            'id', 'tag', 'tag_name', 'tag_color', 'assigned_by', 'assigned_by_name',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class ClientContactSerializer(serializers.ModelSerializer):
    """Serializer for ClientContact model."""
    full_name = serializers.SerializerMethodField()
    preferred_contact_method_display = serializers.CharField(
        source='get_preferred_contact_method_display', read_only=True
    )
    
    class Meta:
        model = ClientContact
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone', 'mobile',
            'job_title', 'department', 'is_primary', 'is_decision_maker',
            'preferred_contact_method', 'preferred_contact_method_display', 'notes',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class IndividualClientSerializer(serializers.ModelSerializer):
    """Serializer for IndividualClient model."""
    full_name = serializers.ReadOnlyField()
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    
    class Meta:
        model = IndividualClient
        fields = [
            'id', 'first_name', 'last_name', 'middle_name', 'full_name',
            'date_of_birth', 'gender', 'gender_display', 'job_title', 'department',
            'company', 'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship', 'nationality', 'language_preference',
            'timezone', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class CorporateClientSerializer(serializers.ModelSerializer):
    """Serializer for CorporateClient model."""
    business_type_display = serializers.CharField(source='get_business_type_display', read_only=True)
    
    class Meta:
        model = CorporateClient
        fields = [
            'id', 'company_name', 'legal_name', 'registration_number',
            'tax_registration_number', 'business_type', 'business_type_display',
            'founded_year', 'annual_revenue', 'ceo_name', 'cfo_name', 'cto_name',
            'parent_company', 'subsidiaries', 'business_description',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class ClientNoteSerializer(serializers.ModelSerializer):
    """Serializer for ClientNote model."""
    note_type_display = serializers.CharField(source='get_note_type_display', read_only=True)
    related_user_name = serializers.CharField(source='related_user.get_full_name', read_only=True)
    
    class Meta:
        model = ClientNote
        fields = [
            'id', 'note_type', 'note_type_display', 'title', 'content',
            'related_user', 'related_user_name', 'related_date', 'is_private',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class ClientDocumentSerializer(serializers.ModelSerializer):
    """Serializer for ClientDocument model."""
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_url = serializers.SerializerMethodField()
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = ClientDocument
        fields = [
            'id', 'document_type', 'document_type_display', 'title', 'description',
            'file', 'file_url', 'file_size', 'file_size_mb', 'uploaded_by',
            'uploaded_by_name', 'is_public', 'expiry_date', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified', 'file_size']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None
    
    def get_file_size_mb(self, obj):
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return None


class ClientInteractionSerializer(serializers.ModelSerializer):
    """Serializer for ClientInteraction model."""
    interaction_type_display = serializers.CharField(source='get_interaction_type_display', read_only=True)
    initiated_by_name = serializers.CharField(source='initiated_by.get_full_name', read_only=True)
    
    class Meta:
        model = ClientInteraction
        fields = [
            'id', 'interaction_type', 'interaction_type_display', 'subject', 'description',
            'initiated_by', 'initiated_by_name', 'duration_minutes', 'outcome',
            'requires_follow_up', 'follow_up_date', 'follow_up_notes',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class ClientSegmentSerializer(serializers.ModelSerializer):
    """Serializer for ClientSegment model."""
    client_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ClientSegment
        fields = [
            'id', 'name', 'description', 'criteria', 'color', 'is_active',
            'client_count', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']
    
    def get_client_count(self, obj):
        return obj.client_assignments.count()


class ClientSegmentAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for ClientSegmentAssignment model."""
    segment_name = serializers.CharField(source='segment.name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    
    class Meta:
        model = ClientSegmentAssignment
        fields = [
            'id', 'segment', 'segment_name', 'assigned_date', 'assigned_by',
            'assigned_by_name', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified', 'assigned_date']


class ClientSerializer(serializers.ModelSerializer):
    """Main serializer for Client model."""
    client_type_display = serializers.CharField(source='get_client_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    preferred_contact_method_display = serializers.CharField(
        source='get_preferred_contact_method_display', read_only=True
    )
    
    # Related fields
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    # Type-specific data
    individual_client = IndividualClientSerializer(read_only=True)
    corporate_client = CorporateClientSerializer(read_only=True)
    
    # Related data
    contacts = ClientContactSerializer(many=True, read_only=True)
    notes = ClientNoteSerializer(many=True, read_only=True)
    documents = ClientDocumentSerializer(many=True, read_only=True)
    interactions = ClientInteractionSerializer(many=True, read_only=True)
    tag_assignments = ClientTagAssignmentSerializer(many=True, read_only=True)
    segment_assignments = ClientSegmentAssignmentSerializer(many=True, read_only=True)
    
    # Computed fields
    display_name = serializers.ReadOnlyField()
    full_address = serializers.ReadOnlyField()
    total_interactions = serializers.SerializerMethodField()
    last_interaction_date = serializers.SerializerMethodField()
    total_documents = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    segments = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = [
            'id', 'client_type', 'client_type_display', 'status', 'status_display',
            'priority', 'priority_display', 'email', 'phone', 'website',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
            'credit_limit', 'payment_terms', 'tax_id', 'currency', 'industry',
            'company_size', 'assigned_to', 'assigned_to_name', 'source', 'notes',
            'preferred_contact_method', 'preferred_contact_method_display',
            'marketing_consent', 'newsletter_subscription', 'last_contact_date',
            'last_activity_date', 'created_by', 'created_by_name',
            'individual_client', 'corporate_client', 'contacts', 'notes', 'documents',
            'interactions', 'tag_assignments', 'segment_assignments',
            'display_name', 'full_address', 'total_interactions', 'last_interaction_date',
            'total_documents', 'tags', 'segments', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified', 'last_contact_date', 'last_activity_date']
    
    def get_total_interactions(self, obj):
        return obj.interactions.count()
    
    def get_last_interaction_date(self, obj):
        last_interaction = obj.interactions.order_by('-created').first()
        return last_interaction.created if last_interaction else None
    
    def get_total_documents(self, obj):
        return obj.documents.count()
    
    def get_tags(self, obj):
        return [assignment.tag.name for assignment in obj.tag_assignments.all()]
    
    def get_segments(self, obj):
        return [assignment.segment.name for assignment in obj.segment_assignments.all()]
    
    def create(self, validated_data):
        """Create client with type-specific data."""
        client_type = validated_data.get('client_type')
        client = Client.objects.create(**validated_data)
        
        # Create type-specific client data if provided
        if client_type == 'individual':
            individual_data = self.initial_data.get('individual_client', {})
            if individual_data:
                IndividualClient.objects.create(client=client, **individual_data)
        elif client_type == 'corporate':
            corporate_data = self.initial_data.get('corporate_client', {})
            if corporate_data:
                CorporateClient.objects.create(client=client, **corporate_data)
        
        return client
    
    def update(self, instance, validated_data):
        """Update client with type-specific data."""
        client_type = validated_data.get('client_type', instance.client_type)
        
        # Update basic client fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update type-specific data
        if client_type == 'individual':
            individual_data = self.initial_data.get('individual_client', {})
            if individual_data:
                individual_client, created = IndividualClient.objects.get_or_create(
                    client=instance,
                    defaults=individual_data
                )
                if not created:
                    for attr, value in individual_data.items():
                        setattr(individual_client, attr, value)
                    individual_client.save()
        elif client_type == 'corporate':
            corporate_data = self.initial_data.get('corporate_client', {})
            if corporate_data:
                corporate_client, created = CorporateClient.objects.get_or_create(
                    client=instance,
                    defaults=corporate_data
                )
                if not created:
                    for attr, value in corporate_data.items():
                        setattr(corporate_client, attr, value)
                    corporate_client.save()
        
        return instance


class ClientCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating clients with type-specific data."""
    individual_client = IndividualClientSerializer(required=False)
    corporate_client = CorporateClientSerializer(required=False)
    
    class Meta:
        model = Client
        fields = [
            'client_type', 'status', 'priority', 'email', 'phone', 'website',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
            'credit_limit', 'payment_terms', 'tax_id', 'currency', 'industry',
            'company_size', 'assigned_to', 'source', 'notes',
            'preferred_contact_method', 'marketing_consent', 'newsletter_subscription',
            'individual_client', 'corporate_client'
        ]
    
    def validate(self, data):
        """Validate that type-specific data is provided."""
        client_type = data.get('client_type')
        
        if client_type == 'individual':
            if not self.initial_data.get('individual_client'):
                raise serializers.ValidationError(
                    "Individual client data is required for individual clients."
                )
        elif client_type == 'corporate':
            if not self.initial_data.get('corporate_client'):
                raise serializers.ValidationError(
                    "Corporate client data is required for corporate clients."
                )
        
        return data
    
    def create(self, validated_data):
        """Create client with type-specific data."""
        client_type = validated_data.pop('client_type')
        individual_data = validated_data.pop('individual_client', None)
        corporate_data = validated_data.pop('corporate_client', None)
        
        # Create the base client
        client = Client.objects.create(
            client_type=client_type,
            **validated_data
        )
        
        # Create type-specific client
        if client_type == 'individual' and individual_data:
            IndividualClient.objects.create(client=client, **individual_data)
        elif client_type == 'corporate' and corporate_data:
            CorporateClient.objects.create(client=client, **corporate_data)
        
        return client


class ClientListSerializer(serializers.ModelSerializer):
    """Simplified serializer for client lists."""
    client_type_display = serializers.CharField(source='get_client_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    display_name = serializers.ReadOnlyField()
    total_interactions = serializers.SerializerMethodField()
    last_interaction_date = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = [
            'id', 'client_type', 'client_type_display', 'status', 'status_display',
            'priority', 'priority_display', 'email', 'phone', 'city', 'state',
            'country', 'assigned_to', 'assigned_to_name', 'display_name',
            'total_interactions', 'last_interaction_date', 'tags',
            'last_contact_date', 'created', 'modified'
        ]
    
    def get_total_interactions(self, obj):
        return obj.interactions.count()
    
    def get_last_interaction_date(self, obj):
        last_interaction = obj.interactions.order_by('-created').first()
        return last_interaction.created if last_interaction else None
    
    def get_tags(self, obj):
        return [assignment.tag.name for assignment in obj.tag_assignments.all()]


# Dashboard and Analytics Serializers
class ClientDashboardSerializer(serializers.Serializer):
    """Serializer for client dashboard data."""
    total_clients = serializers.IntegerField()
    active_clients = serializers.IntegerField()
    prospect_clients = serializers.IntegerField()
    individual_clients = serializers.IntegerField()
    corporate_clients = serializers.IntegerField()
    clients_by_status = serializers.ListField(child=serializers.DictField())
    clients_by_type = serializers.ListField(child=serializers.DictField())
    clients_by_priority = serializers.ListField(child=serializers.DictField())
    recent_clients = serializers.ListField(child=serializers.DictField())
    top_clients_by_interactions = serializers.ListField(child=serializers.DictField())
    clients_by_source = serializers.ListField(child=serializers.DictField())
    monthly_client_growth = serializers.ListField(child=serializers.DictField())


class ClientAnalyticsSerializer(serializers.Serializer):
    """Serializer for client analytics."""
    total_clients = serializers.IntegerField()
    new_clients_this_month = serializers.IntegerField()
    active_clients = serializers.IntegerField()
    conversion_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    average_client_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    client_retention_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    top_sources = serializers.ListField(child=serializers.DictField())
    client_distribution = serializers.ListField(child=serializers.DictField())
    interaction_trends = serializers.ListField(child=serializers.DictField())
    geographic_distribution = serializers.ListField(child=serializers.DictField())


class ClientInteractionAnalyticsSerializer(serializers.Serializer):
    """Serializer for client interaction analytics."""
    total_interactions = serializers.IntegerField()
    interactions_by_type = serializers.ListField(child=serializers.DictField())
    interactions_by_user = serializers.ListField(child=serializers.DictField())
    average_interactions_per_client = serializers.DecimalField(max_digits=5, decimal_places=2)
    interaction_trends = serializers.ListField(child=serializers.DictField())
    follow_up_required = serializers.IntegerField()
    overdue_follow_ups = serializers.IntegerField()
