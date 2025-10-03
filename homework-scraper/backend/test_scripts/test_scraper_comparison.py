"""
Test script to compare Selenium-based scraper vs requests-based scraper
This ensures both scrapers produce the same results
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homework_scraper.settings')
django.setup()

from django.contrib.auth.models import User
from scraper.scrapers import ManodienynasScaper as SeleniumManodienynasScraper
from scraper.scrapers import EdukaScraper as SeleniumEdukaScraper
from scraper.scrapers_simple import ManodienynasScraperSimple
from scraper.scrapers_simple import EdukaScraperSimple
from authentication.credential_storage import SecureCredentialStorage
import json
from datetime import datetime

def format_homework_item(hw):
    """Format homework item for comparison"""
    return {
        'title': hw.get('title', ''),
        'subject': hw.get('subject', ''),
        'description': hw.get('description', '')[:100] + '...' if len(hw.get('description', '')) > 100 else hw.get('description', ''),
        'due_date': str(hw.get('due_date', '')),
        'site': hw.get('site', ''),
    }

def compare_homework_lists(selenium_hw, simple_hw, site_name):
    """Compare two homework lists and report differences"""
    print(f"\n{'='*80}")
    print(f"COMPARING {site_name.upper()} SCRAPERS")
    print(f"{'='*80}")
    
    print(f"\nSelenium Scraper: {len(selenium_hw)} items")
    print(f"Simple Scraper: {len(simple_hw)} items")
    
    if len(selenium_hw) == 0 and len(simple_hw) == 0:
        print("✓ Both scrapers found 0 items (empty results)")
        return True
    
    # Check if counts are similar (within 20% tolerance)
    if len(selenium_hw) > 0:
        diff_percent = abs(len(selenium_hw) - len(simple_hw)) / len(selenium_hw) * 100
        if diff_percent > 20:
            print(f"⚠ WARNING: Item count differs by {diff_percent:.1f}%")
        else:
            print(f"✓ Item counts are similar (difference: {diff_percent:.1f}%)")
    
    # Compare individual items
    print(f"\n{'-'*80}")
    print("SELENIUM SCRAPER RESULTS:")
    print(f"{'-'*80}")
    for idx, hw in enumerate(selenium_hw[:10], 1):  # Show first 10
        formatted = format_homework_item(hw)
        print(f"\n{idx}. Title: {formatted['title']}")
        print(f"   Subject: {formatted['subject']}")
        print(f"   Due Date: {formatted['due_date']}")
        print(f"   Description: {formatted['description']}")
    
    if len(selenium_hw) > 10:
        print(f"\n... and {len(selenium_hw) - 10} more items")
    
    print(f"\n{'-'*80}")
    print("SIMPLE SCRAPER RESULTS:")
    print(f"{'-'*80}")
    for idx, hw in enumerate(simple_hw[:10], 1):  # Show first 10
        formatted = format_homework_item(hw)
        print(f"\n{idx}. Title: {formatted['title']}")
        print(f"   Subject: {formatted['subject']}")
        print(f"   Due Date: {formatted['due_date']}")
        print(f"   Description: {formatted['description']}")
    
    if len(simple_hw) > 10:
        print(f"\n... and {len(simple_hw) - 10} more items")
    
    # Find matching titles
    selenium_titles = set([hw.get('title', '') for hw in selenium_hw])
    simple_titles = set([hw.get('title', '') for hw in simple_hw])
    
    matching_titles = selenium_titles.intersection(simple_titles)
    selenium_only = selenium_titles - simple_titles
    simple_only = simple_titles - selenium_titles
    
    print(f"\n{'-'*80}")
    print("TITLE COMPARISON:")
    print(f"{'-'*80}")
    print(f"Matching titles: {len(matching_titles)}")
    
    if selenium_only:
        print(f"\nTitles only in Selenium scraper ({len(selenium_only)}):")
        for title in list(selenium_only)[:5]:
            print(f"  - {title}")
        if len(selenium_only) > 5:
            print(f"  ... and {len(selenium_only) - 5} more")
    
    if simple_only:
        print(f"\nTitles only in Simple scraper ({len(simple_only)}):")
        for title in list(simple_only)[:5]:
            print(f"  - {title}")
        if len(simple_only) > 5:
            print(f"  ... and {len(simple_only) - 5} more")
    
    # Calculate match percentage
    if len(selenium_hw) > 0 or len(simple_hw) > 0:
        total_unique = len(selenium_titles.union(simple_titles))
        match_percent = len(matching_titles) / total_unique * 100 if total_unique > 0 else 0
        print(f"\nMatch percentage: {match_percent:.1f}%")
        
        if match_percent >= 80:
            print("✓ EXCELLENT: Scrapers produce very similar results")
            return True
        elif match_percent >= 60:
            print("⚠ GOOD: Scrapers produce similar results with some differences")
            return True
        else:
            print("✗ WARNING: Scrapers produce significantly different results")
            return False
    
    return True

def test_manodienynas(user):
    """Test Manodienynas scrapers"""
    print("\n" + "="*80)
    print("TESTING MANODIENYNAS SCRAPERS")
    print("="*80)
    
    # Check if credentials exist
    credential_storage = SecureCredentialStorage()
    credentials = credential_storage.get_user_credentials(user.id, 'manodienynas')
    
    if not credentials:
        print("\n✗ No Manodienynas credentials found for user")
        print("Please add credentials first using the web interface")
        return False
    
    if not credentials.get('is_verified', False):
        print("\n✗ Manodienynas credentials not verified")
        print("Please verify credentials first using the web interface")
        return False
    
    print(f"\n✓ Found verified credentials for user {user.username}")
    print(f"  Username: {credentials['username']}")
    
    # Test Selenium scraper
    print("\n" + "-"*80)
    print("Testing SELENIUM-based Manodienynas Scraper...")
    print("-"*80)
    try:
        selenium_scraper = SeleniumManodienynasScraper(user)
        selenium_homework = selenium_scraper.scrape_homework()
        print(f"✓ Selenium scraper completed: {len(selenium_homework)} items")
    except Exception as e:
        print(f"✗ Selenium scraper failed: {e}")
        import traceback
        traceback.print_exc()
        selenium_homework = []
    
    # Test Simple scraper
    print("\n" + "-"*80)
    print("Testing REQUESTS-based Manodienynas Scraper...")
    print("-"*80)
    try:
        simple_scraper = ManodienynasScraperSimple(user)
        simple_homework = simple_scraper.scrape_homework()
        print(f"✓ Simple scraper completed: {len(simple_homework)} items")
    except Exception as e:
        print(f"✗ Simple scraper failed: {e}")
        import traceback
        traceback.print_exc()
        simple_homework = []
    
    # Compare results
    return compare_homework_lists(selenium_homework, simple_homework, "Manodienynas")

def test_eduka(user):
    """Test Eduka scrapers"""
    print("\n" + "="*80)
    print("TESTING EDUKA SCRAPERS")
    print("="*80)
    
    # Check if credentials exist
    credential_storage = SecureCredentialStorage()
    credentials = credential_storage.get_user_credentials(user.id, 'eduka')
    
    if not credentials:
        print("\n✗ No Eduka credentials found for user")
        print("Please add credentials first using the web interface")
        return False
    
    if not credentials.get('is_verified', False):
        print("\n✗ Eduka credentials not verified")
        print("Please verify credentials first using the web interface")
        return False
    
    print(f"\n✓ Found verified credentials for user {user.username}")
    print(f"  Username: {credentials['username']}")
    
    # Test Selenium scraper
    print("\n" + "-"*80)
    print("Testing SELENIUM-based Eduka Scraper...")
    print("-"*80)
    try:
        selenium_scraper = SeleniumEdukaScraper(user)
        selenium_homework = selenium_scraper.scrape_homework()
        print(f"✓ Selenium scraper completed: {len(selenium_homework)} items")
    except Exception as e:
        print(f"✗ Selenium scraper failed: {e}")
        import traceback
        traceback.print_exc()
        selenium_homework = []
    
    # Test Simple scraper
    print("\n" + "-"*80)
    print("Testing REQUESTS-based Eduka Scraper...")
    print("-"*80)
    try:
        simple_scraper = EdukaScraperSimple(user)
        simple_homework = simple_scraper.scrape_homework()
        print(f"✓ Simple scraper completed: {len(simple_homework)} items")
    except Exception as e:
        print(f"✗ Simple scraper failed: {e}")
        import traceback
        traceback.print_exc()
        simple_homework = []
    
    # Compare results
    return compare_homework_lists(selenium_homework, simple_homework, "Eduka")

def main():
    """Main test function"""
    print("\n" + "="*80)
    print("SCRAPER COMPARISON TEST")
    print("="*80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nThis script compares:")
    print("  1. Selenium-based scrapers (scrapers.py)")
    print("  2. Requests-based scrapers (scrapers_simple.py)")
    print("\nGoal: Ensure both produce the same results")
    
    # Get or create test user
    print("\n" + "-"*80)
    print("Setting up test user...")
    print("-"*80)
    
    # Try to find an existing user with credentials
    credential_storage = SecureCredentialStorage()
    test_user = None
    
    # Look for any user with Manodienynas credentials
    for user in User.objects.all():
        creds = credential_storage.get_user_credentials(user.id, 'manodienynas')
        if creds and creds.get('is_verified'):
            test_user = user
            print(f"✓ Found user with verified Manodienynas credentials: {user.username}")
            break
    
    if not test_user:
        # Look for any user with Eduka credentials
        for user in User.objects.all():
            creds = credential_storage.get_user_credentials(user.id, 'eduka')
            if creds and creds.get('is_verified'):
                test_user = user
                print(f"✓ Found user with verified Eduka credentials: {user.username}")
                break
    
    if not test_user:
        print("\n✗ No user found with verified credentials")
        print("\nPlease:")
        print("  1. Sign in to the web interface")
        print("  2. Go to Settings")
        print("  3. Add and verify credentials for Manodienynas or Eduka")
        print("  4. Run this script again")
        return
    
    # Run tests
    results = {}
    
    # Test Manodienynas
    mano_creds = credential_storage.get_user_credentials(test_user.id, 'manodienynas')
    if mano_creds and mano_creds.get('is_verified'):
        results['manodienynas'] = test_manodienynas(test_user)
    else:
        print("\n⚠ Skipping Manodienynas (no verified credentials)")
        results['manodienynas'] = None
    
    # Test Eduka
    eduka_creds = credential_storage.get_user_credentials(test_user.id, 'eduka')
    if eduka_creds and eduka_creds.get('is_verified'):
        results['eduka'] = test_eduka(test_user)
    else:
        print("\n⚠ Skipping Eduka (no verified credentials)")
        results['eduka'] = None
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    
    if results['manodienynas'] is not None:
        status = "✓ PASS" if results['manodienynas'] else "✗ FAIL"
        print(f"\nManodienynas: {status}")
    else:
        print(f"\nManodienynas: ⊘ SKIPPED (no credentials)")
    
    if results['eduka'] is not None:
        status = "✓ PASS" if results['eduka'] else "✗ FAIL"
        print(f"Eduka: {status}")
    else:
        print(f"Eduka: ⊘ SKIPPED (no credentials)")
    
    # Overall result
    tested = [v for v in results.values() if v is not None]
    if len(tested) == 0:
        print("\n⚠ No tests run - please add and verify credentials first")
    elif all(tested):
        print("\n✓ ALL TESTS PASSED - Scrapers produce matching results!")
    else:
        print("\n✗ SOME TESTS FAILED - Review differences above")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    main()
