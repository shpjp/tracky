from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Count, Q
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
import json
from .models import Application, CustomUser
from .forms import ApplicationForm, CustomUserCreationForm, CustomAuthenticationForm


@require_GET
def check_username_availability(request):
    """AJAX endpoint to check username availability"""
    username = request.GET.get('username', '').strip()
    
    if not username:
        return JsonResponse({'error': 'Username is required'}, status=400)
    
    if len(username) < 3:
        return JsonResponse({'error': 'Username must be at least 3 characters'}, status=400)
    
    # Check if username exists (case-insensitive)
    exists = CustomUser.objects.filter(username__iexact=username).exists()
    
    return JsonResponse({
        'available': not exists,
        'message': 'Username available' if not exists else f'Username "{username}" is already taken'
    })


@require_GET
def check_email_availability(request):
    """AJAX endpoint to check email availability"""
    email = request.GET.get('email', '').strip()
    
    if not email:
        return JsonResponse({'error': 'Email is required'}, status=400)
    
    if '@' not in email:
        return JsonResponse({'error': 'Invalid email format'}, status=400)
    
    # Check if email exists (case-insensitive)
    exists = CustomUser.objects.filter(email__iexact=email).exists()
    
    return JsonResponse({
        'available': not exists,
        'message': 'Email available' if not exists else f'An account with email "{email}" already exists'
    })


def register_view(request):
    """User registration view with duplicate account prevention"""
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in!')
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # Specify the backend when logging in
                user.backend = 'tracker_app.backends.EmailAuthBackend'
                login(request, user)
                messages.success(request, f'Welcome to Placement Tracker, {user.username}! Your account has been created successfully.')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, 'An error occurred during registration. Please try again.')
        else:
            # Show specific error messages for duplicate accounts
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        if 'already' in error.lower():
                            messages.error(request, error)
                        else:
                            messages.error(request, f'{field.replace("_", " ").title()}: {error}')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """Custom login view that works with CustomUser and email authentication"""
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            user.backend = 'tracker_app.backends.EmailAuthBackend'
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_page = request.GET.get('next', 'dashboard')
            return redirect(next_page)
        else:
            messages.error(request, 'Please enter a valid email/username and password.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    """Custom logout view that handles both GET and POST requests"""
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.success(request, f'Goodbye, {username}! You have been logged out.')
    
    return redirect('login')


@login_required
def dashboard_view(request):
    """Main dashboard with Kanban board"""
    # Get all applications for the current user
    applications = Application.objects.filter(user=request.user).select_related('user')
    
    # Group applications by status
    status_groups = {}
    for choice in Application.STATUS_CHOICES:
        status_code, status_name = choice
        status_groups[status_code] = {
            'name': status_name,
            'applications': applications.filter(status=status_code),
            'count': applications.filter(status=status_code).count()
        }
    
    # Calculate stats
    total_applications = applications.count()
    total_interviews = applications.filter(status__in=['INTERVIEW', 'OFFER']).count()
    total_offers = applications.filter(status='OFFER').count()
    success_rate = (total_offers / total_applications * 100) if total_applications > 0 else 0
    
    context = {
        'status_groups': status_groups,
        'total_applications': total_applications,
        'total_interviews': total_interviews,
        'total_offers': total_offers,
        'success_rate': round(success_rate, 1),
    }
    
    return render(request, 'tracker/dashboard.html', context)


@login_required
def create_application(request):
    """Create new application"""
    if request.method == 'POST':
        form = ApplicationForm(request.POST, user=request.user)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            
            # Log status for new application
            print(f"New application created: {application.company_name} - {application.role} ({application.status})")
            
            application.save()
            messages.success(request, f'Application to {application.company_name} created successfully!')
            return redirect('dashboard')
    else:
        form = ApplicationForm(user=request.user)
    
    return render(request, 'tracker/application_form.html', {
        'form': form,
        'title': 'Add New Application'
    })


@login_required
def update_application(request, pk):
    """Update existing application"""
    application = get_object_or_404(Application, pk=pk)
    
    # Ensure user can only edit their own applications
    if application.user != request.user:
        raise Http404("Application not found.")
    
    old_status = application.status
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, instance=application, user=request.user, instance_pk=pk)
        if form.is_valid():
            updated_application = form.save()
            
            # Log status change
            if old_status != updated_application.status:
                print(f"Status change: {updated_application.company_name} - {old_status} → {updated_application.status}")
            
            messages.success(request, f'Application to {updated_application.company_name} updated successfully!')
            return redirect('dashboard')
    else:
        form = ApplicationForm(instance=application, user=request.user, instance_pk=pk)
    
    return render(request, 'tracker/application_form.html', {
        'form': form,
        'title': f'Edit {application.company_name} Application',
        'application': application
    })


@login_required
def delete_application(request, pk):
    """Delete application"""
    application = get_object_or_404(Application, pk=pk)
    
    # Ensure user can only delete their own applications
    if application.user != request.user:
        raise Http404("Application not found.")
    
    if request.method == 'POST':
        company_name = application.company_name
        application.delete()
        messages.success(request, f'Application to {company_name} deleted successfully!')
        return redirect('dashboard')
    
    return render(request, 'tracker/application_confirm_delete.html', {
        'application': application
    })
