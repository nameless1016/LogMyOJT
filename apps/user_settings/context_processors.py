def dark_mode(request):
    """
    Exposes `is_dark_mode` to all templates so any authenticated page
    (Home, Profile, Settings) seamlessly inherits the user's theme.
    """
    if request.user.is_authenticated:
        settings_obj = getattr(request.user, 'settings', None)
        if settings_obj is not None:
            return {'is_dark_mode': settings_obj.dark_mode}
        try:
            from .models import UserSettings
            settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
            return {'is_dark_mode': settings_obj.dark_mode}
        except Exception:
            return {'is_dark_mode': False}
    return {'is_dark_mode': False}
