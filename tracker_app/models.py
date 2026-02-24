import uuid
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
