# Purchasing Management Module

## Overview

The Purchasing Management module provides comprehensive functionality for managing all aspects of procurement and vendor relationships in the TidyGen ERP system. This module handles vendor management, purchase requisitions, purchase orders, contract management, and vendor performance evaluation.

## Features

### Core Functionality
- **Vendor Management**: Complete vendor lifecycle management with contact information, performance metrics, and evaluation systems
- **Purchase Requisitions**: Internal request system for procurement needs with approval workflows
- **Purchase Orders**: Formal purchase order management with status tracking and item management
- **Contract Management**: Long-term contract management with renewal tracking and performance monitoring
- **Vendor Evaluation**: Comprehensive vendor performance assessment and rating system

### Advanced Features
- **Automated Workflows**: Status transitions, approval processes, and automatic calculations
- **Performance Analytics**: Vendor performance metrics, spending analysis, and delivery tracking
- **Multi-currency Support**: Support for different currencies in international procurement
- **Document Management**: Purchase order and contract document generation and tracking
- **Integration**: Seamless integration with Inventory, Finance, and HR modules

## Models

### Vendor Management
- **Vendor**: Core vendor information, performance metrics, and business details
- **VendorContact**: Multiple contact persons per vendor with primary contact designation

### Purchase Process
- **PurchaseRequisition**: Internal procurement requests with approval workflow
- **PurchaseRequisitionItem**: Individual items within requisitions
- **PurchaseOrder**: Formal purchase orders sent to vendors
- **PurchaseOrderItem**: Individual items within purchase orders

### Contract Management
- **PurchaseContract**: Long-term supply agreements and service contracts
- **PurchaseContractItem**: Contract terms and pricing for specific items

### Performance Management
- **VendorEvaluation**: Comprehensive vendor performance assessments

## API Endpoints

### Vendor Management
- `GET/POST /api/purchasing/vendors/` - List and create vendors
- `GET/PUT/PATCH/DELETE /api/purchasing/vendors/{id}/` - Manage individual vendors
- `GET /api/purchasing/vendors/{id}/purchase-orders/` - Get vendor's purchase orders
- `GET /api/purchasing/vendors/{id}/contracts/` - Get vendor's contracts
- `GET /api/purchasing/vendors/{id}/evaluations/` - Get vendor's evaluations
- `GET /api/purchasing/vendors/active-vendors/` - Get active vendors
- `GET /api/purchasing/vendors/top-vendors/` - Get top performing vendors
- `GET /api/purchasing/vendors/vendor-performance/` - Get vendor performance metrics

### Vendor Contacts
- `GET/POST /api/purchasing/vendor-contacts/` - List and create vendor contacts
- `GET/PUT/PATCH/DELETE /api/purchasing/vendor-contacts/{id}/` - Manage individual contacts

### Purchase Orders
- `GET/POST /api/purchasing/purchase-orders/` - List and create purchase orders
- `GET/PUT/PATCH/DELETE /api/purchasing/purchase-orders/{id}/` - Manage individual orders
- `POST /api/purchasing/purchase-orders/{id}/approve/` - Approve purchase order
- `POST /api/purchasing/purchase-orders/{id}/place-order/` - Place order with vendor
- `POST /api/purchasing/purchase-orders/{id}/receive-order/` - Receive complete order
- `GET /api/purchasing/purchase-orders/{id}/items/` - Get order items
- `GET /api/purchasing/purchase-orders/pending-approval/` - Get pending approvals
- `GET /api/purchasing/purchase-orders/approved-orders/` - Get approved orders
- `GET /api/purchasing/purchase-orders/overdue-orders/` - Get overdue orders

### Purchase Order Items
- `GET/POST /api/purchasing/purchase-order-items/` - List and create order items
- `GET/PUT/PATCH/DELETE /api/purchasing/purchase-order-items/{id}/` - Manage individual items
- `POST /api/purchasing/purchase-order-items/{id}/receive-item/` - Receive items

### Purchase Requisitions
- `GET/POST /api/purchasing/purchase-requisitions/` - List and create requisitions
- `GET/PUT/PATCH/DELETE /api/purchasing/purchase-requisitions/{id}/` - Manage individual requisitions
- `POST /api/purchasing/purchase-requisitions/{id}/submit/` - Submit for approval
- `POST /api/purchasing/purchase-requisitions/{id}/approve/` - Approve requisition
- `POST /api/purchasing/purchase-requisitions/{id}/convert-to-po/` - Convert to purchase order
- `GET /api/purchasing/purchase-requisitions/{id}/items/` - Get requisition items
- `GET /api/purchasing/purchase-requisitions/pending-approval/` - Get pending approvals
- `GET /api/purchasing/purchase-requisitions/approved-requisitions/` - Get approved requisitions

### Purchase Requisition Items
- `GET/POST /api/purchasing/purchase-requisition-items/` - List and create requisition items
- `GET/PUT/PATCH/DELETE /api/purchasing/purchase-requisition-items/{id}/` - Manage individual items

### Vendor Evaluations
- `GET/POST /api/purchasing/vendor-evaluations/` - List and create evaluations
- `GET/PUT/PATCH/DELETE /api/purchasing/vendor-evaluations/{id}/` - Manage individual evaluations
- `POST /api/purchasing/vendor-evaluations/{id}/calculate-rating/` - Calculate overall rating
- `GET /api/purchasing/vendor-evaluations/recent-evaluations/` - Get recent evaluations

### Purchase Contracts
- `GET/POST /api/purchasing/purchase-contracts/` - List and create contracts
- `GET/PUT/PATCH/DELETE /api/purchasing/purchase-contracts/{id}/` - Manage individual contracts
- `POST /api/purchasing/purchase-contracts/{id}/approve/` - Approve contract
- `GET /api/purchasing/purchase-contracts/{id}/items/` - Get contract items
- `GET /api/purchasing/purchase-contracts/active-contracts/` - Get active contracts
- `GET /api/purchasing/purchase-contracts/expiring-contracts/` - Get expiring contracts

### Purchase Contract Items
- `GET/POST /api/purchasing/purchase-contract-items/` - List and create contract items
- `GET/PUT/PATCH/DELETE /api/purchasing/purchase-contract-items/{id}/` - Manage individual items

### Dashboard and Analytics
- `GET /api/purchasing/dashboard/summary/` - Get purchasing summary
- `GET /api/purchasing/dashboard/vendor-summary/` - Get vendor summaries
- `GET /api/purchasing/dashboard/purchase-order-summary/` - Get purchase order summaries
- `GET /api/purchasing/dashboard/requisition-summary/` - Get requisition summaries
- `GET /api/purchasing/dashboard/contract-summary/` - Get contract summaries
- `GET /api/purchasing/dashboard/spending-analysis/` - Get spending analysis

## Business Logic

### Automated Processes
- **Vendor Code Generation**: Automatic vendor code generation (VEND-0001, VEND-0002, etc.)
- **Purchase Order Numbering**: Automatic PO number generation (PO-000001, PO-000002, etc.)
- **Requisition Numbering**: Automatic requisition number generation (PR-000001, PR-000002, etc.)
- **Contract Numbering**: Automatic contract number generation (CON-000001, CON-000002, etc.)
- **Total Calculations**: Automatic calculation of order totals, taxes, and item prices
- **Status Updates**: Automatic status updates based on received quantities and approvals

### Workflow Management
- **Requisition Workflow**: Draft → Submitted → Under Review → Approved/Rejected → Converted to PO
- **Purchase Order Workflow**: Draft → Pending Approval → Approved → Ordered → Partially Received → Received → Completed
- **Contract Workflow**: Draft → Active → Expired/Renewed/Terminated

### Performance Metrics
- **Vendor Ratings**: Overall, delivery, quality, price, and communication ratings
- **Delivery Performance**: Average delivery time and on-time delivery rates
- **Spending Analysis**: Total spent, average order values, and category breakdowns
- **Contract Management**: Active contracts, expiring contracts, and renewal tracking

## Security and Permissions

### Access Control
- **Organization Isolation**: Users can only access data from their organization
- **Role-based Access**: Different permission levels for different user roles
- **Audit Trail**: Complete tracking of all changes and approvals

### Data Validation
- **Input Validation**: Comprehensive validation of all input data
- **Business Rule Enforcement**: Enforcement of business rules and constraints
- **Referential Integrity**: Maintenance of data relationships and consistency

## Performance and Scalability

### Database Optimization
- **Efficient Queries**: Optimized database queries with proper indexing
- **Select Related**: Reduced database hits through strategic use of select_related
- **Aggregation**: Efficient calculation of totals and metrics

### Caching Strategy
- **Query Caching**: Caching of frequently accessed data
- **Result Caching**: Caching of dashboard and summary results
- **Performance Monitoring**: Continuous monitoring of API response times

## Integration Points

### Internal Modules
- **Inventory**: Product information and stock management
- **Finance**: Payment processing and financial reporting
- **HR**: Department information and approval workflows
- **Organizations**: Multi-tenant organization management

### External Systems
- **Vendor Portals**: Integration with vendor self-service portals
- **Payment Gateways**: Integration with payment processing systems
- **Document Management**: Integration with document storage and management systems

## Configuration

### Environment Variables
- `PURCHASING_DEFAULT_CURRENCY`: Default currency for purchases (default: USD)
- `PURCHASING_APPROVAL_REQUIRED`: Whether approval is required for purchases (default: true)
- `PURCHASING_MAX_ORDER_VALUE`: Maximum order value without additional approval (default: 10000)

### Settings Configuration
```python
# settings.py
PURCHASING_CONFIG = {
    'DEFAULT_CURRENCY': 'USD',
    'APPROVAL_REQUIRED': True,
    'MAX_ORDER_VALUE': 10000,
    'VENDOR_EVALUATION_FREQUENCY': 365,  # days
    'CONTRACT_EXPIRY_WARNING_DAYS': 30,
}
```

## Testing

### Test Coverage
- **Unit Tests**: Comprehensive testing of all models and business logic
- **API Tests**: Testing of all API endpoints and workflows
- **Integration Tests**: Testing of module interactions and data flow
- **Performance Tests**: Testing of API response times and database performance

### Running Tests
```bash
# Run all purchasing tests
python manage.py test apps.purchasing

# Run specific test classes
python manage.py test apps.purchasing.tests.PurchasingModelsTestCase
python manage.py test apps.purchasing.tests.PurchasingAPITestCase

# Run with coverage
coverage run --source='apps/purchasing' manage.py test apps.purchasing
coverage report
coverage html
```

## Deployment

### Requirements
- Django 4.2+
- Django REST Framework 3.14+
- PostgreSQL 12+
- Redis (for caching)

### Installation
1. Add `apps.purchasing` to `INSTALLED_APPS`
2. Run migrations: `python manage.py makemigrations purchasing`
3. Apply migrations: `python manage.py migrate`
4. Configure URLs in main `urls.py`
5. Set up admin interface
6. Configure permissions and user groups

### Migration Strategy
- **Zero-downtime Deployment**: Blue-green deployment strategy
- **Database Migrations**: Automated migration scripts with rollback capability
- **Data Validation**: Comprehensive data validation during migration
- **Performance Monitoring**: Continuous monitoring during deployment

## Monitoring and Maintenance

### Health Checks
- **API Endpoint Monitoring**: Continuous monitoring of API availability
- **Database Performance**: Monitoring of query performance and database health
- **Error Tracking**: Comprehensive error logging and alerting
- **Performance Metrics**: Monitoring of response times and throughput

### Maintenance Tasks
- **Data Cleanup**: Regular cleanup of old records and temporary data
- **Performance Optimization**: Regular review and optimization of database queries
- **Security Updates**: Regular security updates and vulnerability assessments
- **Backup and Recovery**: Regular backup procedures and disaster recovery testing

## Future Enhancements

### Planned Features
- **AI-powered Vendor Selection**: Machine learning-based vendor recommendation system
- **Advanced Analytics**: Predictive analytics for spending patterns and vendor performance
- **Mobile Application**: Mobile app for purchase order management and approval
- **Blockchain Integration**: Smart contracts and blockchain-based procurement
- **Supplier Portal**: Enhanced vendor self-service portal with real-time updates

### Scalability Improvements
- **Microservices Architecture**: Migration to microservices for better scalability
- **Event-driven Architecture**: Implementation of event-driven workflows
- **Real-time Notifications**: WebSocket-based real-time updates and notifications
- **Advanced Caching**: Implementation of distributed caching strategies

## Support and Documentation

### Documentation
- **API Documentation**: Comprehensive API documentation with examples
- **User Guides**: Step-by-step guides for common workflows
- **Developer Documentation**: Technical documentation for developers
- **Video Tutorials**: Video-based training materials

### Support Channels
- **Technical Support**: Dedicated technical support team
- **User Community**: Online community for user support and knowledge sharing
- **Training Programs**: Regular training sessions and workshops
- **Documentation Updates**: Regular updates to documentation and guides

## Contributing

### Development Guidelines
- **Code Standards**: Follow PEP 8 and Django coding standards
- **Testing Requirements**: All new features must include comprehensive tests
- **Documentation**: All new features must include documentation updates
- **Code Review**: All changes must go through code review process

### Contribution Process
1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request
7. Address review feedback
8. Merge after approval

## License

This module is part of the TidyGen ERP system and is licensed under the same terms as the main project.
