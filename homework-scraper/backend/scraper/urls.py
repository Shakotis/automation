from django.urls import path
from . import views

urlpatterns = [
    # Homework endpoints
    path('homework', views.HomeworkListView.as_view(), name='homework-list'),
    path('homework/scrape', views.ScrapeHomeworkView.as_view(), name='scrape-homework'),
    path('homework/sync-google-tasks', views.SyncToGoogleTasksView.as_view(), name='sync-google-tasks'),
    path('homework/<int:homework_id>/complete', views.HomeworkCompleteView.as_view(), name='homework-complete'),
    
    # Exam endpoints
    path('exams', views.ExamListView.as_view(), name='exam-list'),
    path('exams/scrape', views.ScrapeExamsView.as_view(), name='scrape-exams'),
    path('exams/sync-calendar', views.SyncExamsToCalendarView.as_view(), name='sync-exams-calendar'),
    
    # General endpoints
    path('stats', views.DashboardStatsView.as_view(), name='dashboard-stats'),
    path('preferences', views.UserPreferencesView.as_view(), name='user-preferences'),
]