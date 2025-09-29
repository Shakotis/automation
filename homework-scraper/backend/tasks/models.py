from django.db import models
from django.contrib.auth.models import User

class GoogleTaskList(models.Model):
    """Store Google Task Lists for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    google_task_list_id = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'google_task_list_id']
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
