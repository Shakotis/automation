from django.contrib import admin
from .models import GoogleOAuth

@admin.register(GoogleOAuth)
class GoogleOAuthAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at', 'token_expiry']
    list_filter = ['created_at', 'updated_at', 'token_expiry']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'access_token', 'refresh_token']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')
