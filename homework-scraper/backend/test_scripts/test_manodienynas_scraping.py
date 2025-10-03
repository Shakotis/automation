"""
Test script for Manodienynas and Eduka scraping
Run this to test the scrapers with your credentials
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homework_scraper.settings')
django.setup()

from django.contrib.auth.models import User
from scraper.scrapers import ManodienynasScaper, EdukaScraper
from authentication.credential_storage import SecureCredentialStorage

def test_manodienynas(user):
    """Test Manodienynas scraping"""
    print("\n" + "="*60)
    print("TESTING MANODIENYNAS")
    print("="*60 + "\n")
    
    try:
        # Check credentials
        credential_storage = SecureCredentialStorage()
        credentials = credential_storage.get_user_credentials(user.id, 'manodienynas')
        
        if not credentials:
            print("❌ No credentials found for Manodienynas")
            return
        
        print(f"✓ Found credentials for: {credentials['username']}")
        print(f"✓ Verified: {credentials.get('is_verified', False)}")
        
        # Create scraper
        print("\nStarting scraping...")
        print("-"*60 + "\n")
        
        scraper = ManodienynasScaper(user)
        homework = scraper.scrape_homework()
        
        # Display results
        print("\n" + "="*60)
        print(f"Scraping complete! Found {len(homework)} homework items")
        print("="*60 + "\n")
        
        for idx, hw in enumerate(homework, 1):
            print(f"\n--- Homework {idx} ---")
            print(f"Title: {hw['title']}")
            print(f"Subject: {hw['subject']}")
            print(f"Due Date: {hw['due_date']}")
            print(f"Description:\n{hw['description']}")
            print(f"URL: {hw['url']}")
        
        if not homework:
            print("⚠️  No homework found. Check the debug output above.")
            print(f"Screenshot saved to: debug_manodienynas_{user.id}.png")
        
        return len(homework)
        
    except Exception as e:
        print(f"❌ Error during Manodienynas testing: {e}")
        import traceback
        traceback.print_exc()
        return 0

def test_eduka(user):
    """Test Eduka scraping"""
    print("\n" + "="*60)
    print("TESTING EDUKA")
    print("="*60 + "\n")
    
    try:
        # Check credentials
        credential_storage = SecureCredentialStorage()
        credentials = credential_storage.get_user_credentials(user.id, 'eduka')
        
        if not credentials:
            print("❌ No credentials found for Eduka")
            return
        
        print(f"✓ Found credentials for: {credentials['username']}")
        print(f"✓ Verified: {credentials.get('is_verified', False)}")
        
        # Create scraper
        print("\nStarting scraping...")
        print("-"*60 + "\n")
        
        scraper = EdukaScraper(user)
        homework = scraper.scrape_homework()
        
        # Display results
        print("\n" + "="*60)
        print(f"Scraping complete! Found {len(homework)} homework items")
        print("="*60 + "\n")
        
        for idx, hw in enumerate(homework, 1):
            print(f"\n--- Homework {idx} ---")
            print(f"Title: {hw['title']}")
            print(f"Subject: {hw['subject']}")
            print(f"Due Date: {hw['due_date']}")
            print(f"Description:\n{hw['description']}")
            print(f"URL: {hw['url']}")
        
        if not homework:
            print("⚠️  No homework found. Check the debug output above.")
            print(f"Screenshot saved to: debug_eduka_{user.id}.png")
        
        return len(homework)
        
    except Exception as e:
        print(f"❌ Error during Eduka testing: {e}")
        import traceback
        traceback.print_exc()
        return 0

def test_scraping(user_email, site=None):
    """Test scraping for a specific user and site"""
    try:
        # Get user
        user = User.objects.get(email=user_email)
        print(f"\n{'='*60}")
        print(f"Testing scraping for user: {user.email}")
        print(f"{'='*60}")
        
        total_homework = 0
        
        if site is None or site == 'manodienynas':
            count = test_manodienynas(user)
            total_homework += count if count else 0
        
        if site is None or site == 'eduka':
            count = test_eduka(user)
            total_homework += count if count else 0
        
        # Final summary
        print("\n" + "="*60)
        print(f"TOTAL HOMEWORK FOUND: {total_homework}")
        print("="*60 + "\n")
        
    except User.DoesNotExist:
        print(f"❌ User not found: {user_email}")
        print("\nAvailable users:")
        for user in User.objects.all():
            print(f"  - {user.email}")
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    user_email = None
    site = None
    
    if len(sys.argv) > 1:
        user_email = sys.argv[1]
        if len(sys.argv) > 2:
            site = sys.argv[2]
    else:
        # Try to find the first user with credentials
        from authentication.models import UserCredential
        creds = UserCredential.objects.filter(site__in=['manodienynas', 'eduka']).first()
        if creds:
            user_email = creds.user.email
            print(f"Using user: {user_email}")
        else:
            print("Usage: python test_manodienynas_scraping.py <user_email> [site]")
            print("  site: 'manodienynas' or 'eduka' (optional, tests both if not specified)")
            print("\nOr add credentials through the web interface first")
            sys.exit(1)
    
    test_scraping(user_email, site)
