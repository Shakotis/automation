#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homework_scraper.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.verification_service import CredentialVerificationService
from authentication.credential_storage import SecureCredentialStorage

def test_verification():
    """Test the credential verification functionality"""
    
    # Create or get a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    if created:
        print(f"Created test user: {user.username}")
    else:
        print(f"Using existing test user: {user.username}")
    
    # Initialize services
    credential_storage = SecureCredentialStorage()
    verification_service = CredentialVerificationService()
    
    # Test storing credentials
    print("\n--- Testing credential storage ---")
    
    # Store test credentials for manodienynas
    success = credential_storage.store_user_credentials(
        user_id=user.id,
        site='manodienynas',
        username='demo_user',
        password='demo_password',
        additional_data={'url': 'https://www.manodienynas.lt'}
    )
    print(f"Stored manodienynas credentials: {success}")
    
    # Store test credentials for eduka
    success = credential_storage.store_user_credentials(
        user_id=user.id,
        site='eduka',
        username='demo_user',
        password='demo_password',
        additional_data={'url': 'https://eduka.lt'}
    )
    print(f"Stored eduka credentials: {success}")
    
    # Test verification
    print("\n--- Testing credential verification ---")
    
    # Test manodienynas verification
    success, message = verification_service.verify_credentials(user.id, 'manodienynas')
    print(f"Manodienynas verification: {success} - {message}")
    
    # Test eduka verification
    success, message = verification_service.verify_credentials(user.id, 'eduka')
    print(f"Eduka verification: {success} - {message}")
    
    # Get all user credentials
    print("\n--- Stored credentials ---")
    all_credentials = credential_storage.get_all_user_credentials(user.id)
    for site, creds in all_credentials.items():
        print(f"{site}: {creds['username']} (verified: {creds.get('is_verified', False)})")

if __name__ == '__main__':
    test_verification()