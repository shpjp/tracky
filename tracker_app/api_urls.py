from django.urls import path
from .api_views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    UserRegistrationView,
    LogoutView,
    UserProfileView,
    PasswordChangeView,
    ApplicationListCreateView,
    ApplicationDetailView,
    dashboard_stats,
    user_tokens,
    revoke_token
)

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', UserRegistrationView.as_view(), name='user_register'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    
    # User management
    path('user/profile/', UserProfileView.as_view(), name='user_profile'),
    path('user/change-password/', PasswordChangeView.as_view(), name='change_password'),
    path('user/tokens/', user_tokens, name='user_tokens'),
    path('user/tokens/<int:token_id>/revoke/', revoke_token, name='revoke_token'),
    
    # Applications
    path('applications/', ApplicationListCreateView.as_view(), name='application_list_create'),
    path('applications/<uuid:pk>/', ApplicationDetailView.as_view(), name='application_detail'),
    
    # Dashboard
    path('dashboard/stats/', dashboard_stats, name='dashboard_stats'),
]