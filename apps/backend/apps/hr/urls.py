"""
HR management URL configuration for TidyGen ERP platform.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.hr.views import (
    DepartmentViewSet, PositionViewSet, EmployeeViewSet, AttendanceViewSet,
    LeaveTypeViewSet, LeaveRequestViewSet, PayrollPeriodViewSet, PayrollViewSet,
    PerformanceReviewViewSet, TrainingViewSet, TrainingEnrollmentViewSet,
    DocumentViewSet, PolicyViewSet, PolicyAcknowledgmentViewSet, HRDashboardViewSet
)

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'positions', PositionViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'leave-types', LeaveTypeViewSet)
router.register(r'leave-requests', LeaveRequestViewSet)
router.register(r'payroll-periods', PayrollPeriodViewSet)
router.register(r'payrolls', PayrollViewSet)
router.register(r'performance-reviews', PerformanceReviewViewSet)
router.register(r'trainings', TrainingViewSet)
router.register(r'training-enrollments', TrainingEnrollmentViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'policies', PolicyViewSet)
router.register(r'policy-acknowledgments', PolicyAcknowledgmentViewSet)
router.register(r'dashboard', HRDashboardViewSet, basename='hr-dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
