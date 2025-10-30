from django.contrib import admin
from .models import SecurityEvent, RISCConfiguration, UserSecurityAction


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ['jti', 'event_type', 'google_email', 'received_at', 'processed', 'user']
    list_filter = ['event_type', 'processed', 'received_at', 'disable_reason']
    search_fields = ['jti', 'google_sub', 'google_email', 'user__email']
    readonly_fields = ['jti', 'received_at', 'issued_at', 'raw_token', 'raw_event_data']
    date_hierarchy = 'received_at'
    
    fieldsets = (
        ('Event Information', {
            'fields': ('jti', 'event_type', 'received_at', 'issued_at')
        }),
        ('User Information', {
            'fields': ('user', 'google_sub', 'google_email')
        }),
        ('Event Details', {
            'fields': ('disable_reason', 'verification_state', 'token_identifier_alg', 'token_identifier')
        }),
        ('Processing Status', {
            'fields': ('processed', 'processed_at', 'action_taken', 'error_message')
        }),
        ('Raw Data', {
            'fields': ('raw_token', 'raw_event_data'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Security events are created automatically
        return False


@admin.register(RISCConfiguration)
class RISCConfigurationAdmin(admin.ModelAdmin):
    list_display = ['is_active', 'stream_enabled', 'receiver_endpoint', 'last_synced_at']
    readonly_fields = ['created_at', 'updated_at', 'last_synced_at']
    
    fieldsets = (
        ('Status', {
            'fields': ('is_active', 'stream_enabled')
        }),
        ('Configuration', {
            'fields': ('service_account_file', 'receiver_endpoint')
        }),
        ('Event Subscriptions', {
            'fields': (
                'subscribe_sessions_revoked',
                'subscribe_tokens_revoked',
                'subscribe_token_revoked',
                'subscribe_account_disabled',
                'subscribe_account_enabled',
                'subscribe_account_credential_change_required',
                'subscribe_verification'
            )
        }),
        ('Google RISC Configuration', {
            'fields': ('risc_issuer', 'risc_jwks_uri')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'last_synced_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one configuration
        if RISCConfiguration.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(UserSecurityAction)
class UserSecurityActionAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'performed_at', 'is_active', 'security_event']
    list_filter = ['action_type', 'is_active', 'performed_at']
    search_fields = ['user__email', 'action_details']
    readonly_fields = ['performed_at']
    date_hierarchy = 'performed_at'
    
    fieldsets = (
        ('Action Information', {
            'fields': ('user', 'security_event', 'action_type', 'performed_at')
        }),
        ('Details', {
            'fields': ('action_details', 'is_active', 'expires_at')
        }),
    )
    
    def has_add_permission(self, request):
        # Security actions are created automatically
        return False
