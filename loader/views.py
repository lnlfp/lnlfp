import csv

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from loader.forms import FileForm
from loader.models import File, Feed

def login_to_app(request):
    """
    Login is required to access the main pages.

    The login screen passes data through to here where we can validate and then redirect.

    Currently we redirect to the 'Create Session' page.

    :param request: HTTP request object
    :return: redirect to the load_file window.
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


def logout_of_app(request):
    """
    Basic view to logout a user. Redirects to the login screen.

    :param request: HTTP Request containing the user.
    :return: redirect to login page.
    """
    logout(request)
    return redirect('loader:login_to_app')


def load_file(request):
    """
    Basic view holding the details for a file browsing screen pre-upload.

    :param request: HTTP request holding the user.
    :return: render: the loader template.
    """
    if not request.user.is_authenticated():
        return redirect('django.contrib.auth.views.login')

    if request.method == 'POST':
        print(dir(request.FILES['data']))
        print(request.FILES['data'].name)
        new_upload = File(data=request.FILES['data'],
                          file_name=request.FILES['data'].name,
                          user=request.user,
                          feed=Feed.objects.get(pk=request.POST['feed']))
        new_upload.save()

    form = FileForm()
    return render(request, 'loader.html', {'form':form})

def view_file(request, file):
    with open(file.data, 'r') as data_file:
        reader = csv.reader(data_file, delimiter=file.delimiter)
        data = []

        row_num = 0

        for row in reader:
            data.append(row)
            row_num += 1
            if row_num >= 10:
                break

    return render(request, 'table.html', {'data': data})
