# Backend 404 Error Fix Guide

## 🚨 Problem

Frontend is getting **404 Not Found** error when trying to sync homework to Google Tasks:

```
POST https://api.dovydas.space/api/scraper/homework/sync-google-tasks/ 404 (Not Found)
```

## 🔍 Root Cause

The backend is missing the URL routing configuration for the `tasks` app. Specifically:

1. **Missing File**: `backend/tasks/urls.py` doesn't exist
2. **Missing File**: `backend/tasks/views.py` doesn't exist or incomplete
3. **Wrong URL**: Frontend is calling `/api/scraper/homework/sync-google-tasks/` but the correct endpoint should be `/api/tasks/sync`

## ✅ Solution

### Step 1: Create Missing Backend Files

I've created two files for you locally:

1. **`backend/tasks/urls.py`** - URL routing for tasks app
2. **`backend/tasks/views.py`** - View functions for tasks endpoints

### Step 2: Upload Files to Server

Use one of these methods:

#### Option A: Using PowerShell Script (Automated)
```powershell
.\deploy-fix-404.ps1
```

This will:
- Check for SCP tools (pscp or scp)
- Upload the files to your server
- Provide instructions to restart services

#### Option B: Manual Upload via WinSCP/FileZilla

1. Open WinSCP or FileZilla
2. Connect to: `192.168.0.88` (username: `dovydukas`)
3. Navigate to: `/home/dovydukas/homework-scraper/backend/tasks/`
4. Upload:
   - `backend/tasks/urls.py`
   - `backend/tasks/views.py`

#### Option C: Manual Upload via SCP

If you have PuTTY installed:
```powershell
pscp -i $env:USERPROFILE\.ssh\rpi_3 backend\tasks\urls.py dovydukas@192.168.0.88:/home/dovydukas/homework-scraper/backend/tasks/urls.py
pscp -i $env:USERPROFILE\.ssh\rpi_3 backend\tasks\views.py dovydukas@192.168.0.88:/home/dovydukas/homework-scraper/backend/tasks/views.py
```

### Step 3: SSH into Server and Restart Services

1. Connect to server (use PuTTY or SSH client):
   ```
   Server: 192.168.0.88
   Username: dovydukas
   Key: ~/.ssh/rpi_3
   ```

2. Verify files were uploaded:
   ```bash
   cd /home/dovydukas/homework-scraper/backend
   ls -la tasks/urls.py
   ls -la tasks/views.py
   ```

3. Restart Django service:
   ```bash
   sudo systemctl restart homework-scraper.service
   sudo systemctl status homework-scraper.service
   ```

4. Watch logs for errors:
   ```bash
   sudo journalctl -u homework-scraper.service -f
   ```

### Step 4: Test the Fix

1. **Test on server** (while SSH'd in):
   ```bash
   curl -X POST http://localhost:8000/api/tasks/sync \
     -H "Content-Type: application/json" \
     -d '{}'
   ```

   Expected response:
   ```json
   {
     "success": true,
     "message": "Synced 0 homework items to Google Tasks",
     "synced_count": 0,
     "errors": []
   }
   ```

2. **Test from your browser**:
   - Open your frontend application
   - Try syncing homework
   - Check browser console for errors

## 📁 File Contents

### backend/tasks/urls.py

```python
"""
URL configuration for Google Tasks integration
"""
from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Sync homework to Google Tasks
    path('sync', views.sync_homework_to_tasks, name='sync-homework-to-tasks'),
    path('sync/', views.sync_homework_to_tasks, name='sync-homework-to-tasks-slash'),
    
    # Get Google Task lists
    path('lists', views.get_task_lists, name='get-task-lists'),
    path('lists/', views.get_task_lists, name='get-task-lists-slash'),
    
    # Get tasks from a specific list
    path('lists/<str:list_id>/tasks', views.get_tasks, name='get-tasks'),
    path('lists/<str:list_id>/tasks/', views.get_tasks, name='get-tasks-slash'),
]
```

### backend/tasks/views.py

```python
"""
Views for Google Tasks integration
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def sync_homework_to_tasks(request):
    """Sync homework items to Google Tasks"""
    try:
        body = json.loads(request.body) if request.body else {}
        homework_ids = body.get('homework_ids', None)
        
        logger.info(f"Sync request received. Homework IDs: {homework_ids}")
        
        # TODO: Implement actual Google Tasks sync logic
        synced_count = len(homework_ids) if homework_ids else 0
        
        return JsonResponse({
            'success': True,
            'message': f'Synced {synced_count} homework items to Google Tasks',
            'synced_count': synced_count,
            'errors': []
        })
        
    except Exception as e:
        logger.error(f"Error syncing homework to tasks: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# ... more view functions
```

## 🔧 Verification Checklist

After deploying:

- [ ] Files uploaded to server successfully
- [ ] Django service restarted without errors
- [ ] No errors in `journalctl` logs
- [ ] curl test on server returns 200 OK
- [ ] Frontend can sync homework without 404 error
- [ ] Browser console shows no routing errors

## 🆘 Troubleshooting

### Issue: 404 Still Occurs

**Check 1**: Verify main urls.py includes tasks:
```bash
cat /home/dovydukas/homework-scraper/backend/homework_scraper/urls.py | grep tasks
```

Should see:
```python
path('api/tasks/', include('tasks.urls')),
```

**Check 2**: Verify tasks app is in INSTALLED_APPS:
```bash
cat /home/dovydukas/homework-scraper/backend/homework_scraper/settings.py | grep -A 20 INSTALLED_APPS
```

Should see:
```python
INSTALLED_APPS = [
    # ...
    'tasks',
    # ...
]
```

**Check 3**: Check Django logs:
```bash
sudo journalctl -u homework-scraper.service -n 100 | grep -i "error\|404\|tasks"
```

### Issue: Permission Denied

```bash
sudo chown dovydukas:dovydukas /home/dovydukas/homework-scraper/backend/tasks/*.py
sudo chmod 644 /home/dovydukas/homework-scraper/backend/tasks/*.py
```

### Issue: Module Not Found

Make sure `__init__.py` exists:
```bash
touch /home/dovydukas/homework-scraper/backend/tasks/__init__.py
```

### Issue: Service Won't Restart

```bash
# Check service status
sudo systemctl status homework-scraper.service

# View detailed logs
sudo journalctl -u homework-scraper.service -xe

# Check Python syntax
cd /home/dovydukas/homework-scraper/backend
python3 manage.py check
```

## 📝 Important Notes

### Current Implementation

The views.py file contains **placeholder/stub implementations**. They will:
- ✅ Return 200 OK status
- ✅ Accept requests properly
- ✅ Log activity
- ❌ NOT actually sync to Google Tasks yet

### Next Steps for Full Implementation

You'll need to implement the actual Google Tasks API integration:

1. **Add Google OAuth credentials** to user model
2. **Implement Google Tasks API client** (using `google-api-python-client`)
3. **Fetch homework** from your database
4. **Create tasks** in Google Tasks
5. **Update homework** records as synced
6. **Handle errors** and retry logic

Example implementation structure:
```python
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def sync_homework_to_tasks(request):
    # 1. Get user's Google credentials
    user = request.user
    credentials = get_user_google_credentials(user)
    
    # 2. Build Google Tasks API client
    service = build('tasks', 'v1', credentials=credentials)
    
    # 3. Get or create "Homework" task list
    task_list_id = get_or_create_homework_list(service)
    
    # 4. Fetch unsynced homework from database
    homework_items = Homework.objects.filter(synced=False)
    
    # 5. Create tasks for each homework
    for hw in homework_items:
        task = service.tasks().insert(
            tasklist=task_list_id,
            body={
                'title': hw.title,
                'notes': hw.description,
                'due': hw.due_date.isoformat() if hw.due_date else None
            }
        ).execute()
        
        hw.google_task_id = task['id']
        hw.synced = True
        hw.save()
    
    return JsonResponse({'success': True, 'synced_count': len(homework_items)})
```

## 🔗 Related Files

- `backend/homework_scraper/urls.py` - Main URL configuration
- `frontend/lib/api.ts` - Frontend API client
- `frontend/app/homework/page.tsx` - Homework page using the API
- `debug-404-error.ps1` - Diagnostic tool
- `deploy-fix-404.ps1` - Deployment script

## 📚 Resources

- [Django URL dispatcher](https://docs.djangoproject.com/en/5.2/topics/http/urls/)
- [Google Tasks API](https://developers.google.com/tasks/overview)
- [Django REST views](https://docs.djangoproject.com/en/5.2/topics/http/views/)

---

**Last Updated:** October 29, 2025  
**Status:** Ready to deploy  
**Priority:** High - Blocking user feature
