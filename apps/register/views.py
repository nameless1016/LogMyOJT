from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from apps.user_profile.models import Profile
from apps.user_settings.models import UserSettings
from .forms import RegistrationForm


def register_view(request):
    """
    Register feature — creates a new student account using Django Form
    with strict validation (unique email, unique username, strong password).
    Initializes profile and user settings upon successful creation.
    """
    if request.user.is_authenticated:
        return redirect('home:home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data
            user = User.objects.create_user(
                username=cleaned['username'],
                email=cleaned['email'],
                password=cleaned['password'],
                first_name=cleaned['first_name'],
                last_name=cleaned['last_name'],
            )

            # Initialize student Profile and Settings upon creation
            full_name = f"{cleaned['first_name']} {cleaned['last_name']}".strip()
            Profile.objects.get_or_create(user=user, defaults={'full_name': full_name})
            UserSettings.objects.get_or_create(user=user, defaults={'dark_mode': False, 'email_notifications': True})

            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f"Welcome to LogMyOJT, {cleaned['first_name']}! Your student account is ready.")
            return redirect('home:home')
    else:
        form = RegistrationForm()

    return render(request, 'register/register.html', {'form': form})
