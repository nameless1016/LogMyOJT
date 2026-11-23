from django.urls import path
from . import views

app_name = 'time_log'

urlpatterns = [
    path('', views.log_history, name='history'),
    path('insights/', views.insights, name='insights'),
]
