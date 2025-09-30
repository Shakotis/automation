#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homework_scraper.settings')
django.setup()

from django.contrib.auth.models import User
from scraper.scrapers import HomeworkScrapingService

def test_scraping():
    """Test the homework scraping functionality"""
    
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
    
    # Initialize the scraping service
    scraping_service = HomeworkScrapingService(user)
    
    # Test scraping all sites
    print("\n--- Testing homework scraping ---")
    all_homework = scraping_service.scrape_all_sites()
    
    print(f"\nFound {len(all_homework)} homework items:")
    for i, hw in enumerate(all_homework, 1):
        print(f"\n{i}. {hw['title']}")
        print(f"   Subject: {hw['subject']}")
        print(f"   Due Date: {hw['due_date']}")
        print(f"   Site: {hw['site']}")
        print(f"   Description: {hw['description'][:100]}...")
    
    # Check scraped homework in database
    from scraper.models import ScrapedHomework
    db_homework = ScrapedHomework.objects.filter(user=user)
    print(f"\nHomework saved to database: {db_homework.count()} items")
    
    for hw in db_homework:
        print(f"- {hw.title} ({hw.site}) - Due: {hw.due_date}")

if __name__ == '__main__':
    test_scraping()