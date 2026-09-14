from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import UserSettings


@login_required(login_url='login:login')
def settings_view(request):
    """
    Settings feature — view and update the logged-in student's
    preferences. Owns its own model (UserSettings).
    """
    settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        settings_obj.dark_mode = request.POST.get('dark_mode') == 'on'
        settings_obj.email_notifications = request.POST.get('email_notifications') == 'on'
        settings_obj.save()
        return redirect('user_settings:settings')

    return render(request, 'user_settings/settings.html', {'settings_obj': settings_obj})
