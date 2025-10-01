from django.db import models
from django.contrib.auth.models import User

class ScrapedHomework(models.Model):
    """Model to store scraped homework data"""
    SITE_CHOICES = [
        ('manodienynas', 'Manodienynas.lt'),
        ('eduka', 'Eduka.lt'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    site = models.CharField(max_length=20, choices=SITE_CHOICES)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    subject = models.CharField(max_length=200, blank=True)
    url = models.URLField(max_length=1000, blank=True)
    scraped_at = models.DateTimeField(auto_now_add=True)
    synced_to_google_tasks = models.BooleanField(default=False)
    google_task_id = models.CharField(max_length=200, blank=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['due_date', '-scraped_at']
        unique_together = ['user', 'site', 'title', 'due_date']
    
    def __str__(self):
        return f"{self.title} - {self.site}"

class UserScrapingPreferences(models.Model):
    """User preferences for scraping"""
    GOOGLE_TASKS_TITLE_CHOICES = [
        ('title', 'Task Title'),
        ('subject', 'Subject Name'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    enable_manodienynas = models.BooleanField(default=True)
    enable_eduka = models.BooleanField(default=True)
    auto_sync_to_google_tasks = models.BooleanField(default=True)
    scraping_frequency_hours = models.PositiveIntegerField(default=6)  # Every 6 hours
    last_scraped_manodienynas = models.DateTimeField(null=True, blank=True)
    last_scraped_eduka = models.DateTimeField(null=True, blank=True)
    google_tasks_title_format = models.CharField(
        max_length=20,
        choices=GOOGLE_TASKS_TITLE_CHOICES,
        default='title',
        help_text='What to display in Google Tasks header: task title or subject name'
    )
    
    def __str__(self):
        return f"Preferences for {self.user.username}"
