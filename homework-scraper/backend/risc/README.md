# Google RISC (Cross-Account Protection) Implementation

## Overview

This Django app implements Google's RISC (Risk and Incident Sharing and Coordination) protocol to receive real-time security event notifications about user accounts.

## Features

- ✅ Receives and validates RISC Security Event Tokens (JWT)
- ✅ Handles all 7 RISC event types
- ✅ Automatic session/token revocation based on security events
- ✅ De-duplication of events using JTI
- ✅ Comprehensive event logging and auditing
- ✅ Django admin interface for monitoring
- ✅ Management command for stream configuration

## Event Types Supported

1. **sessions-revoked** - Revokes all user sessions
2. **tokens-revoked** - Deletes all OAuth tokens
3. **token-revoked** - Deletes specific OAuth token
4. **account-disabled** - Disables Google Sign-In
5. **account-enabled** - Re-enables Google Sign-In
6. **account-credential-change-required** - Flags account for review
7. **verification** - Test/ping event

## Setup Instructions

### 1. Add to INSTALLED_APPS

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'risc',
]
```

### 2. Configure URLs

```python
# urls.py
urlpatterns = [
    # ...
    path('risc/', include('risc.urls')),
]
```

### 3. Set RISC Receiver URL

```python
# settings.py
RISC_RECEIVER_URL = 'https://api.dovydas.space/risc/receiver/'
```

### 4. Run Migrations

```bash
python manage.py makemigrations risc
python manage.py migrate risc
```

### 5. Create RISC Configuration

Via Django admin or shell:

```python
from risc.models import RISCConfiguration

RISCConfiguration.objects.create(
    is_active=True,
    service_account_file='/path/to/service-account.json',
    receiver_endpoint='https://api.dovydas.space/risc/receiver/',
    stream_enabled=True,
    # All event subscriptions are True by default
)
```

### 6. Setup Google Cloud Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new service account or use existing one
3. Grant the service account the **RISC Configuration Admin** role
4. Download the JSON key file
5. Store securely on your server

### 7. Configure RISC Stream

Use the management command to register your receiver with Google:

```bash
python manage.py configure_risc \
    --service-account /path/to/service-account.json \
    --receiver-url https://api.dovydas.space/risc/receiver/
```

To test the receiver endpoint:

```bash
python manage.py configure_risc \
    --service-account /path/to/service-account.json \
    --receiver-url https://api.dovydas.space/risc/receiver/ \
    --verify-only
```

To disable the stream:

```bash
python manage.py configure_risc \
    --service-account /path/to/service-account.json \
    --receiver-url https://api.dovydas.space/risc/receiver/ \
    --disable
```

## Security Considerations

### HTTPS Required

Your receiver endpoint **MUST** use HTTPS. Google will not send events to HTTP endpoints.

### Token Validation

All incoming tokens are validated:
- ✅ Signature verification using Google's public keys
- ✅ Issuer validation (`https://accounts.google.com/`)
- ✅ Audience validation (your receiver URL)
- ✅ JTI de-duplication to prevent replay attacks

### Rate Limiting

Consider implementing rate limiting on the receiver endpoint to prevent abuse.

## Monitoring

### Django Admin

View and manage events in Django admin:
- `/admin/risc/securityevent/` - All received events
- `/admin/risc/riscconfiguration/` - Stream configuration
- `/admin/risc/usersecurityaction/` - Actions taken on users

### Status Endpoint

Check RISC status programmatically:

```bash
GET /risc/status/
```

Returns:
```json
{
  "configured": true,
  "enabled": true,
  "receiver_endpoint": "https://api.dovydas.space/risc/receiver/",
  "statistics": {
    "total_events": 42,
    "processed_events": 40,
    "failed_events": 2
  },
  "recent_events": [...],
  "subscribed_events": [...]
}
```

## Event Processing Logic

### sessions-revoked
- Deletes all Django sessions for the user
- Creates UserSecurityAction record

### tokens-revoked
- Deletes all OAuth tokens from `allauth.socialaccount`
- Creates UserSecurityAction record

### token-revoked
- Attempts to delete specific token
- Logs token identifier for manual review

### account-disabled
- Disables Google Sign-In for user
- Revokes all active sessions
- Logs disable reason (hijacking/bulk-account)

### account-enabled
- Re-enables Google Sign-In
- Creates notification record

### account-credential-change-required
- Flags account for review
- Does NOT automatically disable account
- Can be used to trigger additional monitoring

### verification
- Acknowledges test event
- Returns 202 Accepted

## Testing

### Send Test Verification Event

```bash
python manage.py configure_risc \
    --service-account /path/to/service-account.json \
    --receiver-url https://api.dovydas.space/risc/receiver/ \
    --verify-only
```

### Check Logs

```bash
# Backend logs
journalctl -u homework-scraper.service -f | grep RISC

# Django logs
tail -f /path/to/django.log | grep risc
```

### Manually Test Token Validation

```python
from risc.services import RISCTokenValidator

validator = RISCTokenValidator()
decoded = validator.validate_token(your_test_token)
print(decoded)
```

## Troubleshooting

### Common Errors

**400 Bad Request**: Invalid receiver URL or event configuration
- Verify URL is HTTPS
- Check event type URIs are correct

**401 Unauthorized**: Invalid service account credentials
- Regenerate service account key
- Verify JSON file is valid

**403 Forbidden**: Insufficient permissions
- Grant service account "RISC Configuration Admin" role
- Ensure project has RISC API enabled

**404 Not Found**: RISC API not enabled
- Enable RISC API in Google Cloud Console
- Wait a few minutes for propagation

### Event Not Being Processed

1. Check if event was received: `SecurityEvent.objects.filter(jti=...)`
2. Check processing status: `event.processed`, `event.error_message`
3. Check user mapping: Verify user exists with correct Google sub
4. Check logs for exceptions

### User Not Found

The event handler tries to find users by Google subject ID. If using `django-allauth`:

```python
from allauth.socialaccount.models import SocialAccount
social_account = SocialAccount.objects.get(provider='google', uid=google_sub)
user = social_account.user
```

If using a different auth system, modify `get_user_by_google_sub()` in `services.py`.

## API Reference

### POST /risc/receiver/

Receives RISC Security Event Tokens from Google.

**Content-Type**: `application/secevent+jwt` or `application/json`

**Request Body**:
- JWT token as raw string, OR
- JSON: `{"token": "eyJ..."}` or `{"SET": "eyJ..."}`

**Response Codes**:
- `202 Accepted` - Event received and processed
- `400 Bad Request` - Invalid token or request
- `500 Internal Server Error` - Processing error

### GET /risc/status/

Get RISC integration status and statistics.

**Response**:
```json
{
  "configured": true,
  "enabled": true,
  "receiver_endpoint": "https://...",
  "statistics": {...},
  "recent_events": [...],
  "subscribed_events": [...]
}
```

## Dependencies

Required packages (add to requirements.txt):

```
PyJWT>=2.8.0
cryptography>=41.0.0
requests>=2.31.0
google-auth>=2.23.0
```

Install:
```bash
pip install PyJWT cryptography requests google-auth
```

## Production Checklist

- [ ] HTTPS enabled on receiver endpoint
- [ ] Service account created with RISC Configuration Admin role
- [ ] Service account JSON stored securely (not in git)
- [ ] RISC configuration created in database
- [ ] Stream configured with Google via management command
- [ ] Verification event tested successfully
- [ ] Monitoring set up for SecurityEvent table
- [ ] Logging configured for risc module
- [ ] Rate limiting enabled on receiver endpoint
- [ ] Alerts configured for failed events
- [ ] User notification system for security actions

## Further Reading

- [Google RISC Documentation](https://developers.google.com/identity/protocols/risc)
- [OpenID RISC Specification](https://openid.net/specs/openid-risc-profile-specification-1_0.html)
- [Security Event Token (SET) Specification](https://tools.ietf.org/html/rfc8417)
