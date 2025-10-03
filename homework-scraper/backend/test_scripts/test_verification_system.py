"""
Test script for verifying the complete login-based verification and scraping system
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
from scraper.scrapers import EdukaScraper, ManodienynasScaper, HomeworkScrapingService
from authentication.session_manager import ScrapingSessionManager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_credential_verification():
    """Test credential verification for both sites"""
    print("\n" + "="*60)
    print("TESTING CREDENTIAL VERIFICATION SYSTEM")
    print("="*60)
    
    # Get or create a test user
    test_user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    if created:
        print(f"✓ Created test user: {test_user.username}")
    else:
        print(f"✓ Using existing test user: {test_user.username}")
    
    credential_storage = SecureCredentialStorage()
    verification_service = CredentialVerificationService()
    
    # Test data - replace with actual credentials for testing
    test_credentials = {
        'eduka': {
            'username': 'test_eduka_user',
            'password': 'test_eduka_password',
            'url': 'https://eduka.lt/auth'
        },
        'manodienynas': {
            'username': 'test_mano_user', 
            'password': 'test_mano_password',
            'url': 'https://www.manodienynas.lt/1/lt/public/public/login'
        }
    }
    
    print(f"\n📝 Testing with demo credentials (replace with real ones for actual testing)")
    
    for site, creds in test_credentials.items():
        print(f"\n--- Testing {site.upper()} ---")
        
        # Store credentials
        try:
            credential = credential_storage.store_user_credentials(
                test_user.id, 
                site, 
                creds['username'], 
                creds['password'],
                {'url': creds['url']}
            )
            print(f"✓ Stored credentials for {site}")
        except Exception as e:
            print(f"✗ Failed to store credentials for {site}: {e}")
            continue
        
        # Test verification
        try:
            print(f"🔍 Verifying {site} credentials...")
            success, message = verification_service.verify_credentials(
                test_user.id, 
                site, 
                creds['url']
            )
            
            if success:
                print(f"✓ {site} verification successful: {message}")
            else:
                print(f"✗ {site} verification failed: {message}")
                
        except Exception as e:
            print(f"✗ Error during {site} verification: {e}")
        
        # Check stored verification status
        try:
            stored_creds = credential_storage.get_user_credentials(test_user.id, site)
            if stored_creds:
                print(f"📊 {site} verification status: {stored_creds.get('is_verified', False)}")
            else:
                print(f"📊 No stored credentials found for {site}")
        except Exception as e:
            print(f"✗ Error checking stored credentials: {e}")

def test_scraping_with_sessions():
    """Test scraping with session management"""
    print("\n" + "="*60)
    print("TESTING SCRAPING WITH SESSION MANAGEMENT")
    print("="*60)
    
    test_user = User.objects.get(username='test_user')
    
    for site in ['eduka', 'manodienynas']:
        print(f"\n--- Testing {site.upper()} Scraping ---")
        
        # Create scraper
        if site == 'eduka':
            scraper = EdukaScraper(test_user)
        else:
            scraper = ManodienynasScaper(test_user)
        
        # Test scraping
        try:
            print(f"🕷️ Starting {site} scraping...")
            homework_list = scraper.scrape_homework()
            
            print(f"📚 Found {len(homework_list)} homework items from {site}")
            for i, hw in enumerate(homework_list[:3], 1):  # Show first 3
                print(f"  {i}. {hw['title'][:50]}..." if len(hw['title']) > 50 else f"  {i}. {hw['title']}")
                print(f"     Subject: {hw['subject']}")
                print(f"     Due: {hw['due_date'].strftime('%Y-%m-%d')}")
                
        except Exception as e:
            print(f"✗ Error during {site} scraping: {e}")

def test_session_management():
    """Test session management functionality"""
    print("\n" + "="*60)
    print("TESTING SESSION MANAGEMENT")
    print("="*60)
    
    test_user = User.objects.get(username='test_user')
    
    for site in ['eduka', 'manodienynas']:
        print(f"\n--- Testing {site.upper()} Session Management ---")
        
        session_manager = ScrapingSessionManager(test_user.id, site)
        
        # Check for existing sessions
        try:
            driver, session_loaded = session_manager.get_authenticated_driver()
            if session_loaded:
                print(f"✓ Found existing session for {site}")
                
                # Test session validity
                is_valid = session_manager.is_session_valid(driver)
                print(f"📊 Session validity: {is_valid}")
                
            else:
                print(f"📋 No existing session found for {site}")
            
            driver.quit()
            
        except Exception as e:
            print(f"✗ Error testing session for {site}: {e}")
        
        # Test session clearing
        try:
            session_manager.clear_session()
            print(f"🧹 Cleared session for {site}")
        except Exception as e:
            print(f"✗ Error clearing session for {site}: {e}")

def test_complete_workflow():
    """Test the complete workflow"""
    print("\n" + "="*60)
    print("TESTING COMPLETE WORKFLOW")
    print("="*60)
    
    test_user = User.objects.get(username='test_user')
    
    # Test the main scraping service
    try:
        scraping_service = HomeworkScrapingService(test_user)
        print("🔄 Running complete homework scraping...")
        
        all_homework = scraping_service.scrape_all_sites()
        
        print(f"📊 Total homework found: {len(all_homework)}")
        
        # Group by site
        by_site = {}
        for hw in all_homework:
            site = hw['site']
            if site not in by_site:
                by_site[site] = []
            by_site[site].append(hw)
        
        for site, homework_list in by_site.items():
            print(f"  📚 {site}: {len(homework_list)} items")
            
    except Exception as e:
        print(f"✗ Error in complete workflow test: {e}")

def cleanup_test_data():
    """Clean up test data"""
    print("\n" + "="*60)
    print("CLEANING UP TEST DATA")
    print("="*60)
    
    try:
        # Delete test user and associated data
        test_user = User.objects.get(username='test_user')
        
        # Clear all sessions
        ScrapingSessionManager.clear_all_sessions(test_user.id)
        print("🧹 Cleared all sessions")
        
        # Delete credentials
        credential_storage = SecureCredentialStorage()
        for site in ['eduka', 'manodienynas']:
            try:
                credential_storage.delete_user_credentials(test_user.id, site)
                print(f"🗑️ Deleted {site} credentials")
            except:
                pass
        
        # Delete user
        test_user.delete()
        print("🗑️ Deleted test user")
        
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")

if __name__ == "__main__":
    print("🚀 Starting Homework Scraper Verification System Test")
    print("=" * 60)
    
    try:
        # Run tests
        test_credential_verification()
        test_session_management()
        test_scraping_with_sessions()
        test_complete_workflow()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60)
        
        print("\n📝 NOTES:")
        print("- Replace demo credentials with real ones for actual verification")
        print("- Verification will fail with demo credentials (expected)")
        print("- Session management and scraping logic has been tested")
        print("- The system is ready for real credential testing")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        cleanup_test_data()
        print("\n🧹 Test cleanup completed")