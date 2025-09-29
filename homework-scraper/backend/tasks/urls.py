from django.urls import path
from . import views

urlpatterns = [
    path('sync/', views.SyncToGoogleTasksView.as_view(), name='sync-tasks'),
    path('lists/', views.TaskListsView.as_view(), name='task-lists'),
    path('lists/<str:list_id>/tasks/', views.TasksView.as_view(), name='tasks'),
]