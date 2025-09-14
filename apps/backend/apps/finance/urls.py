"""
Finance URL configuration for TidyGen ERP platform.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.finance.views import (
    AccountViewSet, CustomerViewSet, VendorViewSet, InvoiceViewSet,
    InvoiceItemViewSet, PaymentViewSet, ExpenseViewSet, BudgetViewSet,
    BudgetItemViewSet, FinancialReportViewSet, TaxRateViewSet,
    RecurringInvoiceViewSet, RecurringInvoiceItemViewSet, FinanceDashboardViewSet
)

router = DefaultRouter()
router.register(r'accounts', AccountViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'vendors', VendorViewSet)
router.register(r'invoices', InvoiceViewSet)
router.register(r'invoice-items', InvoiceItemViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'expenses', ExpenseViewSet)
router.register(r'budgets', BudgetViewSet)
router.register(r'budget-items', BudgetItemViewSet)
router.register(r'financial-reports', FinancialReportViewSet)
router.register(r'tax-rates', TaxRateViewSet)
router.register(r'recurring-invoices', RecurringInvoiceViewSet)
router.register(r'recurring-invoice-items', RecurringInvoiceItemViewSet)
router.register(r'dashboard', FinanceDashboardViewSet, basename='finance-dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
