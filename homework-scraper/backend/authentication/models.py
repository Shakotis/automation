from django.db import models
from django.contrib.auth.models import User

class GoogleOAuth(models.Model):
    """Store Google OAuth tokens for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)  # Allow NULL refresh tokens
    token_expiry = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Google OAuth for {self.user.username}"

class UserCredential(models.Model):
    """Store encrypted user credentials for various sites"""
    SITE_CHOICES = [
        ('blackboard', 'Blackboard'),
        ('canvas', 'Canvas'),
        ('moodle', 'Moodle'),
        ('schoology', 'Schoology'),
        ('google_classroom', 'Google Classroom'),
        ('microsoft_teams', 'Microsoft Teams for Education'),
        ('manodienynas', 'Manodienynas.lt'),
        ('eduka', 'Eduka.lt'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credentials')
    site = models.CharField(max_length=50, choices=SITE_CHOICES)
    encrypted_data = models.TextField()  # Encrypted JSON containing username, password, etc.
    is_verified = models.BooleanField(default=False)
    last_verified = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'site']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_site_display()}"
