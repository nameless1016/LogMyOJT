from django.db import models


class TimeLog(models.Model):
    """TIME_LOG — one row per day the student logs time in/out for a placement."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    placement = models.ForeignKey('placement.OJTPlacement', on_delete=models.CASCADE, related_name='time_logs')
    log_date = models.DateField()
    time_in = models.TimeField()
    time_out = models.TimeField(null=True, blank=True)
    hours_computed = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'time_log'

    def __str__(self):
        return f"{self.placement.user.username} — {self.log_date}"


class ActivityNote(models.Model):
    """ACTIVITY_NOTE — what the student did that day (1:1 with a time log entry)."""
    time_log = models.OneToOneField(TimeLog, on_delete=models.CASCADE, related_name='activity_note')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'activity_note'

    def __str__(self):
        return f"Note for {self.time_log}"


class SupervisorVerification(models.Model):
    """SUPERVISOR_VERIFICATION — digital approval of a time log entry (1:1)."""
    time_log = models.OneToOneField(TimeLog, on_delete=models.CASCADE, related_name='verification')
    verification_code = models.CharField(max_length=50, unique=True)
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'supervisor_verification'

    def __str__(self):
        return f"Verification for {self.time_log}"
