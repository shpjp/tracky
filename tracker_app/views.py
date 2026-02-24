from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Count, Q
from django.http import Http404
from .models import Application
from .forms import ApplicationForm, CustomUserCreationForm


def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Placement Tracker.')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


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
