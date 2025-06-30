from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model # Best practice to get the User model

User = get_user_model() # Get the currently active User model

class Task(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    # CHANGE THIS LINE:
    shared_with = models.ManyToManyField(User, related_name='shared_tasks_m2m', blank=True) # Renamed related_name to avoid conflict if you had a separate one

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    priority = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-priority', 'created_at']

    def __str__(self):
        return self.title