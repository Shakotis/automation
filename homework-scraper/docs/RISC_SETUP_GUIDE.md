# RISC Integration Configuration Guide

## Django Settings Changes

Add these configurations to your Django settings file.

### 1. Add to INSTALLED_APPS

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'risc',
]
```

### 2. Add RISC Configuration

```python
# RISC (Cross-Account Protection) Configuration
RISC_RECEIVER_URL = os.environ.get('RISC_RECEIVER_URL', 'https://api.dovydas.space/risc/receiver/')
```

### 3. Update URL Configuration

In your main `urls.py` (typically `homework_scraper/urls.py`):

```python
from django.urls import path, include

urlpatterns = [
    # ... existing patterns ...
    path('risc/', include('risc.urls')),
]
```

## Google Cloud Service Account Setup

### Step 1: Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create a new one)
3. Navigate to **IAM & Admin > Service Accounts**
4. Click **Create Service Account**
5. Name it: `risc-receiver` (or any name you prefer)
6. Click **Create and Continue**

### Step 2: Grant RISC Configuration Admin Role

1. In the service account creation wizard, add role:
   - Role: **RISC Configuration Admin**
   - If not available, you may need to enable the RISC API first
2. Click **Continue**
3. Click **Done**

### Step 3: Create and Download Key

1. Find your new service account in the list
2. Click the three dots menu > **Manage Keys**
3. Click **Add Key > Create New Key**
4. Choose **JSON** format
5. Click **Create**
6. Save the downloaded JSON file securely
7. Transfer to your RPI: `scp service-account.json dovydukas@192.168.1.33:/home/dovydukas/`

### Step 4: Enable RISC API

1. Go to **APIs & Services > Library**
2. Search for "RISC"
3. Click on **RISC API** or **Cross-Account Protection API**
4. Click **Enable**
5. Wait a few minutes for propagation

## Initial Configuration

### 1. SSH to RPI and Create Configuration

```bash
ssh dovydukas@192.168.1.33
cd /home/dovydukas/homework-scraper-backend
source venv/bin/activate
python manage.py shell
```

In the Django shell:

```python
from risc.models import RISCConfiguration

config = RISCConfiguration.objects.create(
    is_active=True,
    service_account_file='/home/dovydukas/service-account.json',
    receiver_endpoint='https://api.dovydas.space/risc/receiver/',
    stream_enabled=True,
    # All event subscriptions are enabled by default
)

print(f"Configuration created: {config}")
exit()
```

### 2. Configure Stream with Google

```bash
python manage.py configure_risc \
    --service-account /home/dovydukas/service-account.json \
    --receiver-url https://api.dovydas.space/risc/receiver/
```

Expected output:
```
Getting access token...
Configuring RISC stream...
Receiver URL: https://api.dovydas.space/risc/receiver/
Status: enabled
Subscribed events: 7
Stream configured successfully!

RISC configuration completed!
```

### 3. Test with Verification Event

```bash
python manage.py configure_risc \
    --service-account /home/dovydukas/service-account.json \
    --receiver-url https://api.dovydas.space/risc/receiver/ \
    --verify-only
```

Expected output:
```
Getting access token...
Sending verification to: https://api.dovydas.space/risc/receiver/
Verification state: verify_1234567890
Verification event sent!
Check your receiver endpoint logs to confirm receipt
```

### 4. Check Logs for Verification Receipt

```bash
sudo journalctl -u homework-scraper.service -n 50 | grep -i risc
```

You should see something like:
```
Received verification event with state: verify_1234567890
```

## Nginx Configuration (if needed)

If using Nginx as reverse proxy, ensure RISC endpoint is accessible:

```nginx
# In your nginx config
location /risc/ {
    proxy_pass http://localhost:8000/risc/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Allow larger request bodies for JWT tokens
    client_max_body_size 10M;
}
```

Restart Nginx:
```bash
sudo systemctl restart nginx
```

## Testing the Receiver

### Test 1: Check Status Endpoint

```bash
curl https://api.dovydas.space/risc/status/
```

Expected response:
```json
{
  "configured": true,
  "enabled": true,
  "receiver_endpoint": "https://api.dovydas.space/risc/receiver/",
  "statistics": {
    "total_events": 1,
    "processed_events": 1,
    "failed_events": 0
  },
  "recent_events": [
    {
      "event_type": "verification",
      "google_email": "",
      "received_at": "2024-01-15T10:30:00Z",
      "processed": true,
      "action_taken": "Verification successful, state: verify_1234567890"
    }
  ],
  "subscribed_events": [...]
}
```

### Test 2: Send Manual Verification

From your development machine:

```bash
cd /path/to/homework-scraper
source venv/bin/activate  # If you have venv locally

python -c "
from risc.management.commands.configure_risc import Command
cmd = Command()
token = cmd.get_access_token('/path/to/service-account.json')
cmd.send_verification(token, 'https://api.dovydas.space/risc/receiver/')
"
```

## Monitoring

### Django Admin

Access at: `https://api.dovydas.space/admin/risc/`

Views available:
- **Security Events**: All received RISC events
- **RISC Configuration**: Stream configuration
- **User Security Actions**: Actions taken on user accounts

### Logs

Check logs in real-time:
```bash
# Service logs
sudo journalctl -u homework-scraper.service -f | grep -i risc

# All RISC activity
sudo journalctl -u homework-scraper.service --since "1 hour ago" | grep -i risc
```

### Database Queries

Check events in Django shell:

```python
from risc.models import SecurityEvent, UserSecurityAction

# Recent events
SecurityEvent.objects.order_by('-received_at')[:10]

# Failed events
SecurityEvent.objects.exclude(error_message='')

# Events for specific user
SecurityEvent.objects.filter(user=your_user)

# Security actions taken
UserSecurityAction.objects.order_by('-performed_at')[:10]
```

## Troubleshooting

### Error: "Unauthorized"

**Cause**: Invalid service account credentials

**Solution**:
1. Regenerate service account key in Google Cloud Console
2. Download new JSON file
3. Update `RISCConfiguration.service_account_file` path
4. Run configure_risc command again

### Error: "Forbidden"

**Cause**: Service account lacks RISC Configuration Admin role

**Solution**:
1. Go to IAM & Admin in Google Cloud Console
2. Find your service account
3. Edit permissions
4. Add "RISC Configuration Admin" role
5. Save and wait a few minutes

### Error: "Not Found"

**Cause**: RISC API not enabled

**Solution**:
1. Go to APIs & Services > Library
2. Search for "RISC" or "Cross-Account Protection"
3. Enable the API
4. Wait 5-10 minutes for propagation
5. Try again

### Events Not Being Received

**Check**:
1. Stream is enabled: `python manage.py configure_risc ...` (without --disable)
2. Receiver endpoint is HTTPS (required by Google)
3. Endpoint is publicly accessible (test with curl)
4. No firewall blocking Google IPs
5. Django service is running: `sudo systemctl status homework-scraper.service`

### User Not Found in Events

**Cause**: User mapping issue

**Solution**: Update `get_user_by_google_sub()` in `risc/services.py` to match your authentication setup.

If using django-allauth (default):
```python
from allauth.socialaccount.models import SocialAccount
social_account = SocialAccount.objects.get(provider='google', uid=google_sub)
user = social_account.user
```

If using custom User model:
```python
from myapp.models import UserProfile
profile = UserProfile.objects.get(google_sub=google_sub)
user = profile.user
```

## Production Checklist

Before going live:

- [ ] HTTPS enabled and working on receiver endpoint
- [ ] Service account created with proper role
- [ ] Service account JSON stored securely (not in git, proper file permissions)
- [ ] RISC added to INSTALLED_APPS
- [ ] RISC URLs added to main urls.py
- [ ] Migrations run: `python manage.py migrate risc`
- [ ] Configuration created in database
- [ ] Stream configured with Google
- [ ] Verification test successful
- [ ] Status endpoint returns correct data
- [ ] Django admin accessible for monitoring
- [ ] Logging configured and working
- [ ] Alerts set up for failed events (optional but recommended)
- [ ] Documentation shared with team

## Real-World Event Scenarios

### Scenario 1: Account Compromised

Google detects suspicious activity and disables the account.

**Event Received**: `account-disabled` with `reason: "hijacking"`

**Automatic Actions**:
1. All Django sessions revoked
2. Google Sign-In disabled
3. Security action logged
4. User notified (if you implement notifications)

### Scenario 2: Password Changed

User changes their Google password.

**Event Received**: `tokens-revoked`

**Automatic Actions**:
1. All OAuth tokens deleted
2. User must re-authenticate next time
3. Security action logged

### Scenario 3: Sessions Compromised

Google detects session hijacking across multiple devices.

**Event Received**: `sessions-revoked`

**Automatic Actions**:
1. All active Django sessions terminated
2. User logged out everywhere
3. Must log in again with fresh session

## Support

For issues specific to Google RISC:
- [Google RISC Documentation](https://developers.google.com/identity/protocols/risc)
- [OpenID RISC Specification](https://openid.net/specs/openid-risc-profile-specification-1_0.html)

For Django implementation issues:
- Check logs: `sudo journalctl -u homework-scraper.service -n 100 | grep -i risc`
- Check admin: `https://api.dovydas.space/admin/risc/`
- Test with verification event
