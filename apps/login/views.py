from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST


def login_view(request):
    """
    Login feature — authenticates an existing student against Django auth
    and django-axes rate limiting. Supports safe redirect (?next=).
    """
    if request.user.is_authenticated:
        return redirect('home:home')

    next_url = request.POST.get('next') or request.GET.get('next') or ''

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            display_name = user.first_name if user.first_name else user.username
            messages.success(request, f"Welcome back, {display_name}!")
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('home:home')
        messages.error(request, 'Invalid username or password. Please verify your credentials and try again.')
        return render(request, 'login/login.html', {
            'username': username,
            'next': next_url,
        })

    return render(request, 'login/login.html', {
        'next': next_url,
    })


@require_POST
def logout_view(request):
    """
    Logout feature — signs the user out via POST only, sets an info
    flash message, and returns to the sign-in screen.
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login:login')


def lockout_view(request, credentials=None):
    """
    Lockout callback invoked by django-axes when consecutive failure limit is exceeded.
    """
    return render(request, 'login/lockout.html', status=429)
