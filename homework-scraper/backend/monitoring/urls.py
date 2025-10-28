"""
URL configuration for monitoring app
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.monitoring_info, name='monitoring-info'),
    path('system-status/', views.get_system_status, name='system-status'),
    path('services/', views.get_running_services, name='running-services'),
    path('logs/', views.get_application_logs, name='application-logs'),
    path('errors/', views.get_recent_errors, name='recent-errors'),
    path('processes/', views.get_process_info, name='process-info'),
]
