# Sales & Client Management Module

A comprehensive client management system for the TidyGen ERP platform that supports both individual and corporate clients with advanced relationship management, interaction tracking, and analytics.

## Features

### 👥 **Dual Client Types**
- **Individual Clients**: Personal clients with detailed personal information
- **Corporate Clients**: Business clients with company-specific data
- **Unified Management**: Single interface for both client types
- **Type-Specific Fields**: Tailored data collection for each client type

### 📊 **Client Relationship Management**
- **Contact Management**: Multiple contacts per client with role-based information
- **Interaction Tracking**: Complete history of all client interactions
- **Note Management**: Organized notes with categorization and privacy controls
- **Document Management**: File attachments with expiry tracking
- **Tag System**: Flexible tagging for client categorization
- **Segmentation**: Advanced client segmentation for marketing and sales

### 🔄 **Automated Operations**
- **Activity Tracking**: Automatic last contact and activity date updates
- **Primary Contact Management**: Ensures only one primary contact per client
- **Default Tag Assignment**: Automatic tagging based on client type and status
- **Welcome Interactions**: Automatic welcome interaction for new clients
- **Follow-up Management**: Automated follow-up note creation
- **Document Expiry Alerts**: Automatic notifications for expiring documents

### 📈 **Analytics & Reporting**
- **Client Dashboard**: Real-time overview of client metrics
- **Client Analytics**: Comprehensive client performance analytics
- **Interaction Analytics**: Detailed interaction tracking and trends
- **Geographic Distribution**: Client location analysis
- **Source Tracking**: Lead source performance analysis
- **Growth Metrics**: Client acquisition and retention tracking

## Models

### Core Models

#### Client
- Base client model supporting both individual and corporate types
- Contact information, address, and business details
- Financial information (credit limits, payment terms)
- Status and priority management
- Assignment and tracking fields

#### IndividualClient
- Personal information (name, date of birth, gender)
- Professional details (job title, company, department)
- Emergency contact information
- Personal preferences (language, timezone)

#### CorporateClient
- Company information (name, legal name, registration numbers)
- Business details (type, founded year, annual revenue)
- Key personnel (CEO, CFO, CTO)
- Corporate structure (parent company, subsidiaries)

#### ClientContact
- Additional contacts for corporate clients
- Contact preferences and role information
- Primary contact management
- Decision maker identification

#### ClientNote
- Organized notes with categorization
- Privacy controls and user tracking
- Related date and user information
- Note type classification

#### ClientDocument
- File attachments with metadata
- Document type classification
- Expiry date tracking
- Public/private access controls

#### ClientTag
- Flexible tagging system
- Color-coded tags
- Organization-specific tags
- Description and categorization

#### ClientInteraction
- Complete interaction history
- Interaction type classification
- Duration and outcome tracking
- Follow-up management

#### ClientSegment
- Advanced client segmentation
- JSON-based criteria storage
- Marketing and sales targeting
- Performance tracking

## API Endpoints

### Clients
- `GET /api/v1/sales/clients/` - List clients
- `POST /api/v1/sales/clients/` - Create client
- `GET /api/v1/sales/clients/{id}/` - Get client details
- `PUT /api/v1/sales/clients/{id}/` - Update client
- `DELETE /api/v1/sales/clients/{id}/` - Delete client
- `POST /api/v1/sales/clients/{id}/add_contact/` - Add contact
- `POST /api/v1/sales/clients/{id}/add_note/` - Add note
- `POST /api/v1/sales/clients/{id}/add_interaction/` - Add interaction
- `POST /api/v1/sales/clients/{id}/assign_tag/` - Assign tag
- `DELETE /api/v1/sales/clients/{id}/remove_tag/` - Remove tag
- `POST /api/v1/sales/clients/{id}/assign_segment/` - Assign segment
- `DELETE /api/v1/sales/clients/{id}/remove_segment/` - Remove segment
- `POST /api/v1/sales/clients/{id}/change_status/` - Change status
- `POST /api/v1/sales/clients/{id}/change_priority/` - Change priority
- `GET /api/v1/sales/clients/analytics/` - Get client analytics

### Individual Clients
- `GET /api/v1/sales/individual-clients/` - List individual clients
- `POST /api/v1/sales/individual-clients/` - Create individual client
- `GET /api/v1/sales/individual-clients/{id}/` - Get individual client details
- `PUT /api/v1/sales/individual-clients/{id}/` - Update individual client
- `DELETE /api/v1/sales/individual-clients/{id}/` - Delete individual client

### Corporate Clients
- `GET /api/v1/sales/corporate-clients/` - List corporate clients
- `POST /api/v1/sales/corporate-clients/` - Create corporate client
- `GET /api/v1/sales/corporate-clients/{id}/` - Get corporate client details
- `PUT /api/v1/sales/corporate-clients/{id}/` - Update corporate client
- `DELETE /api/v1/sales/corporate-clients/{id}/` - Delete corporate client

### Client Contacts
- `GET /api/v1/sales/client-contacts/` - List client contacts
- `POST /api/v1/sales/client-contacts/` - Create client contact
- `GET /api/v1/sales/client-contacts/{id}/` - Get client contact details
- `PUT /api/v1/sales/client-contacts/{id}/` - Update client contact
- `DELETE /api/v1/sales/client-contacts/{id}/` - Delete client contact

### Client Notes
- `GET /api/v1/sales/client-notes/` - List client notes
- `POST /api/v1/sales/client-notes/` - Create client note
- `GET /api/v1/sales/client-notes/{id}/` - Get client note details
- `PUT /api/v1/sales/client-notes/{id}/` - Update client note
- `DELETE /api/v1/sales/client-notes/{id}/` - Delete client note

### Client Documents
- `GET /api/v1/sales/client-documents/` - List client documents
- `POST /api/v1/sales/client-documents/` - Create client document
- `GET /api/v1/sales/client-documents/{id}/` - Get client document details
- `PUT /api/v1/sales/client-documents/{id}/` - Update client document
- `DELETE /api/v1/sales/client-documents/{id}/` - Delete client document

### Client Tags
- `GET /api/v1/sales/client-tags/` - List client tags
- `POST /api/v1/sales/client-tags/` - Create client tag
- `GET /api/v1/sales/client-tags/{id}/` - Get client tag details
- `PUT /api/v1/sales/client-tags/{id}/` - Update client tag
- `DELETE /api/v1/sales/client-tags/{id}/` - Delete client tag

### Client Interactions
- `GET /api/v1/sales/client-interactions/` - List client interactions
- `POST /api/v1/sales/client-interactions/` - Create client interaction
- `GET /api/v1/sales/client-interactions/{id}/` - Get client interaction details
- `PUT /api/v1/sales/client-interactions/{id}/` - Update client interaction
- `DELETE /api/v1/sales/client-interactions/{id}/` - Delete client interaction
- `GET /api/v1/sales/client-interactions/analytics/` - Get interaction analytics

### Client Segments
- `GET /api/v1/sales/client-segments/` - List client segments
- `POST /api/v1/sales/client-segments/` - Create client segment
- `GET /api/v1/sales/client-segments/{id}/` - Get client segment details
- `PUT /api/v1/sales/client-segments/{id}/` - Update client segment
- `DELETE /api/v1/sales/client-segments/{id}/` - Delete client segment

### Dashboard
- `GET /api/v1/sales/dashboard/overview/` - Get client dashboard overview

## Filters

The sales module includes comprehensive filtering capabilities:

### Client Filters
- **Basic**: Client type, status, priority, email, phone
- **Address**: City, state, country, postal code
- **Business**: Industry, company size, source
- **Assignment**: Assigned to, created by
- **Financial**: Credit limit, payment terms ranges
- **Date Ranges**: Created, last contact, last activity
- **Preferences**: Contact method, marketing consent
- **Relations**: Tags, segments, interactions, documents, notes

### Individual Client Filters
- **Personal**: Name, gender, date of birth
- **Professional**: Job title, department, company
- **Location**: Nationality, language, timezone

### Corporate Client Filters
- **Company**: Name, legal name, registration numbers
- **Business**: Type, founded year, annual revenue
- **Personnel**: CEO, CFO, CTO names
- **Structure**: Parent company, subsidiaries

### Advanced Analytics Filters
- **Date Range Presets**: Today, this week, this month, etc.
- **Custom Date Ranges**: Flexible date filtering
- **Interaction Filters**: Type, user, duration, follow-up status
- **Document Filters**: Type, size, expiry, uploader

## Signals

The sales module includes automated signals for:

### Activity Tracking
- Automatic last contact date updates on interactions
- Last activity date updates on all client-related changes
- Activity tracking for notes, documents, contacts, tags, segments

### Contact Management
- Primary contact enforcement (only one primary per client)
- Contact preference management
- Decision maker identification

### Client Lifecycle
- Default tag assignment based on type and status
- Welcome interaction creation for new clients
- Status and priority change notifications

### Document Management
- Expiry date tracking and notifications
- File size calculation and storage
- Document type classification

### Follow-up Management
- Automatic follow-up note creation
- Follow-up date tracking
- Overdue follow-up identification

## Permissions

The sales module uses the following permission system:

- **IsAuthenticated**: User must be logged in
- **IsOrganizationMember**: User must be a member of the organization
- **Organization-specific data**: All data is filtered by organization

## Testing

Comprehensive test coverage includes:

- **Model Tests**: Test model creation, validation, and relationships
- **API Tests**: Test all CRUD operations and custom endpoints
- **Signal Tests**: Test automated calculations and updates
- **Filter Tests**: Test filtering functionality
- **Permission Tests**: Test access control

Run tests with:
```bash
python manage.py test apps.sales
```

## Usage Examples

### Creating an Individual Client
```python
# Create individual client
client_data = {
    'client_type': 'individual',
    'email': 'john@example.com',
    'phone': '+1234567890',
    'individual_client': {
        'first_name': 'John',
        'last_name': 'Doe',
        'date_of_birth': '1990-01-01',
        'gender': 'male',
        'job_title': 'Software Engineer'
    }
}

response = requests.post('/api/v1/sales/clients/', json=client_data)
```

### Creating a Corporate Client
```python
# Create corporate client
client_data = {
    'client_type': 'corporate',
    'email': 'info@acme.com',
    'phone': '+1234567890',
    'corporate_client': {
        'company_name': 'Acme Corporation',
        'legal_name': 'Acme Corp LLC',
        'business_type': 'corporation',
        'founded_year': 2020,
        'annual_revenue': '1000000.00'
    }
}

response = requests.post('/api/v1/sales/clients/', json=client_data)
```

### Adding a Contact
```python
# Add contact to client
contact_data = {
    'first_name': 'Jane',
    'last_name': 'Smith',
    'email': 'jane@acme.com',
    'phone': '+1234567891',
    'job_title': 'Manager',
    'is_primary': True
}

response = requests.post(f'/api/v1/sales/clients/{client_id}/add_contact/', json=contact_data)
```

### Recording an Interaction
```python
# Record client interaction
interaction_data = {
    'interaction_type': 'phone_call',
    'subject': 'Follow-up call',
    'description': 'Called to follow up on proposal',
    'duration_minutes': 30,
    'outcome': 'Client interested in proposal'
}

response = requests.post(f'/api/v1/sales/clients/{client_id}/add_interaction/', json=interaction_data)
```

### Assigning Tags
```python
# Assign tag to client
tag_data = {'tag_id': tag_id}
response = requests.post(f'/api/v1/sales/clients/{client_id}/assign_tag/', json=tag_data)
```

### Changing Client Status
```python
# Change client status
status_data = {'status': 'active'}
response = requests.post(f'/api/v1/sales/clients/{client_id}/change_status/', json=status_data)
```

## Integration

The sales module integrates with:

- **Organizations**: Self-hosted support
- **Users**: User authentication and permissions
- **Core**: Base models and permissions
- **Finance**: Client financial information and invoicing

## Future Enhancements

Planned features include:

- **Lead Management**: Lead scoring and conversion tracking
- **Sales Pipeline**: Opportunity and deal management
- **Email Integration**: Email tracking and synchronization
- **Calendar Integration**: Meeting scheduling and tracking
- **Communication Templates**: Pre-built communication templates
- **Client Portal**: Self-service client portal
- **Advanced Analytics**: Predictive analytics and insights
- **Mobile App**: Mobile client management
- **API Webhooks**: Real-time notifications
- **Import/Export**: Data migration tools
- **Custom Fields**: Configurable client fields
- **Workflow Automation**: Automated client workflows
