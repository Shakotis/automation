from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from scraper.models import ScrapedHomework
from .services import GoogleTasksService, GoogleCalendarService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SyncToGoogleTasksView(APIView):
    """Sync homework to Google Tasks"""
    
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            tasks_service = GoogleTasksService(request.user)
            
            # Get homework IDs to sync (optional)
            homework_ids = request.data.get('homework_ids', [])
            
            if homework_ids:
                homework_qs = ScrapedHomework.objects.filter(
                    user=request.user,
                    id__in=homework_ids,
                    synced_to_google_tasks=False
                )
            else:
                homework_qs = None  # Sync all unsynced
            
            result = tasks_service.sync_homework_to_tasks(homework_qs)
            
            return Response({
                'message': 'Sync completed',
                'synced_count': result['synced_count'],
                'errors': result['errors']
            })
            
        except Exception as e:
            return Response({
                'error': f'Sync failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TaskListsView(APIView):
    """Get Google Task Lists"""
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            tasks_service = GoogleTasksService(request.user)
            task_lists = tasks_service.get_task_lists()
            
            return Response({
                'task_lists': task_lists
            })
            
        except Exception as e:
            return Response({
                'error': f'Failed to get task lists: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TasksView(APIView):
    """Get tasks from a specific task list"""
    
    def get(self, request, list_id):
        if not request.user.is_authenticated:
            return Response({
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            tasks_service = GoogleTasksService(request.user)
            tasks = tasks_service.get_tasks(list_id)
            
            return Response({
                'tasks': tasks
            })
            
        except Exception as e:
            return Response({
                'error': f'Failed to get tasks: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SyncToGoogleCalendarView(APIView):
    """Sync homework to Google Calendar"""
    
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            calendar_service = GoogleCalendarService(request.user)
            
            # Get homework IDs to sync (optional)
            homework_ids = request.data.get('homework_ids', [])
            calendar_id = request.data.get('calendar_id')  # Optional specific calendar
            
            if homework_ids:
                homework_qs = ScrapedHomework.objects.filter(
                    user=request.user,
                    id__in=homework_ids,
                    synced_to_google_calendar=False
                )
            else:
                homework_qs = None  # Sync all unsynced
            
            result = calendar_service.sync_homework_to_calendar(homework_qs, calendar_id)
            
            return Response({
                'message': 'Calendar sync completed',
                'synced_count': result['synced_count'],
                'errors': result['errors']
            })
            
        except Exception as e:
            logger.error(f"Calendar sync error: {str(e)}")
            return Response({
                'error': f'Calendar sync failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GoogleCalendarsView(APIView):
    """Get user's Google Calendars"""
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            calendar_service = GoogleCalendarService(request.user)
            calendars = calendar_service.get_calendars()
            
            return Response({
                'calendars': calendars
            })
            
        except Exception as e:
            logger.error(f"Error getting calendars: {str(e)}")
            return Response({
                'error': f'Failed to get calendars: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CreateExamEventView(APIView):
    """Create exam events in Google Calendar"""
    
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        title = request.data.get('title')
        date_str = request.data.get('date')
        description = request.data.get('description')
        calendar_id = request.data.get('calendar_id')
        
        if not title or not date_str:
            return Response({
                'error': 'Title and date are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Parse the date
            exam_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            calendar_service = GoogleCalendarService(request.user)
            event_id = calendar_service.create_exam_event(
                title, exam_date, description, calendar_id
            )
            
            return Response({
                'message': 'Exam event created successfully',
                'event_id': event_id,
                'title': title,
                'date': date_str
            })
            
        except ValueError:
            return Response({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating exam event: {str(e)}")
            return Response({
                'error': f'Failed to create exam event: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserIntegrationPreferencesView(APIView):
    """Handle user preferences for Google Tasks vs Calendar"""
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            from authentication.supabase_service import SupabaseService
            
            supabase_service = SupabaseService()
            user_profile = supabase_service.get_user_profile(request.user.id)
            
            preferences = user_profile.get('preferences', {}) if user_profile else {}
            
            return Response({
                'preferences': {
                    'homework_sync_target': preferences.get('homework_sync_target', 'tasks'),  # 'tasks' or 'calendar'
                    'exam_sync_target': preferences.get('exam_sync_target', 'calendar'),  # 'tasks' or 'calendar'
                    'auto_sync_enabled': preferences.get('auto_sync_enabled', True),
                    'calendar_id': preferences.get('preferred_calendar_id'),
                }
            })
            
        except Exception as e:
            logger.error(f"Error getting integration preferences: {str(e)}")
            return Response({
                'error': f'Failed to get preferences: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Update user integration preferences"""
        if not request.user.is_authenticated:
            return Response({
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            from authentication.supabase_service import SupabaseService
            
            new_preferences = request.data
            
            # Validate preferences
            valid_targets = ['tasks', 'calendar']
            if new_preferences.get('homework_sync_target') not in valid_targets:
                return Response({
                    'error': 'Invalid homework_sync_target. Must be "tasks" or "calendar"'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if new_preferences.get('exam_sync_target') not in valid_targets:
                return Response({
                    'error': 'Invalid exam_sync_target. Must be "tasks" or "calendar"'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            supabase_service = SupabaseService()
            
            # Get existing preferences
            user_profile = supabase_service.get_user_profile(request.user.id)
            existing_preferences = user_profile.get('preferences', {}) if user_profile else {}
            
            # Update with new preferences
            existing_preferences.update(new_preferences)
            
            # Save to Supabase
            supabase_service.update_user_preferences(request.user.id, existing_preferences)
            
            return Response({
                'message': 'Integration preferences updated successfully',
                'preferences': existing_preferences
            })
            
        except Exception as e:
            logger.error(f"Error updating integration preferences: {str(e)}")
            return Response({
                'error': f'Failed to update preferences: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
