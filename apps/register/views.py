from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from apps.user_profile.models import Profile
from apps.user_settings.models import UserSettings


def register_view(request):
    """
    Register feature — creates a new student account. Owns its own
    validation (username uniqueness, password confirmation) rather than
    borrowing Login's or Home's logic.
    """
    if request.user.is_authenticated:
        return redirect('home:home')

    context = {}

    if request.method == 'POST':
        last_name = request.POST.get('last_name', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        context = {
            'last_name': last_name,
            'first_name': first_name,
            'username': username,
            'email': email,
        }

        errors = []
        if not last_name:
            errors.append('Last name is required.')
        if not first_name:
            errors.append('First name is required.')
        if not username:
            errors.append('Username is required.')
        elif User.objects.filter(username=username).exists():
            errors.append('That username is already taken.')
        if not email:
            errors.append('School email is required.')
        if not password or len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        elif password != password_confirm:
            errors.append('Passwords do not match.')

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'register/register.html', context)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Initialize student Profile and Settings upon creation
        full_name = f"{first_name} {last_name}".strip()
        Profile.objects.get_or_create(user=user, defaults={'full_name': full_name})
        UserSettings.objects.get_or_create(user=user, defaults={'dark_mode': False, 'email_notifications': True})

        auth_login(request, user)
        messages.success(request, f"Welcome to LogMyOJT, {first_name}! Your student account is ready.")
        return redirect('home:home')

    return render(request, 'register/register.html', context)
