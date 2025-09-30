#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homework_scraper.settings')
django.setup()

from django.contrib.auth.models import User
from tasks.services import GoogleTasksService
from scraper.models import ScrapedHomework, UserScrapingPreferences
from authentication.models import GoogleOAuth

def test_google_tasks_sync():
    """Test Google Tasks synchronization"""
    
    print("=== Testing Google Tasks Sync ===")
    
    # Check for users with OAuth tokens
    oauth_users = GoogleOAuth.objects.all()
    if not oauth_users:
        print("No users with OAuth tokens found!")
        return
    
    for oauth in oauth_users:
        user = oauth.user
        print(f"\n--- Testing sync for user: {user.email} ---")
        
        # Ensure user has preferences and homework
        preferences, created = UserScrapingPreferences.objects.get_or_create(
            user=user,
            defaults={
                'auto_sync_to_google_tasks': True,
                'enable_manodienynas': True,
                'enable_eduka': True
            }
        )
        
        if created:
            print(f"Created preferences for {user.email}")
        
        # Check for existing homework
        homework_count = ScrapedHomework.objects.filter(user=user).count()
        print(f"Existing homework items: {homework_count}")
        
        if homework_count == 0:
            print("No homework found, creating some test homework...")
            # Use the scraping service to create some homework
            from scraper.scrapers import HomeworkScrapingService
            scraping_service = HomeworkScrapingService(user)
            homework_list = scraping_service.scrape_all_sites()
            print(f"Created {len(homework_list)} homework items")
        
        # Check unsynced homework
        unsynced = ScrapedHomework.objects.filter(user=user, synced_to_google_tasks=False)
        print(f"Unsynced homework items: {unsynced.count()}")
        
        if unsynced.count() == 0:
            print("All homework already synced!")
            continue
        
        # Test Google Tasks service
        try:
            tasks_service = GoogleTasksService(user)
            
            if not tasks_service.credentials:
                print("❌ No valid credentials found")
                continue
                
            if not tasks_service.service:
                print("❌ Could not initialize Google Tasks service")
                continue
            
            print("✅ Google Tasks service initialized")
            
            # Try to sync
            print("Attempting to sync homework to Google Tasks...")
            sync_result = tasks_service.sync_homework_to_tasks()
            
            print(f"✅ Sync completed!")
            print(f"   Synced: {sync_result['synced_count']} items")
            if sync_result['errors']:
                print(f"   Errors: {len(sync_result['errors'])}")
                for error in sync_result['errors']:
                    print(f"     - {error}")
            
        except Exception as e:
            print(f"❌ Sync failed: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_google_tasks_sync()