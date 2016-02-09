from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from loader.forms import FileForm
from loader.models import File

def login_to_app(request):
    """
    Login is required to access the main pages.

    The login screen passes data through to here where we can validate and then redirect.

    Currently we redirect to the 'Create Session' page.

    :param request: HTTP request object
    :return: redirect
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('loader:load_file')
    # If we have reached here, the user has not registered as logged in.
    return redirect('django.contrib.auth.views.login')

def load_file(request):
    if not request.user.is_authenticated():
        return redirect('django.contrib.auth.views.login')

    form = FileForm()
    return render(request, 'loader.html', {'form':form})
