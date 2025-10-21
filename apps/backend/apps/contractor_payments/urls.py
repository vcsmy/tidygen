"""
URL configuration for contractor_payments app.
"""
from django.urls import path
from . import views

app_name = 'contractor_payments'

urlpatterns = [
    # Payment methods
    path('methods/', views.PaymentMethodListView.as_view(), name='payment-method-list'),
    
    # Contractor payments
    path('payments/', views.ContractorPaymentListCreateView.as_view(), name='payment-list-create'),
    path('payments/<int:pk>/', views.ContractorPaymentDetailView.as_view(), name='payment-detail'),
    path('freelancers/<int:freelancer_id>/stats/', views.payment_statistics, name='payment-stats'),
    
    # Escrow accounts
    path('escrow/', views.EscrowAccountListCreateView.as_view(), name='escrow-list-create'),
    
    # Payment schedules
    path('schedules/', views.PaymentScheduleView.as_view(), name='schedule-list-create'),
]
