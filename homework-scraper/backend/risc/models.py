from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class SecurityEvent(models.Model):
    """Store received RISC security events for auditing and de-duplication"""
    
    EVENT_TYPES = [
        ('sessions_revoked', 'Sessions Revoked'),
        ('tokens_revoked', 'Tokens Revoked'),
        ('token_revoked', 'Token Revoked'),
        ('account_disabled', 'Account Disabled'),
        ('account_enabled', 'Account Enabled'),
        ('account_credential_change_required', 'Account Credential Change Required'),
        ('verification', 'Verification'),
    ]
    
    DISABLE_REASONS = [
        ('hijacking', 'Hijacking'),
        ('bulk-account', 'Bulk Account'),
        ('', 'Not Specified'),
    ]
    
    # Unique identifier for the event (jti claim from JWT)
    jti = models.CharField(max_length=255, unique=True, db_index=True)
    
    # Event metadata
    event_type = models.CharField(max_length=100, choices=EVENT_TYPES)
    received_at = models.DateTimeField(default=timezone.now, db_index=True)
    issued_at = models.DateTimeField()  # iat claim from JWT
    
    # User information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='security_events')
    google_sub = models.CharField(max_length=255, db_index=True)  # Google Account ID
    google_email = models.EmailField(blank=True, null=True)
    
    # Event-specific data
    disable_reason = models.CharField(max_length=50, choices=DISABLE_REASONS, blank=True)
    verification_state = models.TextField(blank=True)  # For verification events
    token_identifier_alg = models.CharField(max_length=50, blank=True)  # For token revocation
    token_identifier = models.TextField(blank=True)  # For token revocation
    
    # Processing status
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    action_taken = models.TextField(blank=True)  # Description of action taken
    error_message = models.TextField(blank=True)  # If processing failed
    
    # Raw event data
    raw_token = models.TextField()  # The original JWT
    raw_event_data = models.JSONField()  # Decoded event claims
    
    class Meta:
        ordering = ['-received_at']
        indexes = [
            models.Index(fields=['google_sub', '-received_at']),
            models.Index(fields=['event_type', '-received_at']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.google_sub} - {self.received_at}"


class RISCConfiguration(models.Model):
    """Store RISC stream configuration"""
    
    # Only one active configuration should exist
    is_active = models.BooleanField(default=True, unique=True)
    
    # Service account credentials path
    service_account_file = models.CharField(max_length=500)
    
    # Receiver endpoint URL
    receiver_endpoint = models.URLField()
    
    # Stream status
    stream_enabled = models.BooleanField(default=True)
    
    # Events to subscribe to
    subscribe_sessions_revoked = models.BooleanField(default=True)
    subscribe_tokens_revoked = models.BooleanField(default=True)
    subscribe_token_revoked = models.BooleanField(default=True)
    subscribe_account_disabled = models.BooleanField(default=True)
    subscribe_account_enabled = models.BooleanField(default=True)
    subscribe_account_credential_change_required = models.BooleanField(default=True)
    subscribe_verification = models.BooleanField(default=True)
    
    # Configuration metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    
    # Google's RISC configuration (cached)
    risc_issuer = models.CharField(max_length=255, default='https://accounts.google.com/')
    risc_jwks_uri = models.URLField(default='https://www.googleapis.com/oauth2/v3/certs')
    
    def __str__(self):
        status = "Enabled" if self.stream_enabled else "Disabled"
        return f"RISC Configuration ({status})"
    
    def get_subscribed_events(self):
        """Return list of event types to subscribe to"""
        events = []
        if self.subscribe_sessions_revoked:
            events.append('https://schemas.openid.net/secevent/risc/event-type/sessions-revoked')
        if self.subscribe_tokens_revoked:
            events.append('https://schemas.openid.net/secevent/oauth/event-type/tokens-revoked')
        if self.subscribe_token_revoked:
            events.append('https://schemas.openid.net/secevent/oauth/event-type/token-revoked')
        if self.subscribe_account_disabled:
            events.append('https://schemas.openid.net/secevent/risc/event-type/account-disabled')
        if self.subscribe_account_enabled:
            events.append('https://schemas.openid.net/secevent/risc/event-type/account-enabled')
        if self.subscribe_account_credential_change_required:
            events.append('https://schemas.openid.net/secevent/risc/event-type/account-credential-change-required')
        if self.subscribe_verification:
            events.append('https://schemas.openid.net/secevent/risc/event-type/verification')
        return events


class UserSecurityAction(models.Model):
    """Track security actions taken on user accounts"""
    
    ACTION_TYPES = [
        ('session_revoked', 'Session Revoked'),
        ('google_signin_disabled', 'Google Sign-In Disabled'),
        ('google_signin_enabled', 'Google Sign-In Enabled'),
        ('oauth_tokens_deleted', 'OAuth Tokens Deleted'),
        ('account_flagged', 'Account Flagged for Review'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='security_actions')
    security_event = models.ForeignKey(SecurityEvent, on_delete=models.SET_NULL, null=True, blank=True)
    
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    action_details = models.TextField(blank=True)
    performed_at = models.DateTimeField(default=timezone.now)
    
    # For temporary actions (like disabling sign-in)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-performed_at']
    
    def __str__(self):
        return f"{self.action_type} - {self.user.email} - {self.performed_at}"
