import uuid
import bcrypt
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils import timezone


class CustomUser(AbstractUser):
    """
    Custom user model with bcrypt password hashing
    """
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def set_password(self, raw_password):
        """Override to use bcrypt for password hashing"""
        if raw_password is None:
            self.password = None
        else:
            # Generate salt and hash password with bcrypt
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(raw_password.encode('utf-8'), salt)
            self.password = hashed.decode('utf-8')

    def check_password(self, raw_password):
        """Override to check bcrypt password"""
        if not raw_password or not self.password:
            return False
        try:
            return bcrypt.checkpw(raw_password.encode('utf-8'), self.password.encode('utf-8'))
        except ValueError:
            # Fallback to Django's default password checking for existing users
            from django.contrib.auth.hashers import check_password
            return check_password(raw_password, self.password)

    def __str__(self):
        return self.email


class Application(models.Model):
    STATUS_CHOICES = [
        ('WISHLIST', 'Wishlist'),
        ('APPLIED', 'Applied'),
        ('OA', 'Online Assessment'),
        ('INTERVIEW', 'Interview'),
        ('OFFER', 'Offer'),
        ('REJECTED', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='applications')
    company_name = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='WISHLIST')
    applied_date = models.DateField()
    interview_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['user', 'status']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.company_name} - {self.role} ({self.status})"
    
    def get_absolute_url(self):
        return reverse('application_detail', kwargs={'pk': self.pk})
    
    def get_short_notes(self):
        """Return first 50 characters of notes"""
        return self.notes[:50] + '...' if len(self.notes) > 50 else self.notes
    
    def can_transition_to_offer(self):
        """Check if application can transition to OFFER status"""
        # Prevent skipping from WISHLIST directly to OFFER
        if self.status == 'WISHLIST':
            return False
        return True


class RefreshToken(models.Model):
    """
    Model to store refresh tokens for JWT authentication
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='refresh_tokens')
    token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_revoked = models.BooleanField(default=False)
    device_info = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def is_expired(self):
        return timezone.now() > self.expires_at

    def revoke(self):
        self.is_revoked = True
        self.save()

    def __str__(self):
        return f"RefreshToken for {self.user.email}"
