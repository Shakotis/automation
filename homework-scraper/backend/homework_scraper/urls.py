"""
URL configuration for homework_scraper project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from . import test_views
from authentication.views import CSRFTokenView

def health_check(request):
    """Health check endpoint for monitoring and load balancers"""
    return JsonResponse({
        'status': 'ok',
        'service': 'homework-scraper-backend',
        'version': '1.0.0'
    })

urlpatterns = [
    path('', health_check, name='root-health'),
    path('api/health', health_check, name='api-health'),
    path('health', health_check, name='health'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/scraper/', include('scraper.urls')),
    path('api/tasks/', include('tasks.urls')),
    path('api/test/', test_views.api_test, name='api-test'),
    path('csrf-token/', CSRFTokenView.as_view(), name='csrf-token'),
]
