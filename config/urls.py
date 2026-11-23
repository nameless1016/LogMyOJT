from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from apps.user_profile.views import protected_media_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', include('apps.login.urls')),
    path('register/', include('apps.register.urls')),
    path('profile/', include('apps.user_profile.urls')),
    path('settings/', include('apps.user_settings.urls')),
    path('', include('apps.home.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Serve media via protected view with traversal checks in production environments without S3/Supabase Storage
    media_url_prefix = settings.MEDIA_URL.lstrip('/')
    urlpatterns += [
        re_path(rf'^{media_url_prefix}(?P<path>.*)$', protected_media_view, name='protected_media'),
    ]
