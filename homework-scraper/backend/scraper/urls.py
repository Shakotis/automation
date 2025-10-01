from django.urls import path
from . import views

urlpatterns = [
    path('homework/', views.HomeworkListView.as_view(), name='homework-list'),
    path('homework/scrape/', views.ScrapeHomeworkView.as_view(), name='scrape-homework'),
    path('homework/sync-google-tasks/', views.SyncToGoogleTasksView.as_view(), name='sync-google-tasks'),
    path('homework/<int:homework_id>/complete/', views.HomeworkCompleteView.as_view(), name='homework-complete'),
    path('stats/', views.DashboardStatsView.as_view(), name='dashboard-stats'),
    path('preferences/', views.UserPreferencesView.as_view(), name='user-preferences'),
]