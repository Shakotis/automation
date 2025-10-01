from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.utils.decorators import method_decorator
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
    permission_classes = []
    
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
    permission_classes = []
    
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
            print(f"DEBUG: Session key after login: {request.session.session_key}")
            print(f"DEBUG: User authenticated after login: {request.user.is_authenticated}")
            print(f"DEBUG: Session data: {dict(request.session)}")
            
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
                return redirect(f'http://localhost:3000{redirect_url}')
            
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
    permission_classes = []  # Allow unauthenticated access
    
    def post(self, request):
        logout(request)
        return Response({
            'message': 'Successfully logged out'
        })

@method_decorator(csrf_exempt, name='dispatch')
class UserProfileView(APIView):
    """Get user profile information"""
    permission_classes = []  # Allow unauthenticated access
    
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
    permission_classes = []  # Allow unauthenticated access to check auth status
    
    def get(self, request):
        """Get all user credentials (without passwords)"""
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
            return Response({
                'error': f'Failed to retrieve credentials: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Store user credentials for a site"""
        if not request.user.is_authenticated:
            return Response({
                'error': 'User not authenticated'
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
            
            # Clear any existing sessions when new credentials are stored
            try:
                from .session_manager import ScrapingSessionManager
                session_manager = ScrapingSessionManager(request.user.id, site)
                session_manager.clear_session()
            except Exception as session_error:
                logger.warning(f"Failed to clear session: {session_error}")
            
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
                # Clear any saved sessions for this site when credentials are deleted
                try:
                    from .session_manager import ScrapingSessionManager
                    session_manager = ScrapingSessionManager(request.user.id, site)
                    session_manager.clear_session()
                except Exception as session_error:
                    logger.warning(f"Failed to clear session: {session_error}")
                
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
    
    def post(self, request):
        """Verify user credentials for a specific site"""
        if not request.user.is_authenticated:
            return Response({
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        site = request.data.get('site')
        custom_url = request.data.get('url')  # Optional custom URL
        
        if not site:
            return Response({
                'error': 'Site is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            verification_service = CredentialVerificationService()
            success, message = verification_service.verify_credentials(
                request.user.id, site, custom_url
            )
            
            return Response({
                'success': success,
                'message': message,
                'site': site,
                'verified': success
            })
            
        except Exception as e:
            logger.error(f"Error verifying credentials: {str(e)}")
            return Response({
                'error': f'Verification failed: {str(e)}',
                'success': False,
                'verified': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(ensure_csrf_cookie, name='dispatch')
class CSRFTokenView(APIView):
    """Get CSRF token for frontend"""
    permission_classes = []
    
    def get(self, request):
        return Response({
            'csrfToken': get_token(request)
        })
