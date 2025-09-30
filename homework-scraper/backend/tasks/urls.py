from django.urls import path
from . import views

urlpatterns = [
    # Google Tasks endpoints
    path('sync/', views.SyncToGoogleTasksView.as_view(), name='sync-tasks'),
    path('lists/', views.TaskListsView.as_view(), name='task-lists'),
    path('lists/<str:list_id>/tasks/', views.TasksView.as_view(), name='tasks'),
    
    # Google Calendar endpoints
    path('calendar/sync/', views.SyncToGoogleCalendarView.as_view(), name='sync-calendar'),
    path('calendar/calendars/', views.GoogleCalendarsView.as_view(), name='google-calendars'),
    path('calendar/exam/', views.CreateExamEventView.as_view(), name='create-exam-event'),
    
    # Integration preferences
    path('preferences/', views.UserIntegrationPreferencesView.as_view(), name='integration-preferences'),
]