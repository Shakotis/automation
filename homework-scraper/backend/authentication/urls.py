from django.urls import path
from . import views

urlpatterns = [
    path('google/login', views.GoogleOAuthLoginView.as_view(), name='google-login'),
    path('google/callback', views.GoogleOAuthCallbackView.as_view(), name='google-callback'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('user', views.UserProfileView.as_view(), name='user-profile'),
    path('sites', views.SiteSelectionView.as_view(), name='site-selection'),
    path('preferences', views.UserPreferencesView.as_view(), name='user-preferences'),
    path('credentials', views.CredentialManagementView.as_view(), name='credential-management'),
    path('verify-credentials', views.CredentialVerificationView.as_view(), name='credential-verification'),
]