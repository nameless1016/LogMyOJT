from django.contrib.auth import authenticate, login
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
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home:home')
        return render(request, 'login/login.html', {
            'error': 'Invalid username or password.',
            'username': username,
        })

    return render(request, 'login/login.html')
