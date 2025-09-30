from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import ScrapedHomework, UserScrapingPreferences
from .scrapers import HomeworkScrapingService
from tasks.services import GoogleTasksService
import json

class HomeworkPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class HomeworkListView(APIView):
    """List scraped homework for the authenticated user"""
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        homework_qs = ScrapedHomework.objects.filter(user=request.user)
        
        # Filter by site if requested
        site = request.GET.get('site')
        if site:
            homework_qs = homework_qs.filter(site=site)
        
        # Filter by sync status
        synced = request.GET.get('synced')
        if synced is not None:
            synced_bool = synced.lower() == 'true'
            homework_qs = homework_qs.filter(synced_to_google_tasks=synced_bool)
        
        # Paginate results
        paginator = HomeworkPagination()
        page = paginator.paginate_queryset(homework_qs, request)
        
        homework_data = []
        for hw in page:
            homework_data.append({
                'id': hw.id,
                'title': hw.title,
                'description': hw.description,
                'due_date': hw.due_date.isoformat() if hw.due_date else None,
                'subject': hw.subject,
                'site': hw.site,
                'url': hw.url,
                'scraped_at': hw.scraped_at.isoformat(),
                'synced_to_google_tasks': hw.synced_to_google_tasks,
                'google_task_id': hw.google_task_id,
            })
        
        return paginator.get_paginated_response(homework_data)

@method_decorator(csrf_exempt, name='dispatch')
class ScrapeHomeworkView(APIView):
    """Manually trigger homework scraping"""
    
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            # Initialize scraping service
            scraping_service = HomeworkScrapingService(request.user)
            
            # Scrape homework
            homework_list = scraping_service.scrape_all_sites()
            
            # Auto-sync to Google Tasks if enabled
            preferences = scraping_service.preferences
            if preferences.auto_sync_to_google_tasks:
                try:
                    tasks_service = GoogleTasksService(request.user)
                    sync_result = tasks_service.sync_homework_to_tasks()
                    
                    return Response({
                        'message': 'Homework scraped and synced successfully',
                        'scraped_count': len(homework_list),
                        'synced_count': sync_result['synced_count'],
                        'sync_errors': sync_result['errors']
                    })
                except Exception as sync_error:
                    return Response({
                        'message': 'Homework scraped but sync failed',
                        'scraped_count': len(homework_list),
                        'sync_error': str(sync_error)
                    })
            
            return Response({
                'message': 'Homework scraped successfully',
                'scraped_count': len(homework_list)
            })
            
        except Exception as e:
            return Response({
                'error': f'Scraping failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserPreferencesView(APIView):
    """Manage user scraping preferences"""
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        preferences, created = UserScrapingPreferences.objects.get_or_create(
            user=request.user
        )
        
        return Response({
            'enable_manodienynas': preferences.enable_manodienynas,
            'enable_eduka': preferences.enable_eduka,
            'auto_sync_to_google_tasks': preferences.auto_sync_to_google_tasks,
            'scraping_frequency_hours': preferences.scraping_frequency_hours,
            'last_scraped_manodienynas': preferences.last_scraped_manodienynas.isoformat() if preferences.last_scraped_manodienynas else None,
            'last_scraped_eduka': preferences.last_scraped_eduka.isoformat() if preferences.last_scraped_eduka else None,
        })
    
    def put(self, request):
        if not request.user.is_authenticated:
            return Response({
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        preferences, created = UserScrapingPreferences.objects.get_or_create(
            user=request.user
        )
        
        # Update preferences
        if 'enable_manodienynas' in request.data:
            preferences.enable_manodienynas = request.data['enable_manodienynas']
        
        if 'enable_eduka' in request.data:
            preferences.enable_eduka = request.data['enable_eduka']
        
        if 'auto_sync_to_google_tasks' in request.data:
            preferences.auto_sync_to_google_tasks = request.data['auto_sync_to_google_tasks']
        
        if 'scraping_frequency_hours' in request.data:
            preferences.scraping_frequency_hours = request.data['scraping_frequency_hours']
        
        preferences.save()
        
        return Response({
            'message': 'Preferences updated successfully',
            'enable_manodienynas': preferences.enable_manodienynas,
            'enable_eduka': preferences.enable_eduka,
            'auto_sync_to_google_tasks': preferences.auto_sync_to_google_tasks,
            'scraping_frequency_hours': preferences.scraping_frequency_hours,
        })

class SyncToGoogleTasksView(APIView):
    """Manually sync homework to Google Tasks"""
    
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            # Initialize Google Tasks service
            tasks_service = GoogleTasksService(request.user)
            
            # Check if user has valid OAuth credentials
            if not tasks_service.credentials:
                return Response({
                    'error': 'No Google OAuth credentials found. Please authenticate with Google first.',
                    'action': 'Please go to Settings and connect your Google account.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get unsynced homework
            unsynced_homework = ScrapedHomework.objects.filter(
                user=request.user,
                synced_to_google_tasks=False
            )
            
            if not unsynced_homework:
                return Response({
                    'message': 'No homework to sync. All homework is already synced.',
                    'synced_count': 0
                })
            
            # Sync to Google Tasks
            sync_result = tasks_service.sync_homework_to_tasks(unsynced_homework)
            
            return Response({
                'message': f'Successfully synced {sync_result["synced_count"]} homework items to Google Tasks',
                'synced_count': sync_result['synced_count'],
                'errors': sync_result['errors']
            })
            
        except Exception as e:
            return Response({
                'error': f'Sync failed: {str(e)}',
                'details': 'Please check your Google account connection and try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
