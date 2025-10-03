"""
Test verification system with REAL credentials from database
This will actually attempt to login to verify credentials work
"""
import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homework_scraper.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.credential_storage import SecureCredentialStorage
from authentication.verification_service import CredentialVerificationService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_real_credentials():
    """Test verification with actual stored credentials"""
    print("\n" + "="*60)
    print("TESTING VERIFICATION WITH REAL CREDENTIALS")
    print("="*60)
    
    # Get the first user (or specify email)
    try:
        # Change this to your actual email if needed
        user = User.objects.first()
        if not user:
            print("❌ No users found in database!")
            print("   Create a user first through the web dashboard")
            return
        
        print(f"✓ Testing with user: {user.email or user.username}")
        print()
        
    except Exception as e:
        print(f"❌ Error getting user: {e}")
        return
    
    credential_storage = SecureCredentialStorage()
    verification_service = CredentialVerificationService()
    
    # Test both sites
    sites = ['manodienynas', 'eduka']
    
    for site in sites:
        print("=" * 60)
        print(f"TESTING {site.upper()}")
        print("=" * 60)
        
        # Check if credentials exist
        try:
            stored_creds = credential_storage.get_user_credentials(user.id, site)
            
            if not stored_creds:
                print(f"⚠️  No credentials stored for {site}")
                print(f"   Go to http://localhost:3000/settings to add credentials")
                print()
                continue
            
            # Show what we have (without showing password)
            print(f"✓ Found stored credentials:")
            print(f"  Username: {stored_creds.get('username', 'N/A')}")
            print(f"  Password: {'***' if stored_creds.get('password') else '(empty)'}")
            print(f"  URL: {stored_creds.get('additional_data', {}).get('url', 'N/A')}")
            print(f"  Currently Verified: {stored_creds.get('is_verified', False)}")
            print()
            
        except Exception as e:
            print(f"❌ Error checking stored credentials: {e}")
            continue
        
        # Attempt verification (ACTUAL LOGIN TEST)
        try:
            print(f"🔐 Attempting to login to {site}...")
            print(f"   This will ACTUALLY try to login with your stored credentials")
            print()
            
            success, message = verification_service.verify_credentials(
                user.id, 
                site
            )
            
            print()
            if success:
                print(f"✅ {site.upper()} VERIFICATION SUCCESSFUL!")
                print(f"   Message: {message}")
                print(f"   Your credentials work and have been marked as verified")
            else:
                print(f"❌ {site.upper()} VERIFICATION FAILED!")
                print(f"   Message: {message}")
                print(f"   Please check your credentials in the dashboard")
            print()
                
        except Exception as e:
            print(f"❌ Error during {site} verification: {e}")
            import traceback
            traceback.print_exc()
            print()
        
        # Check updated verification status
        try:
            updated_creds = credential_storage.get_user_credentials(user.id, site)
            if updated_creds:
                print(f"📊 Updated verification status: {updated_creds.get('is_verified', False)}")
            print()
        except Exception as e:
            print(f"❌ Error checking updated credentials: {e}")
            print()


def show_all_credentials():
    """Show all stored credentials for debugging"""
    print("\n" + "="*60)
    print("ALL STORED CREDENTIALS")
    print("="*60)
    
    from authentication.models import UserCredential
    
    credentials = UserCredential.objects.all()
    
    if not credentials.exists():
        print("No credentials stored yet")
        return
    
    credential_storage = SecureCredentialStorage()
    
    for cred in credentials:
        print(f"\nUser: {cred.user.email or cred.user.username}")
        print(f"Site: {cred.site}")
        
        # Decrypt to show username (but not password)
        try:
            decrypted = credential_storage.get_user_credentials(cred.user.id, cred.site)
            if decrypted:
                print(f"Username: {decrypted.get('username', 'N/A')}")
                print(f"Password: {'***' if decrypted.get('password') else '(empty)'}")
        except:
            print(f"Username: (encrypted)")
            print(f"Password: (encrypted)")
        
        print(f"Verified: {cred.is_verified}")
        print(f"Last Updated: {cred.updated_at}")


if __name__ == "__main__":
    print("🚀 Real Credential Verification Test")
    print("=" * 60)
    print()
    print("⚠️  WARNING: This will attempt ACTUAL logins to verify credentials")
    print("   Make sure you have stored your real credentials in the dashboard")
    print()
    
    # Show what we have
    show_all_credentials()
    
    # Test verification
    test_real_credentials()
    
    print("\n" + "="*60)
    print("✅ VERIFICATION TEST COMPLETED")
    print("="*60)
    print()
    print("📝 SUMMARY:")
    print("- Verification DOES actually attempt to login")
    print("- It uses ManoDienynasSimple.login() which tries real authentication")
    print("- Success = credentials work and site accepts them")
    print("- Failure = credentials don't work or site rejects them")
    print()
    print("🔧 NEXT STEPS:")
    print("1. If verification failed, update credentials at http://localhost:3000/settings")
    print("2. If verification succeeded, try running the scraper")
    print("3. Check screenshots in backend/ directory if verification failed")
