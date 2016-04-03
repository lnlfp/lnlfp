import codecs
import csv

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Lower
from django.shortcuts import render, redirect

from loader.forms import FileForm
from loader.models import File, Feed, Column, Procedure

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

    Also handles files and returns the view_file view on POST.

    :param request: HTTP request holding the user.
    :return: render: the loader template.
    """
    if not request.user.is_authenticated():
        return redirect('django.contrib.auth.views.login')

    if request.method == 'POST':
        # Call robs function
        form = FileForm(request.user, request.POST, request.FILES)

        if form.is_valid():
            new_upload = File(**form.cleaned_data)
            new_upload.save()

            return redirect('loader:view_file', new_upload.pk)

    else:
        form = FileForm(request.user)

    return render(request, 'loader.html', {'form': form, 'user': request.user})


def view_file(request, file_pk):
    """

    :param request: HTTP request.
    :param file_pk: pk of the file we need to load into the view.
    :return:
    """
    file_to_load = File.objects.get(pk=file_pk)

    special_cols = Column.objects.all().order_by(Lower('name'))

    data_file = file_to_load.data.file
    reader = csv.reader(codecs.iterdecode(data_file, 'utf-8'), delimiter=file_to_load.delimiter)
    data = []

    row_num = 0

    if file_to_load.has_header:
        header = next(reader)
        no_cols = len(header)
    else:
        header = None
        data.append(next(reader))
        row_num += 1
        no_cols = len(data[0])

    choices = ""
    for col in special_cols:
        choices += '<option value="{pk}">{name}</option>\n'.format(pk=col.pk, name=col.name)

    template_choice = """
<select class="form-control" name="col_select_{col_name}">
    <option value selected disabled>Special Column</option>
    <option value="None">None</option>
    {choices}
</select>"""

    column_choice_row = []
    for idx in range(no_cols):
        if header:
            column_choice_row.append(template_choice.format(col_name=header[idx], choices=choices))

    for row in reader:
        data.append(row)
        row_num += 1
        if row_num >= 10:
            break

    procedures = Procedure.objects.all()

    return render(request, 'table.html', {'data': data,
                                          'column_choice': column_choice_row,
                                          'columns': special_cols,
                                          'header': header,
                                          'procedures': procedures})