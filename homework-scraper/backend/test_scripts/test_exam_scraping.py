"""
Test Manodienynas Exam Scraping and Google Calendar Sync
Run this script to test exam extraction and syncing to Google Calendar
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homework_scraper.settings')
django.setup()

from django.contrib.auth.models import User
from scraper.manodienynas_exams import scrape_manodienynas_exams
from scraper.models import ScrapedExam
from tasks.services import GoogleCalendarService


def test_exam_scraping():
    """Test exam scraping from Manodienynas"""
    print("\n" + "="*60)
    print("TEST: Manodienynas Exam Scraping")
    print("="*60 + "\n")
    
    # Get test user (change this to your username)
    username = input("Enter your username (or press Enter for 'admin'): ").strip()
    if not username:
        username = 'admin'
    
    try:
        user = User.objects.get(username=username)
        print(f"✓ Found user: {user.username}")
    except User.DoesNotExist:
        print(f"✗ User '{username}' not found!")
        print("Available users:")
        for u in User.objects.all():
            print(f"  - {u.username}")
        return False
    
    # Clear existing exams for clean test
    existing_count = ScrapedExam.objects.filter(user=user).count()
    if existing_count > 0:
        print(f"\nFound {existing_count} existing exams")
        clear = input("Clear existing exams? (y/n): ").strip().lower()
        if clear == 'y':
            ScrapedExam.objects.filter(user=user).delete()
            print("✓ Cleared existing exams")
    
    print("\n" + "-"*60)
    print("Starting exam scraping...")
    print("-"*60 + "\n")
    
    try:
        # Scrape exams
        exams = scrape_manodienynas_exams(user)
        
        if exams:
            print(f"\n✓ Successfully scraped {len(exams)} exams!")
            print("\nExam Details:")
            print("-"*60)
            for i, exam in enumerate(exams, 1):
                print(f"\n{i}. {exam.exam_name}")
                print(f"   Subject: {exam.subject}")
                print(f"   Date: {exam.exam_date.strftime('%Y-%m-%d')}")
                print(f"   Synced to Calendar: {exam.synced_to_google_calendar}")
            return True
        else:
            print("\n⚠ No exams found")
            print("This could mean:")
            print("  - No upcoming exams scheduled")
            print("  - Login credentials incorrect")
            print("  - Page structure changed")
            return False
            
    except Exception as e:
        print(f"\n✗ Exam scraping failed!")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_calendar_sync():
    """Test syncing exams to Google Calendar"""
    print("\n" + "="*60)
    print("TEST: Google Calendar Sync")
    print("="*60 + "\n")
    
    # Get test user
    username = input("Enter your username (or press Enter for 'admin'): ").strip()
    if not username:
        username = 'admin'
    
    try:
        user = User.objects.get(username=username)
        print(f"✓ Found user: {user.username}")
    except User.DoesNotExist:
        print(f"✗ User '{username}' not found!")
        return False
    
    # Check for unsynced exams
    unsynced_exams = ScrapedExam.objects.filter(
        user=user,
        synced_to_google_calendar=False
    )
    
    if not unsynced_exams:
        print("\n⚠ No unsynced exams found")
        print("Run the scraping test first to get some exam data.")
        return False
    
    print(f"\nFound {unsynced_exams.count()} exams to sync:")
    for exam in unsynced_exams:
        print(f"  - {exam.exam_name} ({exam.subject}) on {exam.exam_date.strftime('%Y-%m-%d')}")
    
    proceed = input("\nSync these exams to Google Calendar? (y/n): ").strip().lower()
    if proceed != 'y':
        print("Sync cancelled")
        return False
    
    print("\n" + "-"*60)
    print("Starting Google Calendar sync...")
    print("-"*60 + "\n")
    
    try:
        # Initialize calendar service
        calendar_service = GoogleCalendarService(user)
        
        if not calendar_service.service:
            print("✗ Google Calendar not connected!")
            print("\nPlease authenticate with Google first:")
            print("  1. Go to http://localhost:3000/settings")
            print("  2. Connect your Google account")
            print("  3. Run this test again")
            return False
        
        print("✓ Google Calendar service initialized")
        
        # Sync exams
        result = calendar_service.sync_exams_to_calendar()
        
        print(f"\n✓ Successfully synced {result['synced_count']} exams to Google Calendar!")
        
        if result['errors']:
            print("\nErrors encountered:")
            for error in result['errors']:
                print(f"  ✗ {error}")
        
        print("\n" + "-"*60)
        print("Calendar Events Created:")
        print("-"*60)
        
        # Show synced exams
        synced_exams = ScrapedExam.objects.filter(
            user=user,
            synced_to_google_calendar=True
        )
        
        for exam in synced_exams:
            print(f"\n📝 {exam.exam_name}")
            print(f"   Subject: {exam.subject}")
            print(f"   Date: {exam.exam_date.strftime('%Y-%m-%d')}")
            print(f"   Calendar Event ID: {exam.google_calendar_event_id}")
        
        print("\n✓ Check your Google Calendar for the exam events!")
        print("   They should appear as red events with reminders.")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Calendar sync failed!")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test runner"""
    print("\n" + "="*60)
    print("Manodienynas Exam Scraping & Calendar Sync Test")
    print("="*60)
    
    print("\nWhat would you like to test?")
    print("1. Scrape exams from Manodienynas")
    print("2. Sync exams to Google Calendar")
    print("3. Both (scrape then sync)")
    print("4. View existing exams")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        test_exam_scraping()
    elif choice == '2':
        test_calendar_sync()
    elif choice == '3':
        if test_exam_scraping():
            print("\n" + "="*60)
            input("\nPress Enter to continue to calendar sync...")
            test_calendar_sync()
    elif choice == '4':
        view_existing_exams()
    else:
        print("Invalid choice")


def view_existing_exams():
    """View existing scraped exams"""
    print("\n" + "="*60)
    print("Existing Exams")
    print("="*60 + "\n")
    
    username = input("Enter your username (or press Enter for 'admin'): ").strip()
    if not username:
        username = 'admin'
    
    try:
        user = User.objects.get(username=username)
        exams = ScrapedExam.objects.filter(user=user).order_by('exam_date')
        
        if not exams:
            print(f"\nNo exams found for user '{username}'")
            return
        
        print(f"\nFound {exams.count()} exams:\n")
        print("-"*60)
        
        for i, exam in enumerate(exams, 1):
            status = "✓ Synced" if exam.synced_to_google_calendar else "○ Not synced"
            print(f"\n{i}. {exam.exam_name}")
            print(f"   Subject: {exam.subject}")
            print(f"   Date: {exam.exam_date.strftime('%Y-%m-%d')}")
            print(f"   Site: {exam.site}")
            print(f"   Status: {status}")
            if exam.google_calendar_event_id:
                print(f"   Calendar Event: {exam.google_calendar_event_id}")
        
        print("\n" + "-"*60)
        
    except User.DoesNotExist:
        print(f"✗ User '{username}' not found!")


if __name__ == '__main__':
    main()
