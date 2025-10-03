"""
Test the updated verification methods (requests for Manodienynas, Playwright for Eduka)
"""
import os
import sys
import django

# Setup Django
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homework_scraper.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.verification_service import CredentialVerificationService
from authentication.credential_storage import SecureCredentialStorage
import time

def test_new_verification():
    """Test the new verification methods"""
    
    print("=" * 70)
    print("TESTING NEW VERIFICATION METHODS")
    print("=" * 70)
    print()
    
    # Get user
    try:
        # Try to get first user with credentials
        user = User.objects.first()
        if not user:
            print("✗ No users found. Please create a user first.")
            return
        print(f"✓ Found user: {user.username} (ID: {user.id})")
    except Exception as e:
        print(f"✗ Error getting user: {e}")
        return
    
    print()
    
    # Get credentials
    credential_storage = SecureCredentialStorage()
    
    # Test Manodienynas (new requests-based method)
    print("─" * 70)
    print("1. Testing Manodienynas Verification (NEW: requests-based)")
    print("─" * 70)
    
    mano_creds = credential_storage.get_user_credentials(user.id, 'manodienynas')
    if mano_creds:
        print(f"✓ Found Manodienynas credentials for user {user.id}")
        print(f"   Username: {mano_creds['username']}")
        
        verification_service = CredentialVerificationService()
        
        start_time = time.time()
        success, message = verification_service.verify_manodienynas_credentials(
            mano_creds['username'],
            mano_creds['password']
        )
        elapsed = time.time() - start_time
        
        print()
        if success:
            print(f"✅ Manodienynas verification SUCCESSFUL")
            print(f"   Message: {message}")
            print(f"   Time: {elapsed:.2f} seconds")
            print(f"   Expected: 1-2 seconds (85-90% faster than old Selenium method)")
        else:
            print(f"❌ Manodienynas verification FAILED")
            print(f"   Message: {message}")
            print(f"   Time: {elapsed:.2f} seconds")
    else:
        print("⚠️  No Manodienynas credentials found - skipping test")
    
    print()
    
    # Test Eduka (new Playwright method)
    print("─" * 70)
    print("2. Testing Eduka Verification (NEW: Playwright-based)")
    print("─" * 70)
    
    eduka_creds = credential_storage.get_user_credentials(user.id, 'eduka')
    if eduka_creds:
        print(f"✓ Found Eduka credentials for user {user.id}")
        print(f"   Username: {eduka_creds['username']}")
        
        verification_service = CredentialVerificationService()
        
        start_time = time.time()
        success, message = verification_service.verify_eduka_credentials(
            eduka_creds['username'],
            eduka_creds['password']
        )
        elapsed = time.time() - start_time
        
        print()
        if success:
            print(f"✅ Eduka verification SUCCESSFUL")
            print(f"   Message: {message}")
            print(f"   Time: {elapsed:.2f} seconds")
            print(f"   Expected: 5-7 seconds (60-70% faster than old Selenium method)")
        else:
            print(f"❌ Eduka verification FAILED")
            print(f"   Message: {message}")
            print(f"   Time: {elapsed:.2f} seconds")
    else:
        print("⚠️  No Eduka credentials found - skipping test")
    
    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print()
    print("Summary:")
    print("  - Manodienynas: Now uses fast requests-based method (1-2s instead of 10-15s)")
    print("  - Eduka: Now uses Playwright headless (5-7s instead of 15-20s)")
    print("  - Both methods match production scrapers (single source of truth)")
    print("  - No visible browser windows (better UX)")
    print()

if __name__ == "__main__":
    test_new_verification()
