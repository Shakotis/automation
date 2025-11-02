# RAM Optimization Summary

**Date:** November 2, 2025  
**Initial RAM Usage:** 514MB / 906MB (56.7% used)  
**Optimizations Applied**

## 1. Schedule Scraper Memory Optimization (`schedule_scraper.py`)

### Changes Made:
- ✅ Added `import gc` for explicit garbage collection
- ✅ Added `session.close()` after scraping to free HTTP session memory
- ✅ Added `img.close()` after saving PNG to free PIL image memory
- ✅ Added `gc.collect()` calls after cleanup operations
- ✅ Fixed `strftime()` formatting (removed extra spaces)
- ✅ Added `optimize=True` to PNG save for better compression
- ✅ Removed minimum 6-period constraint (only show actual lessons)

### Memory Impact:
- Images are now properly closed, preventing memory leaks
- PNG files are compressed better (reduced from 101K to 79K)
- Sessions are properly cleaned up after each scrape

---

## 2. Gunicorn Service Optimization

### Old Configuration:
```ini
--workers 1
--timeout 600
--max-requests 1000
--max-requests-jitter 50
--worker-class sync
--log-level info
MemoryMax=600M
MemoryHigh=500M
```

### New Configuration:
```ini
--workers 1
--threads 2
--timeout 600
--max-requests 500           # Reduced from 1000
--max-requests-jitter 50
--worker-class gthread       # Changed from sync
--worker-tmp-dir /dev/shm    # Use RAM for temp files
--log-level warning          # Reduced logging
MemoryMax=400M               # Reduced from 600M
MemoryHigh=350M              # Reduced from 500M
CPUQuota=80%                 # NEW: CPU limit
```

### Memory Impact:
- Worker restarts more frequently (500 requests vs 1000)
- Using gthread for better concurrency with less memory
- Temp files in RAM (/dev/shm) for faster I/O
- Less logging = less memory for log buffers
- Stricter memory limits enforce better cleanup

---

## 3. Celery Worker Optimization

### Old Configuration:
```ini
ExecStart=celery -A homework_scraper worker -l info
# No memory limits
```

### New Configuration:
```ini
ExecStart=celery -A homework_scraper worker \
    --loglevel=warning                    # Reduced logging
    --concurrency=1                       # Single worker process
    --max-tasks-per-child=100            # NEW: Restart after 100 tasks
    --max-memory-per-child=200000        # NEW: Restart if >200MB
    --time-limit=300                     # NEW: Kill long-running tasks
    --soft-time-limit=270                # NEW: Soft timeout warning
MemoryMax=250M                           # NEW: Hard memory limit
MemoryHigh=200M                          # NEW: Memory pressure threshold
CPUQuota=50%                             # NEW: CPU limit
```

### Memory Impact:
- Worker automatically restarts after 100 tasks (prevents memory leaks)
- Worker kills itself if memory exceeds 200MB
- Systemd enforces 250MB hard limit
- Tasks are killed if they run too long

---

## 4. Celery Beat Optimization

### Old Configuration:
```ini
ExecStart=celery -A homework_scraper beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
# No memory limits
```

### New Configuration:
```ini
ExecStart=celery -A homework_scraper beat \
    --loglevel=warning                   # Reduced logging
    --scheduler django_celery_beat.schedulers:DatabaseScheduler
MemoryMax=150M                           # NEW: Hard memory limit
MemoryHigh=120M                          # NEW: Memory pressure threshold
CPUQuota=30%                             # NEW: CPU limit
```

### Memory Impact:
- Beat scheduler limited to 150MB maximum
- Less logging reduces memory usage

---

## 5. Code Cleanup

### Removed:
- ✅ Deleted unused `server-files/` directory (empty duplicate code)

### Created:
- ✅ `scraper/cleanup_old_schedules.py` - Script to delete schedule images older than 7 days

---

## 6. Django Settings Verification

- ✅ Confirmed `DEBUG=False` in production (`.env` file)
- Less memory for debug toolbar and verbose logging

---

## Memory Limits Summary

| Service | Old Limit | New Limit | Reduction |
|---------|-----------|-----------|-----------|
| Gunicorn | 600M | 400M | -33% |
| Celery Worker | None | 250M | NEW |
| Celery Beat | None | 150M | NEW |
| **Total** | 600M+ | 800M | Enforced |

---

## Recommendations for Further Optimization

1. **Database Query Optimization**
   - Review N+1 queries in schedule scraping
   - Add database query logging in development
   - Use `select_related()` and `prefetch_related()`

2. **Redis Configuration**
   - Set `maxmemory` policy in Redis
   - Configure `maxmemory-policy volatile-lru`

3. **Monitoring**
   - Set up memory alerts at 80% usage
   - Monitor swap usage (currently 563MB/905MB)
   - Track process restarts from memory limits

4. **Future Tasks**
   - Consider using a lightweight job queue instead of Celery
   - Cache schedule images to avoid regeneration
   - Implement incremental schedule updates

---

## How to Monitor

### Check memory usage:
```bash
free -h
```

### Check process memory:
```bash
ps aux --sort=-%mem | head -15
```

### Check service status:
```bash
sudo systemctl status homework-scraper.service
sudo systemctl status homework-scraper-celery.service
sudo systemctl status homework-scraper-celery-beat.service
```

### Run manual cleanup:
```bash
cd /home/dovydukas/homework-scraper-backend
source venv/bin/activate
python scraper/cleanup_old_schedules.py
```

---

**Optimization Complete! ✅**  
All services restarted with new configurations.
