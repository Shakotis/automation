#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homework_scraper.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.credential_storage import SecureCredentialStorage

def check_verification_update():
    """Check if verification status updates work"""
    
    user = User.objects.get(username='testuser')
    credential_storage = SecureCredentialStorage()
    
    print("--- Before update ---")
    all_credentials = credential_storage.get_all_user_credentials(user.id)
    for site, creds in all_credentials.items():
        print(f"{site}: verified = {creds.get('is_verified', False)}")
    
    print("\n--- Updating verification status ---")
    success1 = credential_storage.update_credential_verification(user.id, 'manodienynas', True)
    success2 = credential_storage.update_credential_verification(user.id, 'eduka', True)
    print(f"Manodienynas update: {success1}")
    print(f"Eduka update: {success2}")
    
    print("\n--- After update ---")
    all_credentials = credential_storage.get_all_user_credentials(user.id)
    for site, creds in all_credentials.items():
        print(f"{site}: verified = {creds.get('is_verified', False)}")

if __name__ == '__main__':
    check_verification_update()