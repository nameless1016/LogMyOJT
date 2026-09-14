from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

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
