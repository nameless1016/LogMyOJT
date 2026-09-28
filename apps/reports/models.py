from django.db import models


class Report(models.Model):
    """REPORT — a generated PDF report of logged hours for a placement."""
    placement = models.ForeignKey('placement.OJTPlacement', on_delete=models.CASCADE, related_name='reports')
    generated_at = models.DateTimeField(auto_now_add=True)
    file_path = models.CharField(max_length=255)
    total_hours_included = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        db_table = 'report'

    def __str__(self):
        return f"Report {self.generated_at:%Y-%m-%d} for {self.placement}"


class ProgressSummary(models.Model):
    """PROGRESS_SUMMARY — weekly/monthly hour totals for a placement."""
    PERIOD_CHOICES = [
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
    ]

    placement = models.ForeignKey('placement.OJTPlacement', on_delete=models.CASCADE, related_name='progress_summaries')
    period_type = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    period_start = models.DateField()
    period_end = models.DateField()
    total_hours = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        db_table = 'progress_summary'

    def __str__(self):
        return f"{self.period_type} {self.period_start} – {self.period_end}"
