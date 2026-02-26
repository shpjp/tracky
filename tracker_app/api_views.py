from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
import jwt
from django.conf import settings

from .models import CustomUser, Application, RefreshToken as CustomRefreshToken
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    ApplicationSerializer,
    PasswordChangeSerializer
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token obtain view that uses email instead of username
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        user = serializer.validated_data['user']
        
        # Create JWT tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # Save refresh token in database
        expires_at = timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
        device_info = request.META.get('HTTP_USER_AGENT', '')[:255]
        ip_address = self.get_client_ip(request)

        CustomRefreshToken.objects.create(
            user=user,
            token=str(refresh),
            expires_at=expires_at,
            device_info=device_info,
            ip_address=ip_address
        )

        # Update user last login
        user.last_login = timezone.now()
        user.last_login_ip = ip_address
        user.save(update_fields=['last_login', 'last_login_ip'])

        return Response({
            'access': str(access),
            'refresh': str(refresh),
            'user': UserProfileSerializer(user).data
        })

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserRegistrationView(generics.CreateAPIView):
    """
    User registration view
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens for the new user
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # Save refresh token in database
        expires_at = timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
        device_info = request.META.get('HTTP_USER_AGENT', '')[:255]
        ip_address = request.META.get('REMOTE_ADDR')

        CustomRefreshToken.objects.create(
            user=user,
            token=str(refresh),
            expires_at=expires_at,
            device_info=device_info,
            ip_address=ip_address
        )

        return Response({
            'message': 'User registered successfully',
            'access': str(access),
            'refresh': str(refresh),
            'user': UserProfileSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom token refresh view that validates against database
    """
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response({'error': 'Refresh token is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # Check if token exists in database and is not revoked
        try:
            stored_token = CustomRefreshToken.objects.get(token=refresh_token, is_revoked=False)
            if stored_token.is_expired():
                stored_token.revoke()
                return Response({'error': 'Token has expired'}, 
                              status=status.HTTP_401_UNAUTHORIZED)
        except CustomRefreshToken.DoesNotExist:
            return Response({'error': 'Invalid refresh token'}, 
                          status=status.HTTP_401_UNAUTHORIZED)

        try:
            # Generate new access token
            refresh = RefreshToken(refresh_token)
            access = refresh.access_token

            response_data = {'access': str(access)}

            # If rotation is enabled, generate new refresh token
            if settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS', False):
                refresh.set_jti()
                refresh.set_exp()
                new_refresh = str(refresh)
                
                # Update stored token
                stored_token.token = new_refresh
                stored_token.expires_at = timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
                stored_token.save()
                
                response_data['refresh'] = new_refresh

            return Response(response_data)

        except TokenError as e:
            return Response({'error': 'Invalid token'}, 
                          status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """
    Logout view that revokes refresh tokens
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        
        if refresh_token:
            # Revoke specific token
            try:
                stored_token = CustomRefreshToken.objects.get(
                    token=refresh_token, 
                    user=request.user,
                    is_revoked=False
                )
                stored_token.revoke()
            except CustomRefreshToken.DoesNotExist:
                pass
        else:
            # Revoke all tokens for user
            CustomRefreshToken.objects.filter(
                user=request.user, 
                is_revoked=False
            ).update(is_revoked=True)

        return Response({'message': 'Logged out successfully'})


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile view
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class PasswordChangeView(APIView):
    """
    Password change view
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Revoke all refresh tokens to force re-login
            CustomRefreshToken.objects.filter(
                user=user, 
                is_revoked=False
            ).update(is_revoked=True)
            
            return Response({'message': 'Password changed successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApplicationListCreateView(generics.ListCreateAPIView):
    """
    List and create applications
    """
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update and delete applications
    """
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    """
    Dashboard statistics API
    """
    user = request.user
    applications = Application.objects.filter(user=user)
    
    # Group applications by status
    status_groups = {}
    for choice in Application.STATUS_CHOICES:
        status_code, status_name = choice
        status_applications = applications.filter(status=status_code)
        status_groups[status_code] = {
            'name': status_name,
            'count': status_applications.count(),
            'applications': ApplicationSerializer(status_applications, many=True).data
        }
    
    # Calculate stats
    total_applications = applications.count()
    total_interviews = applications.filter(status__in=['INTERVIEW', 'OFFER']).count()
    total_offers = applications.filter(status='OFFER').count()
    success_rate = (total_offers / total_applications * 100) if total_applications > 0 else 0
    
    return Response({
        'status_groups': status_groups,
        'stats': {
            'total_applications': total_applications,
            'total_interviews': total_interviews,
            'total_offers': total_offers,
            'success_rate': round(success_rate, 1),
        }
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_tokens(request):
    """
    Get user's active refresh tokens
    """
    tokens = CustomRefreshToken.objects.filter(
        user=request.user, 
        is_revoked=False
    ).order_by('-created_at')
    
    token_data = []
    for token in tokens:
        token_data.append({
            'id': token.id,
            'created_at': token.created_at,
            'expires_at': token.expires_at,
            'device_info': token.device_info,
            'ip_address': token.ip_address,
            'is_expired': token.is_expired()
        })
    
    return Response({'tokens': token_data})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def revoke_token(request, token_id):
    """
    Revoke a specific refresh token
    """
    try:
        token = CustomRefreshToken.objects.get(
            id=token_id, 
            user=request.user, 
            is_revoked=False
        )
        token.revoke()
        return Response({'message': 'Token revoked successfully'})
    except CustomRefreshToken.DoesNotExist:
        return Response({'error': 'Token not found'}, status=status.HTTP_404_NOT_FOUND)