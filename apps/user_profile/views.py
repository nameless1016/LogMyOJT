import os
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import render, redirect

from .forms import ProfileForm
from .models import Profile


@login_required(login_url='login:login')
def profile_view(request):
    """
    Profile feature — view and edit the logged-in student's profile.
    Owns its own model (Profile) and form handling with strict validation
    for email uniqueness, image type/size checks, and sanitization.
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        old_image = profile.profile_image
        form = ProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            # If user uploaded a new image, delete the old file from disk
            if request.FILES.get('profile_image') and old_image:
                try:
                    if old_image.storage.exists(old_image.name):
                        old_image.storage.delete(old_image.name)
                except Exception:
                    pass

            form.save()
            messages.success(request, 'Profile details updated successfully!')
            return redirect('profile:profile')
    else:
        form = ProfileForm(instance=profile, user=request.user)

    return render(request, 'profile/profile.html', {
        'profile': profile,
        'form': form,
    })


def protected_media_view(request, path):
    """
    Safely serves user-uploaded media files with strict path traversal protection.
    Used when DEBUG is False in non-S3/Supabase storage setups.
    """
    if not settings.MEDIA_ROOT:
        raise Http404("Media storage not configured")

    media_root = os.path.abspath(str(settings.MEDIA_ROOT))
    full_path = os.path.abspath(os.path.join(media_root, path))

    # Path traversal guard
    if not full_path.startswith(media_root) or not os.path.exists(full_path) or os.path.isdir(full_path):
        raise Http404("File not found")

    return FileResponse(open(full_path, 'rb'))
