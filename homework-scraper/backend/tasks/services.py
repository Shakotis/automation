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
import logging

logger = logging.getLogger(__name__)

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
            
            # Check if token is expired and refresh if needed
            if credentials.expired and credentials.refresh_token:
                try:
                    from google.auth.transport.requests import Request
                    credentials.refresh(Request())
                    
                    # Update the stored tokens
                    oauth_record.access_token = credentials.token
                    if credentials.expiry:
                        oauth_record.token_expiry = credentials.expiry
                    oauth_record.save()
                    
                    logger.info(f"Refreshed OAuth token for user {self.user.username}")
                except Exception as refresh_error:
                    logger.error(f"Failed to refresh OAuth token: {str(refresh_error)}")
                    return None
            
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
        
        # Get user's preference for task title format
        from scraper.models import UserScrapingPreferences
        try:
            preferences = UserScrapingPreferences.objects.get(user=self.user)
            title_format = preferences.google_tasks_title_format
        except UserScrapingPreferences.DoesNotExist:
            title_format = 'title'  # Default to task title
        
        # Set task title based on user preference
        if title_format == 'subject' and homework.subject:
            task_title = homework.subject
            task_notes = f"Task: {homework.title}\n\nDescription: {homework.description}\n\nSource: {homework.get_site_display()}\nURL: {homework.url}"
        else:
            task_title = homework.title
            task_notes = f"Subject: {homework.subject}\n\nDescription: {homework.description}\n\nSource: {homework.get_site_display()}\nURL: {homework.url}"
        
        # Prepare task data
        task_body = {
            'title': task_title,
            'notes': task_notes,
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
        # Use backend callback URL for now since frontend URL is not registered in Google Cloud Console
        backend_callback_url = request.build_absolute_uri('/api/auth/google/callback/')
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
                    "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [backend_callback_url]
                }
            },
            scopes=settings.GOOGLE_OAUTH2_SCOPES
        )
        
        flow.redirect_uri = backend_callback_url
        
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
        
        try:
            # Use backend callback URL for now since frontend URL is not registered in Google Cloud Console
            backend_callback_url = request.build_absolute_uri('/api/auth/google/callback/')
            
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
                        "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [backend_callback_url]
                    }
                },
                scopes=settings.GOOGLE_OAUTH2_SCOPES
            )
            
            flow.redirect_uri = backend_callback_url
            
            # Disable strict scope checking to handle automatic openid addition
            flow.fetch_token(code=authorization_code)
            
        except Exception as fetch_error:
            logger.error(f"Error during token fetch: {str(fetch_error)}")
            # Try alternative approach - create flow without strict scope checking
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
                        "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [request.build_absolute_uri('/api/auth/google/callback/')]
                    }
                },
                scopes=None  # Don't enforce specific scopes
            )
            flow.redirect_uri = request.build_absolute_uri('/api/auth/google/callback/')
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

class GoogleCalendarService:
    """Service for Google Calendar API integration"""
    
    def __init__(self, user):
        self.user = user
        self.credentials = self._get_user_credentials()
        self.service = None
        if self.credentials:
            self.service = build('calendar', 'v3', credentials=self.credentials)
    
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
    
    def get_calendars(self):
        """Get all user's calendars"""
        if not self.service:
            raise Exception("Google Calendar service not initialized")
        
        try:
            result = self.service.calendarList().list().execute()
            return result.get('items', [])
        except Exception as e:
            logger.error(f"Error getting calendars: {str(e)}")
            raise
    
    def create_homework_calendar(self):
        """Create or get a dedicated homework calendar"""
        if not self.service:
            raise Exception("Google Calendar service not initialized")
        
        try:
            # First, check if homework calendar already exists
            calendars = self.get_calendars()
            homework_calendar = None
            
            for calendar in calendars:
                if calendar.get('summary', '').lower() == 'homework':
                    homework_calendar = calendar
                    break
            
            if homework_calendar:
                return homework_calendar['id']
            
            # Create new homework calendar
            calendar_body = {
                'summary': 'Homework',
                'description': 'Calendar for homework assignments and exams',
                'timeZone': 'UTC'
            }
            
            created_calendar = self.service.calendars().insert(body=calendar_body).execute()
            return created_calendar['id']
            
        except Exception as e:
            logger.error(f"Error creating homework calendar: {str(e)}")
            raise
    
    def create_event_from_homework(self, homework, calendar_id=None):
        """Create a Google Calendar event from scraped homework"""
        if not self.service:
            raise Exception("Google Calendar service not initialized")
        
        try:
            if not calendar_id:
                calendar_id = self.create_homework_calendar()
            
            # Prepare event data
            event_body = {
                'summary': homework.title,
                'description': f"Subject: {homework.subject}\n\nDescription: {homework.description}\n\nSource: {homework.get_site_display()}\nURL: {homework.url}",
                'location': homework.get_site_display(),
            }
            
            # Add due date if available
            if homework.due_date:
                # For all-day events
                event_body['start'] = {
                    'date': homework.due_date.strftime('%Y-%m-%d'),
                    'timeZone': 'UTC'
                }
                event_body['end'] = {
                    'date': homework.due_date.strftime('%Y-%m-%d'),
                    'timeZone': 'UTC'
                }
            else:
                # Default to today if no due date
                from datetime import datetime
                today = datetime.now().strftime('%Y-%m-%d')
                event_body['start'] = {
                    'date': today,
                    'timeZone': 'UTC'
                }
                event_body['end'] = {
                    'date': today,
                    'timeZone': 'UTC'
                }
            
            # Create the event
            result = self.service.events().insert(
                calendarId=calendar_id,
                body=event_body
            ).execute()
            
            # Update homework record with Google Calendar event ID
            homework.google_calendar_event_id = result['id']
            homework.synced_to_google_calendar = True
            homework.save()
            
            return result['id']
            
        except Exception as e:
            logger.error(f"Error creating calendar event: {str(e)}")
            raise
    
    def sync_homework_to_calendar(self, homework_queryset=None, calendar_id=None):
        """Sync scraped homework to Google Calendar"""
        if not self.service:
            raise Exception("Google Calendar service not initialized")
        
        if homework_queryset is None:
            # Get all unsynced homework for this user
            homework_queryset = ScrapedHomework.objects.filter(
                user=self.user,
                synced_to_google_calendar=False
            )
        
        synced_count = 0
        errors = []
        
        for homework in homework_queryset:
            try:
                self.create_event_from_homework(homework, calendar_id)
                synced_count += 1
            except Exception as e:
                errors.append(f"Error syncing {homework.title}: {str(e)}")
        
        return {
            'synced_count': synced_count,
            'errors': errors
        }
    
    def create_exam_event(self, title, date, description=None, calendar_id=None):
        """Create an exam event in Google Calendar"""
        if not self.service:
            raise Exception("Google Calendar service not initialized")
        
        try:
            if not calendar_id:
                calendar_id = self.create_homework_calendar()
            
            event_body = {
                'summary': f"EXAM: {title}",
                'description': description or f"Exam: {title}",
                'start': {
                    'date': date.strftime('%Y-%m-%d'),
                    'timeZone': 'UTC'
                },
                'end': {
                    'date': date.strftime('%Y-%m-%d'),
                    'timeZone': 'UTC'
                },
                'colorId': '11'  # Red color for exams
            }
            
            result = self.service.events().insert(
                calendarId=calendar_id,
                body=event_body
            ).execute()
            
            return result['id']
            
        except Exception as e:
            logger.error(f"Error creating exam event: {str(e)}")
            raise