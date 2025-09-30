"""
Custom middleware to disable CSRF protection for API endpoints
"""

class DisableCSRFForAPIMiddleware:
    """
    Middleware to disable CSRF protection for API endpoints.
    This is safe for API endpoints that use session authentication
    with proper CORS settings.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Disable CSRF for API endpoints
        print(f"DEBUG: Request path: {request.path}")
        if request.path.startswith('/api/'):
            print(f"DEBUG: Disabling CSRF for API path: {request.path}")
            setattr(request, '_dont_enforce_csrf_checks', True)
        
        response = self.get_response(request)
        return response