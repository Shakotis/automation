from django.db import models
from django.contrib.auth.models import User

class GoogleOAuth(models.Model):
    """Store Google OAuth tokens for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_expiry = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Google OAuth for {self.user.username}"
