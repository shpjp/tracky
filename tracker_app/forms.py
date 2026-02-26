from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import Application, CustomUser


class CustomAuthenticationForm(AuthenticationForm):
    """Custom authentication form that allows login with email or username"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update the username field to accept email or username
        self.fields['username'].label = 'Email or Username'
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary focus:border-primary dark:bg-gray-700 dark:text-white',
            'placeholder': 'Enter your email or username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary focus:border-primary dark:bg-gray-700 dark:text-white',
            'placeholder': 'Enter your password'
        })
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            # Try authentication with our custom backend
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    "Please enter a correct email/username and password. Note that both fields may be case-sensitive."
                )
            else:
                self.confirm_login_allowed(self.user_cache)
        
        return self.cleaned_data


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
        model = CustomUser
        fields = ("username", "email", "password1", "password2")
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user