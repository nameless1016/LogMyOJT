from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect


def login_view(request):
    """
    Login feature — authenticates an existing user against Django's
    built-in auth backend. This feature owns only sign-in behavior;
    it does not know how accounts get created (that's Register's job).
    """
    if request.user.is_authenticated:
        return redirect('home:home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            display_name = user.first_name if user.first_name else user.username
            messages.success(request, f"Welcome back, {display_name}!")
            return redirect('home:home')
        messages.error(request, 'Invalid username or password. Please verify your credentials and try again.')
        return render(request, 'login/login.html', {
            'username': username,
        })

    return render(request, 'login/login.html')


def logout_view(request):
    """
    Logout feature — signs the user out, sets an info flash message,
    and returns them to the sign-in screen.
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login:login')
