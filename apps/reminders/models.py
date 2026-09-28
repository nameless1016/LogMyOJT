from django.contrib.auth.models import User
from django.db import models


class Reminder(models.Model):
    """REMINDER — reminders and pace alerts sent to a student."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=50)  # e.g. 'daily_reminder', 'pace_alert'
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reminder'

    def __str__(self):
        return f"{self.reminder_type} for {self.user.username}"
