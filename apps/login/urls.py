from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import login_view

app_name = 'login'

urlpatterns = [
    path('', login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login:login'), name='logout'),
]
