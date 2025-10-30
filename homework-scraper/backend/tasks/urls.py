"""
URL configuration for Google Tasks integration
"""
from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Sync homework to Google Tasks
    path('sync', views.sync_homework_to_tasks, name='sync-homework-to-tasks'),
    path('sync/', views.sync_homework_to_tasks, name='sync-homework-to-tasks-slash'),
    
    # Get Google Task lists
    path('lists', views.get_task_lists, name='get-task-lists'),
    path('lists/', views.get_task_lists, name='get-task-lists-slash'),
    
    # Get tasks from a specific list
    path('lists/<str:list_id>/tasks', views.get_tasks, name='get-tasks'),
    path('lists/<str:list_id>/tasks/', views.get_tasks, name='get-tasks-slash'),
]
