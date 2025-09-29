from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.contrib.auth.models import User
from tasks.services import GoogleOAuthService
from .models import GoogleOAuth
import json

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

class GoogleOAuthCallbackView(APIView):
    """Handle Google OAuth callback"""
    permission_classes = []
    
    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')
        
        if not code:
            return Response({
                'error': 'Authorization code not provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = GoogleOAuthService.handle_oauth_callback(request, code, state)
            login(request, user)
            
            return Response({
                'message': 'Successfully authenticated',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    """Logout user"""
    
    def post(self, request):
        logout(request)
        return Response({
            'message': 'Successfully logged out'
        })

class UserProfileView(APIView):
    """Get user profile information"""
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if user has Google OAuth set up
        has_google_oauth = GoogleOAuth.objects.filter(user=request.user).exists()
        
        return Response({
            'user': {
                'id': request.user.id,
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'has_google_oauth': has_google_oauth,
            }
        })
