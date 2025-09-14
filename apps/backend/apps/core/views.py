"""
Core views for iNEAT ERP platform.
"""

from rest_framework import generics, status, permissions, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import User, Permission, Role, SystemSettings, AuditLog
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    PasswordChangeSerializer, LoginSerializer, PermissionSerializer,
    RoleSerializer, SystemSettingsSerializer, AuditLogSerializer,
    Web3WalletConnectSerializer
)
from .permissions import IsOwnerOrReadOnly, IsSystemAdmin
from .filters import UserFilter, RoleFilter, AuditLogFilter


class BaseModelViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet for all ERP modules with common functionality.
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering = ['-created']
    
    def get_queryset(self):
        """
        Override to add organization filtering for self-hosted setup.
        In community edition, all data belongs to the same organization context.
        """
        return super().get_queryset()


class UserListCreateView(generics.ListCreateAPIView):
    """
    List and create users.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsSystemAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UserFilter
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'email', 'date_joined', 'last_login']
    ordering = ['-date_joined']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer
    
    @extend_schema(
        summary="List users",
        description="Get a list of all users in the system.",
        tags=["Users"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create user",
        description="Create a new user account.",
        tags=["Users"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a user.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer
    
    @extend_schema(
        summary="Get user",
        description="Retrieve a specific user by ID.",
        tags=["Users"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update user",
        description="Update user information.",
        tags=["Users"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Partially update user",
        description="Partially update user information.",
        tags=["Users"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete user",
        description="Delete a user account.",
        tags=["Users"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update current user profile.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    @extend_schema(
        summary="Get user profile",
        description="Get current user's profile information.",
        tags=["Users"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update user profile",
        description="Update current user's profile information.",
        tags=["Users"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class PasswordChangeView(APIView):
    """
    Change user password.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Change password",
        description="Change user password.",
        request=PasswordChangeSerializer,
        responses={200: {"description": "Password changed successfully"}},
        tags=["Authentication"]
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password changed successfully."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    """
    User login view.
    """
    serializer_class = LoginSerializer
    
    @extend_schema(
        summary="Login",
        description="Authenticate user and return JWT tokens.",
        request=LoginSerializer,
        responses={200: {"description": "Login successful"}},
        tags=["Authentication"]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        # Log the login
        AuditLog.objects.create(
            user=user,
            action='login',
            model_name='User',
            object_id=str(user.id),
            object_repr=str(user),
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })


class LogoutView(APIView):
    """
    User logout view.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Logout",
        description="Logout user and blacklist refresh token.",
        responses={200: {"description": "Logout successful"}},
        tags=["Authentication"]
    )
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            # Log the logout
            AuditLog.objects.create(
                user=request.user,
                action='logout',
                model_name='User',
                object_id=str(request.user.id),
                object_repr=str(request.user),
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({"message": "Logout successful."})
        except Exception as e:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class Web3WalletConnectView(APIView):
    """
    Web3 wallet connection view.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Connect Web3 wallet",
        description="Connect and verify Web3 wallet address.",
        request=Web3WalletConnectSerializer,
        responses={200: {"description": "Wallet connected successfully"}},
        tags=["Web3"]
    )
    def post(self, request):
        serializer = Web3WalletConnectSerializer(data=request.data)
        if serializer.is_valid():
            wallet_address = serializer.validated_data['wallet_address']
            
            # Update user's wallet address
            user = request.user
            user.wallet_address = wallet_address
            user.wallet_verified = True  # TODO: Implement proper verification
            user.save()
            
            # Log the wallet connection
            AuditLog.objects.create(
                user=user,
                action='update',
                model_name='User',
                object_id=str(user.id),
                object_repr=str(user),
                changes={'wallet_address': wallet_address},
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({
                "message": "Wallet connected successfully.",
                "wallet_address": wallet_address
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PermissionListView(generics.ListAPIView):
    """
    List all permissions.
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated, IsSystemAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'codename', 'description', 'module']
    ordering_fields = ['name', 'module']
    ordering = ['module', 'name']
    
    @extend_schema(
        summary="List permissions",
        description="Get a list of all system permissions.",
        tags=["Permissions"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class RoleListCreateView(generics.ListCreateAPIView):
    """
    List and create roles.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated, IsSystemAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RoleFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created']
    ordering = ['name']
    
    @extend_schema(
        summary="List roles",
        description="Get a list of all roles.",
        tags=["Roles"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create role",
        description="Create a new role.",
        tags=["Roles"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a role.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated, IsSystemAdmin]
    
    @extend_schema(
        summary="Get role",
        description="Retrieve a specific role by ID.",
        tags=["Roles"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update role",
        description="Update role information.",
        tags=["Roles"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Partially update role",
        description="Partially update role information.",
        tags=["Roles"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete role",
        description="Delete a role.",
        tags=["Roles"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class SystemSettingsListView(generics.ListAPIView):
    """
    List system settings.
    """
    queryset = SystemSettings.objects.all()
    serializer_class = SystemSettingsSerializer
    permission_classes = [permissions.IsAuthenticated, IsSystemAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['key', 'description']
    ordering_fields = ['key', 'created']
    ordering = ['key']
    
    @extend_schema(
        summary="List system settings",
        description="Get a list of all system settings.",
        tags=["System"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AuditLogListView(generics.ListAPIView):
    """
    List audit logs.
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsSystemAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = AuditLogFilter
    search_fields = ['user__username', 'user__email', 'model_name', 'object_repr']
    ordering_fields = ['created', 'action', 'model_name']
    ordering = ['-created']
    
    @extend_schema(
        summary="List audit logs",
        description="Get a list of all audit logs.",
        tags=["System"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Health check",
    description="Check system health status.",
    responses={200: {"description": "System is healthy"}},
    tags=["System"]
)
def health_check(request):
    """
    System health check endpoint.
    """
    return Response({
        "status": "healthy",
        "timestamp": timezone.now().isoformat(),
        "version": "1.0.0"
    })