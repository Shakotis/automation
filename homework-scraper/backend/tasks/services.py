from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from django.conf import settings
from django.contrib.auth.models import User
from authentication.models import GoogleOAuth
from scraper.models import ScrapedHomework
from .models import GoogleTaskList
from datetime import datetime
import json

class GoogleTasksService:
    """Service for Google Tasks API integration"""
    
    def __init__(self, user):
        self.user = user
        self.credentials = self._get_user_credentials()
        self.service = None
        if self.credentials:
            self.service = build('tasks', 'v1', credentials=self.credentials)
    
    def _get_user_credentials(self):
        """Get user's Google OAuth credentials"""
        try:
            oauth_record = GoogleOAuth.objects.get(user=self.user)
            credentials = Credentials(
                token=oauth_record.access_token,
                refresh_token=oauth_record.refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=settings.GOOGLE_OAUTH2_CLIENT_ID,
                client_secret=settings.GOOGLE_OAUTH2_CLIENT_SECRET
            )
            return credentials
        except GoogleOAuth.DoesNotExist:
            return None
    
    def get_or_create_homework_tasklist(self):
        """Get or create the 'Homework' task list"""
        if not self.service:
            raise Exception("Google Tasks service not initialized")
        
        # Check if we already have the Homework task list stored
        try:
            homework_list = GoogleTaskList.objects.get(
                user=self.user, 
                name='Homework'
            )
            return homework_list.google_task_list_id
        except GoogleTaskList.DoesNotExist:
            pass
        
        # Get all task lists from Google
        results = self.service.tasklists().list().execute()
        task_lists = results.get('items', [])
        
        # Look for existing Homework list
        for task_list in task_lists:
            if task_list['title'].lower() == 'homework':
                # Store in our database
                homework_list, created = GoogleTaskList.objects.get_or_create(
                    user=self.user,
                    google_task_list_id=task_list['id'],
                    defaults={'name': 'Homework'}
                )
                return task_list['id']
        
        # Create new Homework task list
        task_list = {
            'title': 'Homework'
        }
        result = self.service.tasklists().insert(body=task_list).execute()
        
        # Store in our database
        GoogleTaskList.objects.create(
            user=self.user,
            google_task_list_id=result['id'],
            name='Homework'
        )
        
        return result['id']
    
    def create_task_from_homework(self, homework):
        """Create a Google Task from scraped homework"""
        if not self.service:
            raise Exception("Google Tasks service not initialized")
        
        task_list_id = self.get_or_create_homework_tasklist()
        
        # Prepare task data
        task_body = {
            'title': homework.title,
            'notes': f"Subject: {homework.subject}\n\nDescription: {homework.description}\n\nSource: {homework.get_site_display()}\nURL: {homework.url}",
        }
        
        # Add due date if available
        if homework.due_date:
            # Google Tasks API expects RFC 3339 format
            task_body['due'] = homework.due_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        # Create the task
        result = self.service.tasks().insert(
            tasklist=task_list_id,
            body=task_body
        ).execute()
        
        # Update homework record with Google Task ID
        homework.google_task_id = result['id']
        homework.synced_to_google_tasks = True
        homework.save()
        
        return result['id']
    
    def sync_homework_to_tasks(self, homework_queryset=None):
        """Sync scraped homework to Google Tasks"""
        if not self.service:
            raise Exception("Google Tasks service not initialized")
        
        if homework_queryset is None:
            # Get all unsynced homework for this user
            homework_queryset = ScrapedHomework.objects.filter(
                user=self.user,
                synced_to_google_tasks=False
            )
        
        synced_count = 0
        errors = []
        
        for homework in homework_queryset:
            try:
                self.create_task_from_homework(homework)
                synced_count += 1
            except Exception as e:
                errors.append(f"Error syncing {homework.title}: {str(e)}")
        
        return {
            'synced_count': synced_count,
            'errors': errors
        }
    
    def get_task_lists(self):
        """Get all user's task lists"""
        if not self.service:
            raise Exception("Google Tasks service not initialized")
        
        results = self.service.tasklists().list().execute()
        return results.get('items', [])
    
    def get_tasks(self, task_list_id):
        """Get tasks from a specific task list"""
        if not self.service:
            raise Exception("Google Tasks service not initialized")
        
        results = self.service.tasks().list(tasklist=task_list_id).execute()
        return results.get('items', [])

class GoogleOAuthService:
    """Service for Google OAuth authentication"""
    
    @staticmethod
    def get_authorization_url(request):
        """Get Google OAuth authorization URL"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
                    "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [request.build_absolute_uri('/auth/google/callback/')]
                }
            },
            scopes=[
                'https://www.googleapis.com/auth/tasks',
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile'
            ]
        )
        
        flow.redirect_uri = request.build_absolute_uri('/auth/google/callback/')
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        # Store state in session for security
        request.session['google_oauth_state'] = state
        
        return authorization_url
    
    @staticmethod
    def handle_oauth_callback(request, authorization_code, state):
        """Handle Google OAuth callback"""
        # Verify state
        if request.session.get('google_oauth_state') != state:
            raise Exception("Invalid OAuth state")
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
                    "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [request.build_absolute_uri('/auth/google/callback/')]
                }
            },
            scopes=[
                'https://www.googleapis.com/auth/tasks',
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile'
            ]
        )
        
        flow.redirect_uri = request.build_absolute_uri('/auth/google/callback/')
        flow.fetch_token(code=authorization_code)
        
        credentials = flow.credentials
        
        # Get user info
        user_info_service = build('oauth2', 'v2', credentials=credentials)
        user_info = user_info_service.userinfo().get().execute()
        
        # Create or get user
        user, created = User.objects.get_or_create(
            email=user_info['email'],
            defaults={
                'username': user_info['email'],
                'first_name': user_info.get('given_name', ''),
                'last_name': user_info.get('family_name', ''),
            }
        )
        
        # Store OAuth credentials
        oauth_record, created = GoogleOAuth.objects.update_or_create(
            user=user,
            defaults={
                'access_token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_expiry': credentials.expiry,
            }
        )
        
        return user