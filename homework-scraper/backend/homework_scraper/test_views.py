from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

@csrf_exempt
def api_test(request):
    """Simple API test endpoint"""
    return JsonResponse({
        'status': 'success',
        'message': 'Backend API is working!',
        'django_running': True,
        'google_oauth_configured': bool(getattr(settings, 'GOOGLE_OAUTH2_CLIENT_ID', '')),
    })