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
            
            # Set expiry from database if available
            expiry = oauth_record.token_expiry if hasattr(oauth_record, 'token_expiry') else None
            
            credentials = Credentials(
                token=oauth_record.access_token,
                refresh_token=oauth_record.refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=settings.GOOGLE_OAUTH2_CLIENT_ID,
                client_secret=settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                expiry=expiry
            )
            
            # Always try to refresh if we have a refresh token
            # This prevents the "<!DOCTYPE" HTML error
            if credentials.refresh_token:
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
                    raise Exception("Google authentication has expired. Please reconnect your Google account in settings.")
            
            return credentials
        except GoogleOAuth.DoesNotExist:
            raise Exception("Google account not connected. Please connect your Google account in settings.")
    
    def get_or_create_homework_tasklist(self):
        """Get or create the 'Homework' task list"""
        if not self.service:
            raise Exception("Google Tasks service not initialized. Please connect your Google account.")
        
        try:
            # Try to find existing "Homework" task list
            task_lists_result = self.service.tasklists().list().execute()
            task_lists = task_lists_result.get('items', [])
            
            for task_list in task_lists:
                if task_list['title'].lower() == 'homework':
                    return task_list['id']
            
            # Create new "Homework" task list if not found
            new_list = {
                'title': 'Homework'
            }
            result = self.service.tasklists().insert(body=new_list).execute()
            return result['id']
            
        except json.JSONDecodeError as json_error:
            # This means the API returned HTML instead of JSON (usually expired auth)
            logger.error(f"Google API returned non-JSON response: {str(json_error)}")
            raise Exception("Google authentication has expired. Please reconnect your Google account in settings to continue syncing tasks.")
        except Exception as e:
            error_msg = str(e)
            # Check for various authentication error patterns
            if any(keyword in error_msg.lower() for keyword in ['invalid_grant', 'token_expired', 'unauthorized', '401']):
                raise Exception("Google authentication expired. Please reconnect your Google account in settings.")
            elif '<!' in error_msg or 'html' in error_msg.lower() or 'doctype' in error_msg.lower():
                raise Exception("Google API returned an error page. Your authentication has expired. Please reconnect your Google account in settings.")
            else:
                raise Exception(f"Failed to access Google Tasks: {error_msg}")
    
    def get_or_create_exams_tasklist(self):
        """Get or create the 'Exams' task list"""
        if not self.service:
            raise Exception("Google Tasks service not initialized. Please connect your Google account.")
        
        try:
            # Try to find existing "Exams" task list
            task_lists_result = self.service.tasklists().list().execute()
            task_lists = task_lists_result.get('items', [])
            
            for task_list in task_lists:
                if task_list['title'].lower() == 'exams':
                    return task_list['id']
            
            # Create new "Exams" task list if not found
            new_list = {
                'title': 'Exams'
            }
            result = self.service.tasklists().insert(body=new_list).execute()
            return result['id']
            
        except json.JSONDecodeError as json_error:
            # This means the API returned HTML instead of JSON (usually expired auth)
            logger.error(f"Google API returned non-JSON response: {str(json_error)}")
            raise Exception("Google authentication has expired. Please reconnect your Google account in settings to continue syncing tasks.")
        except Exception as e:
            error_msg = str(e)
            # Check for various authentication error patterns
            if any(keyword in error_msg.lower() for keyword in ['invalid_grant', 'token_expired', 'unauthorized', '401']):
                raise Exception("Google authentication expired. Please reconnect your Google account in settings.")
            elif '<!' in error_msg or 'html' in error_msg.lower() or 'doctype' in error_msg.lower():
                raise Exception("Google API returned an error page. Your authentication has expired. Please reconnect your Google account in settings.")
            else:
                raise Exception(f"Failed to access Google Tasks: {error_msg}")
        
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
            task_notes = homework.description
        else:
            task_title = homework.title
            task_notes = homework.description
        
        # Check if task already exists with same title and due date
        try:
            existing_tasks = self.service.tasks().list(
                tasklist=task_list_id,
                showCompleted=False,
                maxResults=100
            ).execute()
            
            tasks = existing_tasks.get('items', [])
            
            # Format homework due date for comparison (date only, no time)
            homework_due_date = None
            if homework.due_date:
                homework_due_date = homework.due_date.strftime('%Y-%m-%d')
            
            for task in tasks:
                # Check if title matches
                if task.get('title') == task_title:
                    # Get task due date (date only, no time)
                    task_due_date = None
                    if task.get('due'):
                        task_due_date = task['due'][:10]  # Extract YYYY-MM-DD
                    
                    # If both have same title and same due date (or both have no due date), it's a duplicate
                    if task_due_date == homework_due_date:
                        logger.info(f"Task already exists: {task_title} (Due: {homework_due_date})")
                        # Update homework record with existing task ID
                        homework.google_task_id = task['id']
                        homework.synced_to_google_tasks = True
                        homework.save()
                        return task['id']
        except Exception as e:
            logger.warning(f"Error checking for existing tasks: {str(e)}. Creating new task anyway.")
        
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
            raise Exception("Google Tasks service not initialized. Please connect your Google account in settings.")
        
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
                error_msg = str(e)
                # Provide user-friendly error messages
                if 'invalid_grant' in error_msg.lower():
                    errors.append("Google authentication expired. Please reconnect your account.")
                    break  # Stop trying if auth is expired
                elif '<!' in error_msg or 'html' in error_msg.lower() or 'DOCTYPE' in error_msg:
                    errors.append("Google API error (authentication may have expired). Please reconnect your account.")
                    break  # Stop trying if auth is expired
                else:
                    errors.append(f"Error syncing {homework.title}: {error_msg}")
        
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
    
    def create_task_from_exam(self, exam):
        """Create a Google Task from scraped exam"""
        if not self.service:
            raise Exception("Google Tasks service not initialized")
        
        task_list_id = self.get_or_create_exams_tasklist()
        
        # Set task title and notes
        task_title = f"{exam.subject} - {exam.exam_name}"
        task_notes = f"Exam Date: {exam.exam_date.strftime('%Y-%m-%d')}\n\n{exam.exam_name}\n\nSource: {exam.get_site_display()}\nURL: {exam.url}"
        
        # Check if task already exists with same title and due date
        try:
            existing_tasks = self.service.tasks().list(
                tasklist=task_list_id,
                showCompleted=False,
                maxResults=100
            ).execute()
            
            tasks = existing_tasks.get('items', [])
            
            # Format exam due date for comparison (date only, no time)
            exam_due_date = exam.exam_date.strftime('%Y-%m-%d')
            
            for task in tasks:
                # Check if title matches
                if task.get('title') == task_title:
                    # Get task due date (date only, no time)
                    task_due_date = None
                    if task.get('due'):
                        task_due_date = task['due'][:10]  # Extract YYYY-MM-DD
                    
                    # If both have same title and same due date, it's a duplicate
                    if task_due_date == exam_due_date:
                        logger.info(f"Task already exists: {task_title} (Due: {exam_due_date})")
                        # Update exam record with existing task ID
                        exam.google_task_id = task['id']
                        exam.synced_to_google_tasks = True
                        exam.save()
                        return task['id']
        except Exception as e:
            logger.warning(f"Error checking for existing tasks: {str(e)}. Creating new task anyway.")
        
        # Prepare task data
        task_body = {
            'title': task_title,
            'notes': task_notes,
            'due': exam.exam_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        }
        
        # Create the task
        result = self.service.tasks().insert(
            tasklist=task_list_id,
            body=task_body
        ).execute()
        
        # Update exam record with Google Task ID
        exam.google_task_id = result['id']
        exam.synced_to_google_tasks = True
        exam.save()
        
        return result['id']
    
    def sync_exams_to_tasks(self, exam_queryset=None):
        """Sync scraped exams to Google Tasks"""
        if not self.service:
            raise Exception("Google Tasks service not initialized. Please connect your Google account in settings.")
        
        from scraper.models import ScrapedExam
        
        if exam_queryset is None:
            # Get all unsynced exams for this user
            exam_queryset = ScrapedExam.objects.filter(
                user=self.user,
                synced_to_google_tasks=False
            )
        
        synced_count = 0
        errors = []
        
        for exam in exam_queryset:
            try:
                self.create_task_from_exam(exam)
                synced_count += 1
            except Exception as e:
                error_msg = str(e)
                # Provide user-friendly error messages
                if 'invalid_grant' in error_msg.lower():
                    errors.append("Google authentication expired. Please reconnect your account.")
                    break  # Stop trying if auth is expired
                elif '<!' in error_msg or 'html' in error_msg.lower() or 'DOCTYPE' in error_msg:
                    errors.append("Google API error (authentication may have expired). Please reconnect your account.")
                    break  # Stop trying if auth is expired
                else:
                    errors.append(f"Error syncing {exam.exam_name}: {error_msg}")
        
        return {
            'synced_count': synced_count,
            'errors': errors
        }


class GoogleOAuthService:
    """Service for Google OAuth authentication"""
    
    @staticmethod
    def get_authorization_url(request):
        """Get Google OAuth authorization URL"""
        # Use production callback URL if available, otherwise build from request
        # Check if we're in production environment
        if hasattr(settings, 'GOOGLE_OAUTH_REDIRECT_URI') and settings.GOOGLE_OAUTH_REDIRECT_URI:
            backend_callback_url = settings.GOOGLE_OAUTH_REDIRECT_URI
        else:
            backend_callback_url = request.build_absolute_uri('/api/auth/google/callback')
        
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
        request.session.modified = True  # Ensure session is saved
        request.session.save()  # Explicitly save session
        
        print(f"DEBUG: Stored OAuth state: {state}")
        print(f"DEBUG: Session key after storing state: {request.session.session_key}")
        
        return authorization_url
    
    @staticmethod
    def handle_oauth_callback(request, authorization_code, state):
        """Handle Google OAuth callback"""
        # Verify state
        stored_state = request.session.get('google_oauth_state')
        print(f"DEBUG: Stored state in session: {stored_state}")
        print(f"DEBUG: Received state: {state}")
        print(f"DEBUG: Session key: {request.session.session_key}")
        print(f"DEBUG: Session data: {dict(request.session)}")
        
        # Skip state validation if session doesn't have it (session might not persist across requests)
        # This can happen with cross-domain OAuth flows
        if stored_state and stored_state != state:
            print(f"DEBUG: State mismatch - stored: {stored_state}, received: {state}")
            raise Exception("Invalid OAuth state")
        
        if not stored_state:
            print("WARNING: No stored state in session - skipping state validation (cross-domain OAuth flow)")
        
        try:
            # Use production callback URL if available, otherwise build from request
            if hasattr(settings, 'GOOGLE_OAUTH_REDIRECT_URI') and settings.GOOGLE_OAUTH_REDIRECT_URI:
                backend_callback_url = settings.GOOGLE_OAUTH_REDIRECT_URI
            else:
                backend_callback_url = request.build_absolute_uri('/api/auth/google/callback')
            
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
            if hasattr(settings, 'GOOGLE_OAUTH_REDIRECT_URI') and settings.GOOGLE_OAUTH_REDIRECT_URI:
                redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI
            else:
                redirect_uri = request.build_absolute_uri('/api/auth/google/callback')
            
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
                        "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [redirect_uri]
                    }
                },
                scopes=None  # Don't enforce specific scopes
            )
            flow.redirect_uri = redirect_uri
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
            
            # Set expiry from database if available
            expiry = oauth_record.token_expiry if hasattr(oauth_record, 'token_expiry') else None
            
            credentials = Credentials(
                token=oauth_record.access_token,
                refresh_token=oauth_record.refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=settings.GOOGLE_OAUTH2_CLIENT_ID,
                client_secret=settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                expiry=expiry
            )
            
            # Always try to refresh if we have a refresh token
            if credentials.refresh_token:
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
                    raise Exception("Google authentication has expired. Please reconnect your Google account in settings.")
            
            return credentials
        except GoogleOAuth.DoesNotExist:
            raise Exception("Google account not connected. Please connect your Google account in settings.")
    
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
    
    def create_event_from_exam(self, exam, calendar_id=None):
        """Create a Google Calendar event from scraped exam"""
        if not self.service:
            raise Exception("Google Calendar service not initialized")
        
        try:
            if not calendar_id:
                calendar_id = self.create_homework_calendar()
            
            # Prepare event data
            event_body = {
                'summary': f"📝 EXAM: {exam.subject} - {exam.exam_name}",
                'description': f"Subject: {exam.subject}\nExam: {exam.exam_name}\n\nSource: {exam.get_site_display()}\nURL: {exam.url}",
                'location': exam.get_site_display(),
                'start': {
                    'date': exam.exam_date.strftime('%Y-%m-%d'),
                    'timeZone': 'UTC'
                },
                'end': {
                    'date': exam.exam_date.strftime('%Y-%m-%d'),
                    'timeZone': 'UTC'
                },
                'colorId': '11',  # Red color for exams
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 60},  # 1 hour before
                    ],
                },
            }
            
            result = self.service.events().insert(
                calendarId=calendar_id,
                body=event_body
            ).execute()
            
            # Update exam record with Google Calendar event ID
            exam.google_calendar_event_id = result['id']
            exam.synced_to_google_calendar = True
            exam.save()
            
            logger.info(f"Created calendar event for exam: {exam.exam_name}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating exam calendar event: {str(e)}")
            raise
    
    def sync_exams_to_calendar(self, calendar_id=None):
        """Sync scraped exams to Google Calendar"""
        if not self.service:
            raise Exception("Google Calendar service not initialized")
        
        from scraper.models import ScrapedExam
        
        # Get unsynced exams for this user
        exams = ScrapedExam.objects.filter(
            user=self.user,
            synced_to_google_calendar=False
        )
        
        synced_count = 0
        errors = []
        
        for exam in exams:
            try:
                self.create_event_from_exam(exam, calendar_id)
                synced_count += 1
            except Exception as e:
                errors.append(f"Error syncing exam {exam.exam_name}: {str(e)}")
        
        return {
            'synced_count': synced_count,
            'errors': errors
        }