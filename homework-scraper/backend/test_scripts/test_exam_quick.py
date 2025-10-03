"""
Quick test for exam scraping - auto-runs with first available user
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homework_scraper.settings')
django.setup()

from django.contrib.auth.models import User
from scraper.manodienynas_exams import scrape_manodienynas_exams
from scraper.models import ScrapedExam

def main():
    print("\n" + "="*60)
    print("Quick Exam Scraping Test")
    print("="*60 + "\n")
    
    # Get first user
    try:
        user = User.objects.first()
        if not user:
            print("✗ No users found in database")
            return
        
        print(f"Testing with user: {user.username}\n")
        
        # Show existing exams
        existing = ScrapedExam.objects.filter(user=user).count()
        print(f"Existing exams in database: {existing}\n")
        
        print("-"*60)
        print("Starting exam scraping...")
        print("-"*60 + "\n")
        
        # Scrape
        exams = scrape_manodienynas_exams(user)
        
        print("\n" + "="*60)
        if exams:
            print(f"✓ SUCCESS! Scraped {len(exams)} exams")
            print("="*60 + "\n")
            
            print("Exam Summary:")
            for i, exam in enumerate(exams, 1):
                print(f"\n{i}. {exam.exam_name}")
                print(f"   📚 Subject: {exam.subject}")
                print(f"   📅 Date: {exam.exam_date.strftime('%Y-%m-%d')}")
                print(f"   {'✓' if exam.synced_to_google_calendar else '○'} Calendar: {exam.synced_to_google_calendar}")
        else:
            print("⚠ No exams found")
            print("="*60)
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
