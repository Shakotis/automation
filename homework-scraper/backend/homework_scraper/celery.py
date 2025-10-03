"""
Celery configuration for homework_scraper project.
Supports both local development and production server deployment.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homework_scraper.settings')

app = Celery('homework_scraper')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure Celery Beat schedule
# This schedule will scrape homework for ALL users in the system automatically
app.conf.beat_schedule = {
    # Morning schedule: Every 2 hours from 9am to 1pm
    'scrape-homework-morning-1': {
        'task': 'scraper.tasks.scrape_all_homework',
        'schedule': crontab(hour='9', minute='0'),
        'options': {'expires': 3600},  # Expire after 1 hour if not run
    },
    'scrape-homework-morning-2': {
        'task': 'scraper.tasks.scrape_all_homework',
        'schedule': crontab(hour='11', minute='0'),
        'options': {'expires': 3600},
    },
    # Afternoon schedule: Every hour from 1pm to 4pm
    'scrape-homework-afternoon-1': {
        'task': 'scraper.tasks.scrape_all_homework',
        'schedule': crontab(hour='13', minute='0'),
        'options': {'expires': 3600},
    },
    'scrape-homework-afternoon-2': {
        'task': 'scraper.tasks.scrape_all_homework',
        'schedule': crontab(hour='14', minute='0'),
        'options': {'expires': 3600},
    },
    'scrape-homework-afternoon-3': {
        'task': 'scraper.tasks.scrape_all_homework',
        'schedule': crontab(hour='15', minute='0'),
        'options': {'expires': 3600},
    },
    'scrape-homework-afternoon-4': {
        'task': 'scraper.tasks.scrape_all_homework',
        'schedule': crontab(hour='16', minute='0'),
        'options': {'expires': 3600},
    },
}

# Set timezone - Lithuanian timezone
app.conf.timezone = 'Europe/Vilnius'

# Additional production-ready settings
app.conf.update(
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    
    # Task execution settings
    task_acks_late=True,  # Task acknowledged after execution, not before
    task_reject_on_worker_lost=True,  # Reject task if worker dies
    
    # Retry settings
    task_default_retry_delay=300,  # Retry after 5 minutes
    task_max_retries=3,  # Maximum 3 retries
    
    # Worker settings
    worker_prefetch_multiplier=4,  # Number of tasks to prefetch
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks (memory management)
    
    # Beat settings (for server deployment with django-celery-beat)
    beat_scheduler='django_celery_beat.schedulers:DatabaseScheduler',
)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to test Celery is working"""
    print(f'Request: {self.request!r}')

