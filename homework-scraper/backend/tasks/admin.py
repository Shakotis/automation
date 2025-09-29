from django.contrib import admin
from .models import GoogleTaskList

@admin.register(GoogleTaskList)
class GoogleTaskListAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'google_task_list_id', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'user__email', 'google_task_list_id']
    readonly_fields = ['google_task_list_id', 'created_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')
