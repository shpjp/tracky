from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Application URLs
    path('', views.dashboard_view, name='dashboard'),
    path('create/', views.create_application, name='create_application'),
    path('edit/<uuid:pk>/', views.update_application, name='update_application'),
    path('delete/<uuid:pk>/', views.delete_application, name='delete_application'),
]