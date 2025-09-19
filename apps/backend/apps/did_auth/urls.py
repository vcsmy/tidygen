from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DIDDocumentViewSet, DIDRoleViewSet, DIDCredentialViewSet,
    DIDSessionViewSet, DIDPermissionViewSet
)

router = DefaultRouter()
router.register(r'documents', DIDDocumentViewSet, basename='diddocument')
router.register(r'roles', DIDRoleViewSet, basename='didrole')
router.register(r'credentials', DIDCredentialViewSet, basename='didcredential')
router.register(r'sessions', DIDSessionViewSet, basename='didsession')
router.register(r'permissions', DIDPermissionViewSet, basename='didpermission')

urlpatterns = [
    path('', include(router.urls)),
]
