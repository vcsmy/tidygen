"""
URL configuration for TidyGen ERP project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API v1
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/inventory/', include('apps.inventory.urls')),
    path('api/v1/sales/', include('apps.sales.urls')),
    path('api/v1/purchasing/', include('apps.purchasing.urls')),
    path('api/v1/finance/', include('apps.finance.urls')),
    path('api/v1/hr/', include('apps.hr.urls')),
    path('api/v1/payroll/', include('apps.payroll.urls')),
    path('api/v1/scheduling/', include('apps.scheduling.urls')),
    path('api/v1/web3/', include('apps.web3.urls')),
    path('api/v1/ledger/', include('apps.ledger.urls')),
    path('api/v1/wallet/', include('apps.wallet.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),
    path('api/v1/facility-management/', include('apps.facility_management.urls')),
    path('api/v1/field-operations/', include('apps.field_operations.urls')),
    path('api/v1/audit-trail/', include('apps.audit_trail.urls')),
    path('api/v1/did-auth/', include('apps.did_auth.urls')), # Added DID authentication
    path('api/v1/freelancers/', include('apps.freelancers.urls')), # Community: Individual contractors
    path('api/v1/gig-management/', include('apps.gig_management.urls')), # Community: Job posting & assignment
    path('api/v1/contractor-payments/', include('apps.contractor_payments.urls')), # Community: Freelancer payments
    path('api/v1/freelancer-web3/', include('apps.freelancer_web3.urls')), # Community: Advanced Web3 features
    path('api/v1/', include('apps.core.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
