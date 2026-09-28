from django.contrib import admin
from .models import TimeLog, ActivityNote, SupervisorVerification

admin.site.register(TimeLog)
admin.site.register(ActivityNote)
admin.site.register(SupervisorVerification)
