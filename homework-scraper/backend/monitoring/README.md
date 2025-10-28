"""
Monitoring Django App

This app provides API endpoints for monitoring server status, logs, and services.

Features:
- System status (CPU, memory, disk, uptime)
- Service status monitoring
- Application log viewing
- Error tracking
- Process information

All endpoints require authentication for security.

Usage:
- Add 'monitoring' to INSTALLED_APPS in settings.py
- Include monitoring.urls in main urls.py
- Ensure proper log file permissions
- Access via /api/monitoring/ endpoints

API Endpoints:
- GET /api/monitoring/ - API information
- GET /api/monitoring/system-status/ - System information
- GET /api/monitoring/services/ - Service status
- GET /api/monitoring/logs/ - Application logs
- GET /api/monitoring/errors/ - Recent errors
- GET /api/monitoring/processes/ - Running processes
"""
