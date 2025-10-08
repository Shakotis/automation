from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from django.contrib.auth import login, logout, update_session_auth_hash
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from tasks.services import GoogleOAuthService
from .models import GoogleOAuth
from .supabase_service import SupabaseService
from .credential_storage import SecureCredentialStorage
from .verification_service import CredentialVerificationService
import json
import logging

logger = logging.getLogger(__name__)

class GoogleOAuthLoginView(APIView):
    """Initiate Google OAuth login"""
    authentication_classes = []  # Disable authentication
    permission_classes = []  # Allow unauthenticated access
    
    def get(self, request):
        try:
            authorization_url = GoogleOAuthService.get_authorization_url(request)
            return Response({
                'authorization_url': authorization_url
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class GoogleOAuthCallbackView(APIView):
    """Handle Google OAuth callback"""
    authentication_classes = []  # Disable authentication
    permission_classes = []  # Allow unauthenticated access
    
    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')
        return self._handle_oauth_callback(request, code, state)
    
    def post(self, request):
        code = request.data.get('code')
        state = request.data.get('state')
        return self._handle_oauth_callback(request, code, state)
    
    def _handle_oauth_callback(self, request, code, state):
        if not code:
            return Response({
                'error': 'Authorization code not provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            print(f"DEBUG: Starting OAuth callback with code: {code[:20]}... and state: {state}")
            user = GoogleOAuthService.handle_oauth_callback(request, code, state)
            print(f"DEBUG: OAuth callback got user: {user.email if user else None}")
            print(f"DEBUG: Session key before login: {request.session.session_key}")
            
            login(request, user)
            # Update session auth hash to ensure it matches current user state
            update_session_auth_hash(request, user)
            print(f"DEBUG: Session key after login: {request.session.session_key}")
            print(f"DEBUG: User authenticated after login: {request.user.is_authenticated}")
            print(f"DEBUG: Session data: {dict(request.session)}")
            print(f"DEBUG: Updated session auth hash")
            
            # Delete demo homework and duplicates for logged-in users
            try:
                from scraper.models import ScrapedHomework
                # Delete demo homework (homework with specific demo markers)
                demo_deleted = ScrapedHomework.objects.filter(
                    user=user,
                    title__icontains='demo'
                ).delete()
                logger.info(f"Deleted {demo_deleted[0]} demo homework items for user {user.email}")
                
                # Remove duplicate homework entries
                # Keep the most recent one for each unique (title, due_date, site) combination
                from django.db.models import Count, Min
                duplicates = ScrapedHomework.objects.filter(user=user).values(
                    'title', 'due_date', 'site'
                ).annotate(count=Count('id'), min_id=Min('id')).filter(count__gt=1)
                
                for dup in duplicates:
                    # Keep the first one, delete the rest
                    ScrapedHomework.objects.filter(
                        user=user,
                        title=dup['title'],
                        due_date=dup['due_date'],
                        site=dup['site']
                    ).exclude(id=dup['min_id']).delete()
                
                logger.info(f"Removed duplicate homework entries for user {user.email}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to clean up homework data: {str(cleanup_error)}")
            
            # Sync user to Supabase
            try:
                supabase_service = SupabaseService()
                supabase_service.sync_user_to_supabase(user)
            except Exception as supabase_error:
                logger.warning(f"Failed to sync user to Supabase: {str(supabase_error)}")
            
            # Check if this is the user's first login or if they need to setup credentials
            # Redirect logic:
            # 1. If no credentials at all -> onboarding (first time)
            # 2. If has credentials but not verified -> settings (to verify)
            # 3. If all good -> dashboard
            is_first_login = False
            needs_credential_setup = False
            
            try:
                # Check if user has any stored credentials
                from .models import UserCredential
                has_credentials = UserCredential.objects.filter(user=user).exists()
                print(f"DEBUG: User {user.email} has_credentials: {has_credentials}")
                
                if not has_credentials:
                    # No credentials at all - first time user
                    is_first_login = True
                    needs_credential_setup = True
                else:
                    # Has credentials - check if any are verified
                    verified_credentials = UserCredential.objects.filter(user=user, is_verified=True).exists()
                    print(f"DEBUG: User {user.email} has verified_credentials: {verified_credentials}")
                    
                    if not verified_credentials:
                        # Has credentials but none are verified - need to verify
                        needs_credential_setup = True
                
                print(f"DEBUG: User {user.email} is_first_login: {is_first_login}, needs_credential_setup: {needs_credential_setup}")
                
            except Exception as e:
                logger.warning(f"Error checking login status: {str(e)}")
                print(f"DEBUG: Error in login check: {str(e)}")
                # Default to dashboard if we can't determine (safer for returning users)
                is_first_login = False
                needs_credential_setup = False
            
            # Determine redirect URL
            if is_first_login:
                redirect_url = '/onboarding'
            elif needs_credential_setup:
                redirect_url = '/settings?setup=credentials'
            else:
                redirect_url = '/dashboard'
            
            # Return JSON response instead of redirect for frontend to handle
            response_data = {
                'message': 'Authentication successful',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                },
                'is_first_login': is_first_login,
                'needs_credential_setup': needs_credential_setup,
                'redirect_url': redirect_url
            }
            
            # For GET requests (direct backend callback), redirect to frontend with result
            if self.request.method == 'GET':
                # Force session to be saved
                request.session.modified = True
                request.session.save()
                session_key = request.session.session_key
                
                # Get frontend URL from settings
                frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
                
                print(f"DEBUG: Creating redirect with session_key: {session_key}")
                print(f"DEBUG: Redirect URL: {frontend_url}{redirect_url}")
                
                # Create redirect response to frontend
                from django.http import HttpResponse
                
                # Instead of redirecting, send an HTML page that will:
                # 1. Set the session cookie in the browser
                # 2. Redirect to the frontend
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Redirecting...</title>
                    <script>
                        // Set session info in localStorage for the frontend
                        localStorage.setItem('session_key', '{session_key}');
                        localStorage.setItem('user_authenticated', 'true');
                        // Redirect to frontend
                        window.location.href = '{frontend_url}{redirect_url}';
                    </script>
                </head>
                <body>
                    <p>Authentication successful! Redirecting...</p>
                </body>
                </html>
                """
                
                response = HttpResponse(html_content, content_type='text/html')
                
                # Determine cookie domain based on frontend URL
                cookie_domain = None
                if 'dovydas.space' in frontend_url:
                    cookie_domain = '.dovydas.space'  # Works for both nd.dovydas.space and api.dovydas.space
                elif 'localhost' in frontend_url:
                    cookie_domain = 'localhost'
                
                # Set session cookie that will work across subdomains
                response.set_cookie(
                    'sessionid',
                    session_key,
                    max_age=1209600,  # 2 weeks
                    path='/',
                    domain=cookie_domain,
                    secure='https' in frontend_url,  # Secure only for HTTPS
                    httponly=False,  # Allow JavaScript to read
                    samesite='Lax' if 'localhost' in frontend_url else 'None'  # None for cross-domain in production
                )
                
                print(f"DEBUG: Set-Cookie headers: {response.cookies}")
                
                return response
            
            # For POST requests (frontend callback), return JSON
            return Response(response_data)
                
        except Exception as e:
            # Log the error for debugging
            logger.error(f"OAuth callback error: {str(e)}")
            print(f"DEBUG: OAuth callback error: {str(e)}")
            print(f"DEBUG: Error type: {type(e).__name__}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            
            # Return JSON error response
            return Response({
                'error': str(e),
                'message': 'Authentication failed'
            }, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    """Logout user"""
    authentication_classes = []  # Disable authentication
    permission_classes = []  # Allow unauthenticated access
    
    def post(self, request):
        logout(request)
        return Response({
            'message': 'Successfully logged out'
        })

@method_decorator(csrf_exempt, name='dispatch')
class UserProfileView(APIView):
    """Get user profile information"""
    authentication_classes = [SessionAuthentication]  # Use session authentication
    permission_classes = []  # Allow unauthenticated access (will check manually)
    
    def get(self, request):
        print(f"DEBUG: UserProfileView - Session key: {request.session.session_key}")
        print(f"DEBUG: UserProfileView - User authenticated: {request.user.is_authenticated}")
        print(f"DEBUG: UserProfileView - Session data: {dict(request.session)}")
        print(f"DEBUG: UserProfileView - User: {request.user}")
        
        if not request.user.is_authenticated:
            return Response({
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if user has Google OAuth set up
        has_google_oauth = GoogleOAuth.objects.filter(user=request.user).exists()
        
        # Get user's site selections from Supabase
        try:
            supabase_service = SupabaseService()
            selected_sites = supabase_service.get_user_site_selections(request.user.id)
            user_profile = supabase_service.get_user_profile(request.user.id)
            preferences = user_profile.get('preferences', {}) if user_profile else {}
        except:
            selected_sites = []
            preferences = {}
        
        return Response({
            'user': {
                'id': request.user.id,
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'has_google_oauth': has_google_oauth,
                'selected_sites': selected_sites,
                'preferences': preferences,
            }
        })

@method_decorator(csrf_exempt, name='dispatch')
class SiteSelectionView(APIView):
    """Handle user site selection for scraping"""
    authentication_classes = []  # Disable authentication for GET
    permission_classes = []  # Allow unauthenticated access to get available sites
    
    def get(self, request):
        """Get available sites for scraping"""
        available_sites = [
            {'id': 'manodienynas', 'name': 'Manodienynas.lt', 'description': 'Lithuanian homework platform'},
            {'id': 'eduka', 'name': 'Eduka.lt', 'description': 'Lithuanian educational platform'},
        ]
        
        return Response({
            'available_sites': available_sites
        })
    
    def post(self, request):
        """Save user's selected sites"""
        if not request.user.is_authenticated:
            return Response({
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        selected_sites = request.data.get('selected_sites', [])
        
        if not selected_sites:
            return Response({
                'error': 'No sites selected'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            supabase_service = SupabaseService()
            supabase_service.save_user_site_selections(request.user.id, selected_sites)
            
            return Response({
                'message': 'Site selections saved successfully',
                'selected_sites': selected_sites
            })
        except Exception as e:
            return Response({
                'error': f'Failed to save site selections: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserPreferencesView(APIView):
    """Handle user preferences"""
    
    def post(self, request):
        """Update user preferences"""
        if not request.user.is_authenticated:
            return Response({
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        preferences = request.data.get('preferences', {})
        
        try:
            supabase_service = SupabaseService()
            result = supabase_service.update_user_preferences(request.user.id, preferences)
            
            return Response({
                'message': 'Preferences updated successfully',
                'preferences': preferences
            })
        except Exception as e:
            return Response({
                'error': f'Failed to update preferences: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class CredentialManagementView(APIView):
    """Handle user credential storage and retrieval"""
    authentication_classes = [SessionAuthentication]  # Use session authentication
    permission_classes = []  # Allow unauthenticated access to check auth status
    
    def get(self, request):
        """Get all user credentials (without passwords)"""
        print(f"DEBUG: CredentialManagementView GET - Session key: {request.session.session_key}")
        print(f"DEBUG: CredentialManagementView GET - User authenticated: {request.user.is_authenticated}")
        print(f"DEBUG: CredentialManagementView GET - User: {request.user}")
        print(f"DEBUG: CredentialManagementView GET - Session data: {dict(request.session)}")
        
        if not request.user.is_authenticated:
            return Response({
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            credential_storage = SecureCredentialStorage()
            credentials = credential_storage.get_all_user_credentials(request.user.id)
            
            # Remove passwords from response for security
            safe_credentials = {}
            for site, cred_data in credentials.items():
                safe_credentials[site] = {
                    'username': cred_data['username'],
                    'is_verified': cred_data['is_verified'],
                    'last_verified': cred_data['last_verified'].isoformat() if cred_data['last_verified'] else None,
                    'additional_data': cred_data.get('additional_data', {})
                }
            
            return Response({
                'credentials': safe_credentials
            })
            
        except Exception as e:
            import traceback
            logger.error(f"Error in CredentialManagementView GET: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return Response({
                'error': f'Failed to retrieve credentials: {str(e)}',
                'details': 'Check server logs for more information'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Store user credentials for a site"""
        print(f"DEBUG: CredentialManagementView POST - Session key: {request.session.session_key}")
        print(f"DEBUG: CredentialManagementView POST - User authenticated: {request.user.is_authenticated}")
        print(f"DEBUG: CredentialManagementView POST - User: {request.user}")
        print(f"DEBUG: CredentialManagementView POST - Session data: {dict(request.session)}")
        print(f"DEBUG: CredentialManagementView POST - Cookies: {request.COOKIES}")
        
        if not request.user.is_authenticated:
            return Response({
                'error': 'Please sign in with Google first to save credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        site = request.data.get('site')
        username = request.data.get('username')
        password = request.data.get('password')
        additional_data = request.data.get('additional_data', {})
        
        if not all([site, username, password]):
            return Response({
                'error': 'Site, username, and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            credential_storage = SecureCredentialStorage()
            credential = credential_storage.store_user_credentials(
                request.user.id, site, username, password, additional_data
            )
            
            return Response({
                'message': 'Credentials stored successfully',
                'site': site,
                'username': username,
                'is_verified': False
            })
            
        except Exception as e:
            return Response({
                'error': f'Failed to store credentials: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        """Update credential verification status"""
        if not request.user.is_authenticated:
            return Response({
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        site = request.data.get('site')
        is_verified = request.data.get('is_verified', False)
        
        if not site:
            return Response({
                'error': 'Site is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            credential_storage = SecureCredentialStorage()
            success = credential_storage.update_credential_verification(
                request.user.id, site, is_verified
            )
            
            if success:
                return Response({
                    'message': 'Verification status updated',
                    'site': site,
                    'is_verified': is_verified
                })
            else:
                return Response({
                    'error': 'Failed to update verification status'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'error': f'Failed to update verification: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request):
        """Delete user credentials for a site"""
        if not request.user.is_authenticated:
            return Response({
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        site = request.data.get('site')
        
        if not site:
            return Response({
                'error': 'Site is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            credential_storage = SecureCredentialStorage()
            success = credential_storage.delete_user_credentials(request.user.id, site)
            
            if success:
                return Response({
                    'message': 'Credentials deleted successfully',
                    'site': site
                })
            else:
                return Response({
                    'error': 'Failed to delete credentials'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'error': f'Failed to delete credentials: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class CredentialVerificationView(APIView):
    """Handle credential verification"""
    authentication_classes = [SessionAuthentication]  # Use session authentication
    permission_classes = []  # Allow unauthenticated access to check auth status
    
    def post(self, request):
        """Verify user credentials for a specific site"""
        print(f"DEBUG: CredentialVerificationView POST - Session key: {request.session.session_key}")
        print(f"DEBUG: CredentialVerificationView POST - User authenticated: {request.user.is_authenticated}")
        print(f"DEBUG: CredentialVerificationView POST - User: {request.user}")
        
        if not request.user.is_authenticated:
            response = Response({
                'error': 'User not authenticated',
                'success': False,
                'verified': False
            }, status=status.HTTP_401_UNAUTHORIZED)
            # Ensure CORS headers are set
            self._add_cors_headers(response, request)
            return response
        
        site = request.data.get('site')
        custom_url = request.data.get('url')  # Optional custom URL
        
        if not site:
            response = Response({
                'error': 'Site is required',
                'success': False,
                'verified': False
            }, status=status.HTTP_400_BAD_REQUEST)
            self._add_cors_headers(response, request)
            return response
        
        try:
            verification_service = CredentialVerificationService()
            success, message = verification_service.verify_credentials(
                request.user.id, site, custom_url
            )
            
            response = Response({
                'success': success,
                'message': message,
                'site': site,
                'verified': success
            })
            self._add_cors_headers(response, request)
            return response
            
        except Exception as e:
            logger.error(f"Error verifying credentials: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            response = Response({
                'error': f'Verification failed: {str(e)}',
                'success': False,
                'verified': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            self._add_cors_headers(response, request)
            return response
    
    def _add_cors_headers(self, response, request):
        """Manually add CORS headers to ensure they're present on error responses"""
        from django.conf import settings
        origin = request.META.get('HTTP_ORIGIN', '')
        
        # Check if origin is allowed
        allowed_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        if origin in allowed_origins or origin.endswith('.dovydas.space'):
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'accept, accept-encoding, authorization, content-type, dnt, origin, user-agent, x-csrftoken, x-requested-with'
        return response

@method_decorator(ensure_csrf_cookie, name='dispatch')
class CSRFTokenView(APIView):
    """Get CSRF token for frontend"""
    authentication_classes = []  # Disable authentication
    permission_classes = []  # Allow unauthenticated access
    
    def get(self, request):
        return Response({
            'csrfToken': get_token(request)
        })
