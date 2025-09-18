"""
URL configuration for Field Operations app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FieldTeamViewSet, TeamMemberViewSet, ServiceRouteViewSet,
    RouteStopViewSet, FieldJobViewSet, JobEquipmentViewSet, DispatchLogViewSet
)

router = DefaultRouter()
router.register(r'teams', FieldTeamViewSet)
router.register(r'team-members', TeamMemberViewSet)
router.register(r'routes', ServiceRouteViewSet)
router.register(r'route-stops', RouteStopViewSet)
router.register(r'jobs', FieldJobViewSet)
router.register(r'job-equipment', JobEquipmentViewSet)
router.register(r'dispatch-logs', DispatchLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
