from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url='login:login')
def home_view(request):
    """
    Home feature — the main authenticated landing screen.
    Reads Profile data if it exists, but does not own or duplicate
    Profile's model/logic (kept in the user_profile feature).
    """
    profile = getattr(request.user, 'profile', None)
    return render(request, 'home/home.html', {'profile': profile})
