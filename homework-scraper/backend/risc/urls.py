from django.urls import path
from . import views

urlpatterns = [
    path('receiver/', views.risc_receiver, name='risc-receiver'),
    path('status/', views.risc_status, name='risc-status'),
]
