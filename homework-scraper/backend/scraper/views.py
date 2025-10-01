from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import ScrapedHomework, UserScrapingPreferences
from .scrapers import HomeworkScrapingService
from tasks.services import GoogleTasksService
import json
import logging

logger = logging.getLogger(__name__)

class HomeworkPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class HomeworkListView(APIView):
    """List scraped homework for the authenticated user"""
    permission_classes = [AllowAny]  # Allow unauthenticated access
    
    def get(self, request):
        # Return empty list if not authenticated
        if not request.user.is_authenticated:
            return Response({
                'results': [],
                'count': 0,
                'next': None,
                'previous': None,
            })
        
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
        
        # Filter by completion status
        completed = request.GET.get('completed')
        if completed is not None:
            completed_bool = completed.lower() == 'true'
            homework_qs = homework_qs.filter(completed=completed_bool)
        
        # Filter by status (upcoming, overdue, completed)
        filter_status = request.GET.get('status')
        if filter_status == 'upcoming':
            homework_qs = homework_qs.filter(
                completed=False,
                due_date__gte=timezone.now()
            )
        elif filter_status == 'overdue':
            homework_qs = homework_qs.filter(
                completed=False,
                due_date__lt=timezone.now()
            )
        elif filter_status == 'completed':
            homework_qs = homework_qs.filter(completed=True)
        
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
                'completed': hw.completed,
                'completed_at': hw.completed_at.isoformat() if hw.completed_at else None,
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
            'google_tasks_title_format': preferences.google_tasks_title_format,
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
        
        if 'google_tasks_title_format' in request.data:
            preferences.google_tasks_title_format = request.data['google_tasks_title_format']
        
        preferences.save()
        
        return Response({
            'message': 'Preferences updated successfully',
            'enable_manodienynas': preferences.enable_manodienynas,
            'enable_eduka': preferences.enable_eduka,
            'auto_sync_to_google_tasks': preferences.auto_sync_to_google_tasks,
            'scraping_frequency_hours': preferences.scraping_frequency_hours,
            'google_tasks_title_format': preferences.google_tasks_title_format,
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

class HomeworkCompleteView(APIView):
    """Mark homework as complete or incomplete"""
    
    def post(self, request, homework_id):
        if not request.user.is_authenticated:
            return Response({
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            homework = ScrapedHomework.objects.get(id=homework_id, user=request.user)
            completed = request.data.get('completed', True)
            
            homework.completed = completed
            if completed:
                homework.completed_at = timezone.now()
            else:
                homework.completed_at = None
            homework.save()
            
            # If synced to Google Tasks, update there too
            if homework.synced_to_google_tasks and homework.google_task_id:
                try:
                    tasks_service = GoogleTasksService(request.user)
                    if tasks_service.service:
                        task_list_id = tasks_service.get_or_create_homework_tasklist()
                        task_body = {'status': 'completed' if completed else 'needsAction'}
                        tasks_service.service.tasks().patch(
                            tasklist=task_list_id,
                            task=homework.google_task_id,
                            body=task_body
                        ).execute()
                except Exception as e:
                    logger.warning(f"Failed to update Google Task status: {str(e)}")
            
            return Response({
                'message': 'Homework status updated',
                'completed': homework.completed,
                'completed_at': homework.completed_at.isoformat() if homework.completed_at else None
            })
            
        except ScrapedHomework.DoesNotExist:
            return Response({
                'error': 'Homework not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Failed to update homework: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DashboardStatsView(APIView):
    """Get dashboard statistics"""
    permission_classes = [AllowAny]  # Allow unauthenticated access
    
    def get(self, request):
        # Return empty stats if not authenticated
        if not request.user.is_authenticated:
            return Response({
                'total_homework': 0,
                'synced_homework': 0,
                'completed_homework': 0,
                'pending_homework': 0,
                'overdue_homework': 0,
                'sites_enabled': [],
                'last_scrape': None,
            })
        
        try:
            preferences = UserScrapingPreferences.objects.get(user=request.user)
            total_homework = ScrapedHomework.objects.filter(user=request.user).count()
            synced_homework = ScrapedHomework.objects.filter(
                user=request.user,
                synced_to_google_tasks=True
            ).count()
            completed_homework = ScrapedHomework.objects.filter(
                user=request.user,
                completed=True
            ).count()
            pending_homework = ScrapedHomework.objects.filter(
                user=request.user,
                completed=False
            ).count()
            overdue_homework = ScrapedHomework.objects.filter(
                user=request.user,
                completed=False,
                due_date__lt=timezone.now()
            ).count()
            
            sites_enabled = []
            if preferences.enable_manodienynas:
                sites_enabled.append('manodienynas')
            if preferences.enable_eduka:
                sites_enabled.append('eduka')
            
            last_scrape = None
            if preferences.last_scraped_manodienynas or preferences.last_scraped_eduka:
                dates = [d for d in [preferences.last_scraped_manodienynas, preferences.last_scraped_eduka] if d]
                if dates:
                    last_scrape = max(dates).isoformat()
            
            return Response({
                'total_homework': total_homework,
                'synced_homework': synced_homework,
                'completed_homework': completed_homework,
                'pending_homework': pending_homework,
                'overdue_homework': overdue_homework,
                'sites_enabled': sites_enabled,
                'last_scrape': last_scrape,
            })
            
        except UserScrapingPreferences.DoesNotExist:
            return Response({
                'total_homework': 0,
                'synced_homework': 0,
                'completed_homework': 0,
                'pending_homework': 0,
                'overdue_homework': 0,
                'sites_enabled': [],
                'last_scrape': None,
            })
        except Exception as e:
            return Response({
                'error': f'Failed to fetch stats: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
