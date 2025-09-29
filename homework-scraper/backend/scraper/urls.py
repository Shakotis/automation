from django.urls import path
from . import views

urlpatterns = [
    path('homework/', views.HomeworkListView.as_view(), name='homework-list'),
    path('homework/scrape/', views.ScrapeHomeworkView.as_view(), name='scrape-homework'),
    path('preferences/', views.UserPreferencesView.as_view(), name='user-preferences'),
]