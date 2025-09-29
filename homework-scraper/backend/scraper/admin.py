from django.contrib import admin
from .models import ScrapedHomework, UserScrapingPreferences

@admin.register(ScrapedHomework)
class ScrapedHomeworkAdmin(admin.ModelAdmin):
    list_display = ['title', 'site', 'subject', 'user', 'due_date', 'synced_to_google_tasks', 'scraped_at']
    list_filter = ['site', 'synced_to_google_tasks', 'scraped_at', 'due_date']
    search_fields = ['title', 'description', 'subject', 'user__email']
    ordering = ['-scraped_at']
    readonly_fields = ['scraped_at', 'google_task_id']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')

@admin.register(UserScrapingPreferences)
class UserScrapingPreferencesAdmin(admin.ModelAdmin):
    list_display = ['user', 'enable_manodienynas', 'enable_eduka', 'auto_sync_to_google_tasks', 'scraping_frequency_hours']
    list_filter = ['enable_manodienynas', 'enable_eduka', 'auto_sync_to_google_tasks']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')
