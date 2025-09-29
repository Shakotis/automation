from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from scraper.models import ScrapedHomework
from .services import GoogleTasksService

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
