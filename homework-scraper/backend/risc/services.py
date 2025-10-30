import json
import jwt
import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
from .models import SecurityEvent, RISCConfiguration, UserSecurityAction
import logging

logger = logging.getLogger(__name__)


class RISCTokenValidator:
    """Validates JWT tokens from Google's RISC service"""
    
    def __init__(self):
        self.jwks_cache = None
        self.jwks_cache_time = None
        self.cache_duration = timedelta(hours=24)
    
    def get_risc_configuration(self):
        """Fetch RISC configuration from Google"""
        try:
            response = requests.get('https://accounts.google.com/.well-known/risc-configuration')
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch RISC configuration: {e}")
            # Return defaults
            return {
                'issuer': 'https://accounts.google.com/',
                'jwks_uri': 'https://www.googleapis.com/oauth2/v3/certs'
            }
    
    def get_jwks(self):
        """Get JSON Web Key Set from Google"""
        # Check cache
        if (self.jwks_cache and self.jwks_cache_time and 
            timezone.now() - self.jwks_cache_time < self.cache_duration):
            return self.jwks_cache
        
        try:
            config = self.get_risc_configuration()
            jwks_uri = config.get('jwks_uri', 'https://www.googleapis.com/oauth2/v3/certs')
            
            response = requests.get(jwks_uri)
            response.raise_for_status()
            
            self.jwks_cache = response.json()
            self.jwks_cache_time = timezone.now()
            
            return self.jwks_cache
        except Exception as e:
            logger.error(f"Failed to fetch JWKS: {e}")
            raise
    
    def validate_token(self, token_string):
        """
        Validate JWT token from RISC event
        Returns decoded token if valid, raises exception if invalid
        """
        try:
            # Get signing keys
            jwks = self.get_jwks()
            
            # Decode header to get key ID
            unverified_header = jwt.get_unverified_header(token_string)
            kid = unverified_header.get('kid')
            
            if not kid:
                raise ValueError("Token header missing 'kid' field")
            
            # Find the correct key
            signing_key = None
            for key in jwks.get('keys', []):
                if key.get('kid') == kid:
                    signing_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
                    break
            
            if not signing_key:
                raise ValueError(f"No signing key found for kid: {kid}")
            
            # Get expected audience from settings
            risc_config = RISCConfiguration.objects.filter(is_active=True).first()
            if risc_config:
                expected_audience = risc_config.receiver_endpoint
            else:
                expected_audience = getattr(settings, 'RISC_RECEIVER_URL', None)
            
            if not expected_audience:
                raise ValueError("RISC receiver URL not configured")
            
            # Validate token
            decoded = jwt.decode(
                token_string,
                signing_key,
                algorithms=['RS256'],
                audience=expected_audience,
                issuer='https://accounts.google.com/'
            )
            
            # Check required claims
            required_claims = ['iss', 'aud', 'iat', 'jti', 'events']
            for claim in required_claims:
                if claim not in decoded:
                    raise ValueError(f"Token missing required claim: {claim}")
            
            # Check if event was already processed (duplicate)
            jti = decoded['jti']
            if SecurityEvent.objects.filter(jti=jti).exists():
                raise ValueError(f"Event already processed: {jti}")
            
            return decoded
            
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            raise
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {e}")
            raise
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            raise


class RISCEventHandler:
    """Handles different types of RISC security events"""
    
    def __init__(self):
        self.event_type_map = {
            'https://schemas.openid.net/secevent/risc/event-type/sessions-revoked': self.handle_sessions_revoked,
            'https://schemas.openid.net/secevent/oauth/event-type/tokens-revoked': self.handle_tokens_revoked,
            'https://schemas.openid.net/secevent/oauth/event-type/token-revoked': self.handle_token_revoked,
            'https://schemas.openid.net/secevent/risc/event-type/account-disabled': self.handle_account_disabled,
            'https://schemas.openid.net/secevent/risc/event-type/account-enabled': self.handle_account_enabled,
            'https://schemas.openid.net/secevent/risc/event-type/account-credential-change-required': self.handle_credential_change_required,
            'https://schemas.openid.net/secevent/risc/event-type/verification': self.handle_verification,
        }
    
    def get_user_by_google_sub(self, google_sub):
        """Find user by Google subject ID"""
        try:
            # Assuming you store Google sub in a social auth model or user profile
            # Adjust based on your authentication implementation
            from allauth.socialaccount.models import SocialAccount
            social_account = SocialAccount.objects.get(provider='google', uid=google_sub)
            return social_account.user
        except:
            # Fallback: try to find by email if available
            logger.warning(f"Could not find user by Google sub: {google_sub}")
            return None
    
    def handle_sessions_revoked(self, event_data, security_event):
        """Handle sessions-revoked event"""
        google_sub = event_data['subject']['subject']['email'] if 'email' in event_data['subject']['subject'] else event_data['subject']['subject'].get('id')
        user = self.get_user_by_google_sub(google_sub)
        
        if not user:
            logger.warning(f"User not found for sessions-revoked event: {google_sub}")
            return "User not found in system"
        
        # Delete all active sessions for this user
        sessions = Session.objects.all()
        deleted_count = 0
        
        for session in sessions:
            session_data = session.get_decoded()
            if session_data.get('_auth_user_id') == str(user.id):
                session.delete()
                deleted_count += 1
        
        # Create security action record
        UserSecurityAction.objects.create(
            user=user,
            security_event=security_event,
            action_type='session_revoked',
            action_details=f"Revoked {deleted_count} active sessions due to RISC event"
        )
        
        logger.info(f"Revoked {deleted_count} sessions for user {user.email}")
        return f"Revoked {deleted_count} sessions"
    
    def handle_tokens_revoked(self, event_data, security_event):
        """Handle tokens-revoked event (all OAuth tokens)"""
        google_sub = event_data['subject']['subject']['email'] if 'email' in event_data['subject']['subject'] else event_data['subject']['subject'].get('id')
        user = self.get_user_by_google_sub(google_sub)
        
        if not user:
            logger.warning(f"User not found for tokens-revoked event: {google_sub}")
            return "User not found in system"
        
        # Delete OAuth tokens (adjust based on your OAuth implementation)
        try:
            from allauth.socialaccount.models import SocialToken
            tokens = SocialToken.objects.filter(account__user=user, account__provider='google')
            token_count = tokens.count()
            tokens.delete()
            
            # Create security action record
            UserSecurityAction.objects.create(
                user=user,
                security_event=security_event,
                action_type='oauth_tokens_deleted',
                action_details=f"Deleted {token_count} OAuth tokens due to RISC event"
            )
            
            logger.info(f"Deleted {token_count} OAuth tokens for user {user.email}")
            return f"Deleted {token_count} OAuth tokens"
        except Exception as e:
            logger.error(f"Error deleting OAuth tokens: {e}")
            return f"Error: {str(e)}"
    
    def handle_token_revoked(self, event_data, security_event):
        """Handle token-revoked event (specific token)"""
        google_sub = event_data['subject']['subject']['email'] if 'email' in event_data['subject']['subject'] else event_data['subject']['subject'].get('id')
        user = self.get_user_by_google_sub(google_sub)
        
        if not user:
            logger.warning(f"User not found for token-revoked event: {google_sub}")
            return "User not found in system"
        
        # Get token identifier from event
        event_info = event_data['event_data']
        token_identifier_alg = event_info.get('token_identifier_alg')
        token_identifier = event_info.get('token_identifier')
        
        # Store in security event
        security_event.token_identifier_alg = token_identifier_alg
        security_event.token_identifier = token_identifier
        security_event.save()
        
        # Try to find and delete the specific token
        # Implementation depends on how you store and can identify tokens
        action_details = f"Token revoked (alg: {token_identifier_alg}, identifier: {token_identifier[:20]}...)"
        
        UserSecurityAction.objects.create(
            user=user,
            security_event=security_event,
            action_type='oauth_tokens_deleted',
            action_details=action_details
        )
        
        logger.info(f"Specific token revoked for user {user.email}")
        return "Specific token revoked"
    
    def handle_account_disabled(self, event_data, security_event):
        """Handle account-disabled event"""
        google_sub = event_data['subject']['subject']['email'] if 'email' in event_data['subject']['subject'] else event_data['subject']['subject'].get('id')
        user = self.get_user_by_google_sub(google_sub)
        
        if not user:
            logger.warning(f"User not found for account-disabled event: {google_sub}")
            return "User not found in system"
        
        # Get reason for disabling
        event_info = event_data['event_data']
        reason = event_info.get('reason', '')
        
        security_event.disable_reason = reason
        security_event.save()
        
        # Disable Google Sign-In for this user
        # This could involve:
        # 1. Setting a flag in user profile
        # 2. Deleting social account connection
        # 3. Sending notification to user
        
        action_details = f"Google account disabled. Reason: {reason}. Temporarily disabled Google Sign-In."
        
        UserSecurityAction.objects.create(
            user=user,
            security_event=security_event,
            action_type='google_signin_disabled',
            action_details=action_details
        )
        
        # Revoke sessions as well for security
        sessions = Session.objects.all()
        for session in sessions:
            session_data = session.get_decoded()
            if session_data.get('_auth_user_id') == str(user.id):
                session.delete()
        
        logger.warning(f"Account disabled for user {user.email}, reason: {reason}")
        return f"Account disabled: {reason}"
    
    def handle_account_enabled(self, event_data, security_event):
        """Handle account-enabled event"""
        google_sub = event_data['subject']['subject']['email'] if 'email' in event_data['subject']['subject'] else event_data['subject']['subject'].get('id')
        user = self.get_user_by_google_sub(google_sub)
        
        if not user:
            logger.warning(f"User not found for account-enabled event: {google_sub}")
            return "User not found in system"
        
        # Re-enable Google Sign-In for this user
        UserSecurityAction.objects.create(
            user=user,
            security_event=security_event,
            action_type='google_signin_enabled',
            action_details="Google account re-enabled"
        )
        
        logger.info(f"Account re-enabled for user {user.email}")
        return "Account re-enabled"
    
    def handle_credential_change_required(self, event_data, security_event):
        """Handle account-credential-change-required event"""
        google_sub = event_data['subject']['subject']['email'] if 'email' in event_data['subject']['subject'] else event_data['subject']['subject'].get('id')
        user = self.get_user_by_google_sub(google_sub)
        
        if not user:
            logger.warning(f"User not found for credential-change event: {google_sub}")
            return "User not found in system"
        
        # Flag account for review, but don't take immediate action
        # Send notification to user
        UserSecurityAction.objects.create(
            user=user,
            security_event=security_event,
            action_type='account_flagged',
            action_details="Google detected potential credential compromise. Monitor for suspicious activity."
        )
        
        logger.warning(f"Credential change required for user {user.email}")
        return "Account flagged for credential change"
    
    def handle_verification(self, event_data, security_event):
        """Handle verification event (test/ping from Google)"""
        # Extract state if present
        event_info = event_data.get('event_data', {})
        state = event_info.get('state', '')
        
        security_event.verification_state = state
        security_event.save()
        
        logger.info(f"Received verification event with state: {state}")
        return f"Verification successful, state: {state}"
    
    def process_event(self, decoded_token, token_string):
        """Process a validated RISC event token"""
        try:
            # Extract event information
            events = decoded_token.get('events', {})
            
            # There should be exactly one event type per token
            if len(events) != 1:
                raise ValueError(f"Expected 1 event, got {len(events)}")
            
            event_type_uri = list(events.keys())[0]
            event_data = events[event_type_uri]
            
            # Map event type URI to short name
            event_type_map = {
                'https://schemas.openid.net/secevent/risc/event-type/sessions-revoked': 'sessions_revoked',
                'https://schemas.openid.net/secevent/oauth/event-type/tokens-revoked': 'tokens_revoked',
                'https://schemas.openid.net/secevent/oauth/event-type/token-revoked': 'token_revoked',
                'https://schemas.openid.net/secevent/risc/event-type/account-disabled': 'account_disabled',
                'https://schemas.openid.net/secevent/risc/event-type/account-enabled': 'account_enabled',
                'https://schemas.openid.net/secevent/risc/event-type/account-credential-change-required': 'account_credential_change_required',
                'https://schemas.openid.net/secevent/risc/event-type/verification': 'verification',
            }
            
            event_type_short = event_type_map.get(event_type_uri, 'unknown')
            
            # Extract subject information
            subject_obj = event_data.get('subject', {})
            subject = subject_obj.get('subject', {})
            google_sub = subject.get('email') or subject.get('id', '')
            google_email = subject.get('email', '')
            
            # Find user
            user = self.get_user_by_google_sub(google_sub)
            
            # Create SecurityEvent record
            security_event = SecurityEvent.objects.create(
                jti=decoded_token['jti'],
                event_type=event_type_short,
                issued_at=timezone.datetime.fromtimestamp(decoded_token['iat'], tz=timezone.utc),
                user=user,
                google_sub=google_sub,
                google_email=google_email,
                raw_token=token_string,
                raw_event_data=decoded_token
            )
            
            # Process event based on type
            handler = self.event_type_map.get(event_type_uri)
            if handler:
                action_taken = handler({'event_data': event_data, 'subject': subject_obj}, security_event)
                security_event.action_taken = action_taken
                security_event.processed = True
                security_event.processed_at = timezone.now()
                security_event.save()
                
                return {
                    'success': True,
                    'event_type': event_type_short,
                    'action': action_taken
                }
            else:
                error_msg = f"No handler for event type: {event_type_uri}"
                security_event.error_message = error_msg
                security_event.save()
                
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except Exception as e:
            logger.error(f"Error processing RISC event: {e}", exc_info=True)
            raise
