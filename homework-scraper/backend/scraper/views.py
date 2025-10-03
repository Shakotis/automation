from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import ScrapedHomework, ScrapedExam, UserScrapingPreferences
# Use simple scrapers without Selenium for server deployment
from .scrapers_simple import HomeworkScrapingService
from tasks.services import GoogleTasksService, GoogleCalendarService
import json
import logging

logger = logging.getLogger(__name__)

class HomeworkPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class HomeworkListView(APIView):
    """List scraped homework for the authenticated user"""
    authentication_classes = [SessionAuthentication]
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
        
        # Check if requesting deleted items
        show_deleted = request.GET.get('deleted', 'false').lower() == 'true'
        
        if show_deleted:
            homework_qs = ScrapedHomework.objects.filter(user=request.user, deleted=True)
        else:
            homework_qs = ScrapedHomework.objects.filter(user=request.user, deleted=False)
        
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
                'deleted': hw.deleted,
                'deleted_at': hw.deleted_at.isoformat() if hw.deleted_at else None,
            })
        
        return paginator.get_paginated_response(homework_data)

@method_decorator(csrf_exempt, name='dispatch')
class ScrapeHomeworkView(APIView):
    """Manually trigger homework scraping"""
    authentication_classes = [SessionAuthentication]
    permission_classes = []  # We'll check authentication manually
    
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
            
            # Also scrape exams
            exam_count = 0
            try:
                from .manodienynas_exams import scrape_manodienynas_exams
                exams = scrape_manodienynas_exams(request.user)
                exam_count = len(exams)
            except Exception as exam_error:
                logger.warning(f"Failed to scrape exams: {str(exam_error)}")
            
            # Auto-sync to Google Tasks if enabled
            preferences = scraping_service.preferences
            if preferences.auto_sync_to_google_tasks:
                try:
                    tasks_service = GoogleTasksService(request.user)
                    sync_result = tasks_service.sync_homework_to_tasks()
                    
                    # Also sync exams
                    exam_sync_count = 0
                    try:
                        exam_sync_result = tasks_service.sync_exams_to_tasks()
                        exam_sync_count = exam_sync_result.get('synced_count', 0)
                    except Exception as exam_sync_error:
                        logger.warning(f"Failed to sync exams: {str(exam_sync_error)}")
                    
                    return Response({
                        'message': 'Homework and exams scraped and synced successfully',
                        'homework_scraped': len(homework_list),
                        'exams_scraped': exam_count,
                        'homework_synced': sync_result['synced_count'],
                        'exams_synced': exam_sync_count,
                        'sync_errors': sync_result['errors']
                    })
                except Exception as sync_error:
                    return Response({
                        'message': 'Scraped but sync failed',
                        'homework_scraped': len(homework_list),
                        'exams_scraped': exam_count,
                        'sync_error': str(sync_error)
                    })
            
            return Response({
                'message': 'Homework and exams scraped successfully',
                'homework_scraped': len(homework_list),
                'exams_scraped': exam_count
            })
            
        except Exception as e:
            return Response({
                'error': f'Scraping failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserPreferencesView(APIView):
    """Manage user scraping preferences"""
    authentication_classes = [SessionAuthentication]
    permission_classes = []
    
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
    authentication_classes = [SessionAuthentication]
    permission_classes = []
    
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
    authentication_classes = [SessionAuthentication]
    permission_classes = []
    
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
                # When unchecking a task, bring it back from deleted state
                homework.deleted = False
                homework.deleted_at = None
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
    authentication_classes = [SessionAuthentication]
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
            from datetime import timedelta
            
            # Auto-delete overdue and completed tasks
            now = timezone.now()
            
            # Mark overdue tasks as deleted
            overdue_tasks = ScrapedHomework.objects.filter(
                user=request.user,
                deleted=False,
                completed=False,
                due_date__lt=now
            )
            overdue_tasks.update(deleted=True, deleted_at=now)
            
            # Mark completed tasks as deleted
            completed_tasks = ScrapedHomework.objects.filter(
                user=request.user,
                deleted=False,
                completed=True
            )
            completed_tasks.update(deleted=True, deleted_at=now)
            
            preferences = UserScrapingPreferences.objects.get(user=request.user)
            
            # Calculate week boundaries (this week = next 7 days)
            week_start = now
            week_end = now + timedelta(days=7)
            
            # Total = tasks left to do this week (not deleted, not completed)
            # Include tasks with no deadline OR tasks due within this week
            from django.db.models import Q
            total_homework = ScrapedHomework.objects.filter(
                user=request.user,
                deleted=False,
                completed=False
            ).filter(
                Q(due_date__isnull=True) |  # No deadline
                Q(due_date__gte=week_start, due_date__lte=week_end)  # This week
            ).count()
            
            # Tomorrow's tasks for completion rate
            tomorrow = now + timedelta(days=1)
            tomorrow_start = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow_end = tomorrow_start + timedelta(days=1)
            
            tomorrow_total = ScrapedHomework.objects.filter(
                user=request.user,
                deleted=False,
                due_date__gte=tomorrow_start,
                due_date__lt=tomorrow_end
            ).count()
            
            tomorrow_completed = ScrapedHomework.objects.filter(
                user=request.user,
                deleted=False,
                completed=True,
                due_date__gte=tomorrow_start,
                due_date__lt=tomorrow_end
            ).count()
            
            synced_homework = 0  # Not used anymore
            completed_homework = tomorrow_completed
            pending_homework = ScrapedHomework.objects.filter(
                user=request.user,
                deleted=False,
                completed=False
            ).filter(
                Q(due_date__isnull=True) | Q(due_date__gte=week_start)
            ).count()
            overdue_homework = 0  # Not used anymore
            
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
                'total_homework': total_homework,  # This week's incomplete tasks
                'synced_homework': synced_homework,  # Deprecated
                'completed_homework': tomorrow_completed,  # Tomorrow's completed
                'pending_homework': pending_homework,  # All future incomplete
                'overdue_homework': overdue_homework,  # Deprecated
                'sites_enabled': sites_enabled,
                'last_scrape': last_scrape,
                'tomorrow_total': tomorrow_total,  # For completion rate calculation
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
                'tomorrow_total': 0,
            })
        except Exception as e:
            return Response({
                'error': f'Failed to fetch stats: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExamListView(APIView):
    """List scraped exams for the authenticated user"""
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({
                'results': [],
                'count': 0,
            })
        
        exams_qs = ScrapedExam.objects.filter(user=request.user)
        
        # Filter by site if requested
        site = request.GET.get('site')
        if site:
            exams_qs = exams_qs.filter(site=site)
        
        # Filter by upcoming/past
        filter_time = request.GET.get('time')
        if filter_time == 'upcoming':
            exams_qs = exams_qs.filter(exam_date__gte=timezone.now())
        elif filter_time == 'past':
            exams_qs = exams_qs.filter(exam_date__lt=timezone.now())
        
        exams_data = []
        for exam in exams_qs:
            exams_data.append({
                'id': exam.id,
                'exam_name': exam.exam_name,
                'subject': exam.subject,
                'exam_date': exam.exam_date.isoformat(),
                'site': exam.site,
                'url': exam.url,
                'scraped_at': exam.scraped_at.isoformat(),
                'synced_to_google_calendar': exam.synced_to_google_calendar,
                'google_calendar_event_id': exam.google_calendar_event_id,
            })
        
        return Response({
            'results': exams_data,
            'count': len(exams_data),
        })


@method_decorator(csrf_exempt, name='dispatch')
class ScrapeExamsView(APIView):
    """Manually trigger exam scraping"""
    authentication_classes = [SessionAuthentication]
    permission_classes = []
    
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            # Import the scraper
            from .manodienynas_exams import scrape_manodienynas_exams
            
            # Scrape exams
            exams = scrape_manodienynas_exams(request.user)
            
            # Auto-sync to Google Calendar
            try:
                calendar_service = GoogleCalendarService(request.user)
                if calendar_service.service:
                    sync_result = calendar_service.sync_exams_to_calendar()
                    
                    return Response({
                        'message': 'Exams scraped and synced successfully',
                        'scraped_count': len(exams),
                        'synced_count': sync_result['synced_count'],
                        'sync_errors': sync_result['errors']
                    })
                else:
                    return Response({
                        'message': 'Exams scraped but Google Calendar not connected',
                        'scraped_count': len(exams),
                        'sync_error': 'No Google Calendar credentials found'
                    })
            except Exception as sync_error:
                return Response({
                    'message': 'Exams scraped but sync failed',
                    'scraped_count': len(exams),
                    'sync_error': str(sync_error)
                })
            
        except Exception as e:
            logger.error(f"Exam scraping error: {str(e)}")
            return Response({
                'error': f'Exam scraping failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SyncExamsToCalendarView(APIView):
    """Manually sync exams to Google Calendar"""
    authentication_classes = [SessionAuthentication]
    permission_classes = []
    
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            calendar_service = GoogleCalendarService(request.user)
            
            if not calendar_service.service:
                return Response({
                    'error': 'No Google Calendar credentials found. Please authenticate with Google first.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get unsynced exams
            unsynced_exams = ScrapedExam.objects.filter(
                user=request.user,
                synced_to_google_calendar=False
            )
            
            if not unsynced_exams:
                return Response({
                    'message': 'No exams to sync. All exams are already synced.',
                    'synced_count': 0
                })
            
            # Sync to Google Calendar
            sync_result = calendar_service.sync_exams_to_calendar()
            
            return Response({
                'message': f'Successfully synced {sync_result["synced_count"]} exams to Google Calendar',
                'synced_count': sync_result['synced_count'],
                'errors': sync_result['errors']
            })
            
        except Exception as e:
            logger.error(f"Calendar sync error: {str(e)}")
            return Response({
                'error': f'Sync failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
