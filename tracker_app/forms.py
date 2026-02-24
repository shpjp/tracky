from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Application


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['company_name', 'role', 'location', 'status', 'applied_date', 'interview_date', 'notes']
        widgets = {
            'applied_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'interview_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.instance_pk = kwargs.pop('instance_pk', None)
        super().__init__(*args, **kwargs)
    
    def clean_status(self):
        status = self.cleaned_data.get('status')
        
        # If we're updating an existing application
        if self.instance and self.instance.pk:
            # Prevent skipping from WISHLIST directly to OFFER
            if self.instance.status == 'WISHLIST' and status == 'OFFER':
                raise forms.ValidationError("Cannot move directly from Wishlist to Offer. Please update through the application process.")
        
        return status


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user