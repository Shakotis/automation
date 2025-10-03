"""Check which user and credentials are being used"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homework_scraper.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.credential_storage import SecureCredentialStorage

print("\n=== All Users ===\n")
users = User.objects.all()
for i, user in enumerate(users, 1):
    print(f"{i}. {user.username} (ID: {user.id})")
    
    storage = SecureCredentialStorage()
    creds = storage.get_user_credentials(user.id, 'manodienynas')
    if creds:
        print(f"   [OK] Manodienynas: {creds['username']}")
    else:
        print(f"   [NO] No Manodienynas credentials")
    print()

print("\n=== First User (used by test_exam_quick.py) ===")
first_user = User.objects.first()
if first_user:
    print(f"Username: {first_user.username}")
    storage = SecureCredentialStorage()
    creds = storage.get_user_credentials(first_user.id, 'manodienynas')
    if creds:
        print(f"Manodienynas login: {creds['username']}")
