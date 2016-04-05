import codecs
import csv

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models.functions import Lower
from django.shortcuts import render, redirect, Http404
from django.views.generic import View, ListView, CreateView, UpdateView
from loader.forms import FileForm
from loader.models import File, Column, Procedure, Feed


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

                if request.POST.get('next'):
                    return redirect(request.POST.get('next', 'loader:user_home'))
                else:
                    return redirect('loader:user_home')

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


class UserHomeView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        """
        Build up the user home page.

        :param request: HTTP request holding the user.
        :return: render: the home page template.
        """
        context = {}

        return render(request, 'home.html', context)


class FileListView(LoginRequiredMixin, ListView):
    """
    Allow a user to view the feeds they have access to.
    """
    model = Feed
    context_object_name = 'user_files'
    template_name = 'files.html'

    def get_queryset(self):
        """
        Limit the feeds to the logged in user
        :return: QuerySet, the feeds the user has access to.
        """
        return self.request.user.file_set.all()


class FeedListView(LoginRequiredMixin, ListView):
    """
    Allow a user to view the feeds they have access to.
    """
    model = Feed
    context_object_name = 'user_feeds'
    template_name = 'feeds.html'

    def get_queryset(self):
        """
        Limit the feeds to the logged in user
        :return: QuerySet, the feeds the user has access to.
        """
        return self.request.user.feed_set.all()


class UserCreate(LoginRequiredMixin, CreateView):
    model = User
    fields = '__all__'
    template_name = 'user_create_form.html'

    def get_success_url(self):
        return reverse('loader:update_user', kwargs={'pk': self.object.id})


class UserUpdate(LoginRequiredMixin, UpdateView):
    """
    Manage feed updates
    """
    model = User
    fields = '__all__'
    template_name = 'user_update_form.html'

    def get(self, *args, **kwargs):
        """
        Ensure that the person accessing this feed is allowed access.
        :return: Http response, 404 or successful feed update form.
        """
        user = User.objects.get(pk=kwargs['pk'])

        if self.request.user.pk == user.pk:
            return super(UserUpdate, self).get(*args, **kwargs)
        else:
            return Http404('Sorry you cannot access this user.')

    def get_success_url(self):
        return reverse('loader:update_user', kwargs={'pk': self.object.id})


class FeedCreate(LoginRequiredMixin, CreateView):
    """
    Manage feed creation.
    """
    model = Feed
    fields = '__all__'
    template_name = 'feed_create_form.html'

    def get_success_url(self):
        return reverse('loader:update_feed', kwargs={'pk': self.object.id})


class FeedUpdate(LoginRequiredMixin, UpdateView):
    """
    Manage feed updates
    """
    model = Feed
    fields = '__all__'
    template_name = 'feed_update_form.html'

    def get(self, *args, **kwargs):
        """
        Ensure that the person accessing this feed is allowed access.
        :return: Http response, 404 or successful feed update form.
        """
        feed = Feed.objects.get(pk=kwargs['pk'])

        if self.request.user in feed.users.all():
            return super(FeedUpdate, self).get(*args, **kwargs)
        else:
            return Http404('Sorry you cannot access this feed.')

    def get_success_url(self):
        return reverse('loader:update_feed', kwargs={'pk': self.object.id})


class LoadFileView(LoginRequiredMixin, View):
    """
    Handle the file loading views here.
    """
    FORM_CLASS = FileForm
    MODEL = File

    def get(self, request, *args, **kwargs):
        """
        Load up the file uploader form.

        :param request: HTTP request holding the user.
        :return: render: the loader template.
        """
        form = self.FORM_CLASS(request.user)

        return render(request, 'loader.html', {'form': form})

    def post(self, request, *args, **kwargs):
        """
        Handle the post data from an input file form.

        :param request: HTTP request holding the user.
        :return: redirect: a page showing the new file.
        """
        form = self.FORM_CLASS(request.user, request.POST, request.FILES)

        if form.is_valid():
            new_upload = self.MODEL(**form.cleaned_data)
            new_upload.save()

            return redirect('loader:view_file', new_upload.pk)

        return render(request, 'loader.html', {'form': form})


@login_required
def view_file(request, pk):
    """

    :param request: HTTP request.
    :param file_pk: pk of the file we need to load into the view.
    :return:
    """
    file_to_load = File.objects.get(pk=pk)

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
