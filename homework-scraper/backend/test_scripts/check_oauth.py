#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homework_scraper.settings')
django.setup()

from authentication.models import GoogleOAuth
from django.contrib.auth.models import User
from scraper.models import UserScrapingPreferences

def check_oauth_and_preferences():
    """Check OAuth tokens and preferences"""
    
    print("=== OAuth Tokens ===")
    oauth_tokens = GoogleOAuth.objects.all()
    if oauth_tokens:
        for oauth in oauth_tokens:
            print(f"User: {oauth.user.username}")
            print(f"Email: {oauth.user.email}")
            print(f"Has Access Token: {'Yes' if oauth.access_token else 'No'}")
            print(f"Has Refresh Token: {'Yes' if oauth.refresh_token else 'No'}")
            print(f"Token Expiry: {oauth.token_expiry}")
            print("---")
    else:
        print("No OAuth tokens found")
    
    print("\n=== User Preferences ===")
    preferences = UserScrapingPreferences.objects.all()
    if preferences:
        for pref in preferences:
            print(f"User: {pref.user.username}")
            print(f"Auto-sync to Google Tasks: {pref.auto_sync_to_google_tasks}")
            print(f"Enable Manodienynas: {pref.enable_manodienynas}")
            print(f"Enable Eduka: {pref.enable_eduka}")
            print("---")
    else:
        print("No user preferences found")

if __name__ == '__main__':
    check_oauth_and_preferences()