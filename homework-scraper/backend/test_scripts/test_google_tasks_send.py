"""
Test script to send a test task to Google Tasks
"""
import os
import sys
import django

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homework_scraper.settings')
django.setup()

from django.contrib.auth.models import User
from tasks.services import GoogleTasksService
from datetime import datetime, timedelta

def test_send_task():
    print("=" * 60)
    print("TESTING GOOGLE TASKS INTEGRATION")
    print("=" * 60)
    
    # Get the first user (should be you)
    try:
        user = User.objects.first()
        if not user:
            print("❌ No user found in database")
            return
        
        print(f"✓ Found user: {user.email}")
        
        # Initialize Google Tasks service
        tasks_service = GoogleTasksService(user)
        print("✓ Initialized Google Tasks service")
        
        if not tasks_service.service:
            print("❌ Google Tasks service not properly authenticated")
            print("   Make sure you've completed OAuth login")
            return
        
        # Get or create homework task list
        task_list_id = tasks_service.get_or_create_homework_tasklist()
        print(f"✓ Got task list ID: {task_list_id}")
        
        # Create a test task directly using the Google Tasks API
        test_task_body = {
            'title': '🧪 TEST TASK - Homework Scraper Integration',
            'notes': 'This is a test task created by the Homework Scraper backend to verify Google Tasks integration is working correctly.\n\nIf you see this in your Google Tasks, the integration is working! ✅\n\nYou can safely delete this task.',
            'due': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S.000Z')  # Due tomorrow
        }
        
        print(f"\n📝 Creating test task: {test_task_body['title']}")
        print(f"   Due: {test_task_body['due']}")
        
        # Send the task using Google Tasks API
        result = tasks_service.service.tasks().insert(
            tasklist=task_list_id,
            body=test_task_body
        ).execute()
        
        if result:
            print(f"\n✅ SUCCESS! Test task created in Google Tasks!")
            print(f"   Task ID: {result.get('id', 'N/A')}")
            print(f"   Title: {result.get('title', 'N/A')}")
            print(f"   Status: {result.get('status', 'N/A')}")
            print(f"\n🔍 Check your Google Tasks:")
            print(f"   - Google Tasks app on phone")
            print(f"   - Gmail sidebar")
            print(f"   - https://tasks.google.com/")
            print(f"\n   Look in the 'Homework' task list!")
        else:
            print(f"\n❌ FAILED to create task")
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_send_task()
