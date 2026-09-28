from django.contrib.auth.models import User
from django.db import models


class OJTPlacement(models.Model):
    """OJT_PLACEMENT — where a student does their OJT and how many hours are required."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='placements')
    company_name = models.CharField(max_length=150)
    company_address = models.CharField(max_length=255)
    supervisor_name = models.CharField(max_length=150)
    supervisor_email = models.EmailField(max_length=254)
    supervisor_phone = models.CharField(max_length=20, blank=True)
    required_hours = models.DecimalField(max_digits=6, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ojt_placement'

    def __str__(self):
        return f"{self.user.username} @ {self.company_name}"
