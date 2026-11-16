from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import Profile


@login_required(login_url='login:login')
def profile_view(request):
    """
    Profile feature — view and edit the logged-in student's profile.
    Owns its own model (Profile) and its own form handling, syncing
    essential identity details (first name, last name, email) cleanly
    with Django's User model.
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user = request.user
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()

        # Update User identity fields
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if email:
            user.email = email
        user.save()

        # Update Profile fields
        combined_name = f"{user.first_name} {user.last_name}".strip()
        profile.full_name = combined_name or request.POST.get('full_name', '').strip()
        profile.bio = request.POST.get('bio', '').strip()

        if request.FILES.get('profile_image'):
            profile.profile_image = request.FILES['profile_image']

        profile.save()
        messages.success(request, 'Profile details updated successfully!')
        return redirect('profile:profile')

    return render(request, 'profile/profile.html', {'profile': profile})
