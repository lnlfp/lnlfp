import codecs
import csv

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import password_change
from django.core.urlresolvers import reverse
from django.db.models.functions import Lower
from django.shortcuts import render, redirect, Http404
from django.views.generic import View, ListView, CreateView, UpdateView
from loader.forms import FileForm, ProcedureForm, ValidationError, LoginForm
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
        form = LoginForm(request.POST)

        if form.is_valid():
            user = form.login()

            if user:
                login(request, user)

                if request.POST.get('next'):
                    return redirect(request.POST.get('next', 'loader:user_home'))
                else:
                    return redirect('loader:user_home', )
    else:
        form = LoginForm()
    # If we have reached here, the user has not registered as logged in.
    return render(request, 'login.html', {'form': form})


def logout_of_app(request):
    """
    Basic view to logout a user. Redirects to the login screen.

    :param request: HTTP Request containing the user.
    :return: redirect to login page.
    """
    logout(request)
    return redirect('loader:login')


class UserHomeView(LoginRequiredMixin, View):
    """
    The home page for a user.
    """
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


class UserUpdate(LoginRequiredMixin, UpdateView):
    """
    Manage feed updates.
    """
    model = User
    fields = ['first_name', 'last_name', 'email']
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
        """
        On success return the update page for this user.

        :return: HTTP, response for update page.
        """
        return reverse('loader:update_user', kwargs={'pk': self.object.id})


def change_own_pass(request):
    return password_change(request,
                           template_name='change_password.html',
                           post_change_redirect=reverse('loader:update_user', kwargs={'pk': request.user.pk}))


class FeedCreate(LoginRequiredMixin, CreateView):
    """
    Manage Feed creation.
    """
    model = Feed
    fields = '__all__'
    template_name = 'feed_create_form.html'

    def get_success_url(self):
        """
        On success return the update page for this feed.

        :return: HTTP, response for update page.
        """
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
        """
        On success return the update page for this feed.

        :return: HTTP, response for update page.
        """
        return reverse('loader:update_feed', kwargs={'pk': self.object.id})


class ProcedureListView(LoginRequiredMixin, ListView):
    """
    Allow a user to view the feeds they have access to.
    """
    model = Procedure
    context_object_name = 'user_procedures'
    template_name = 'procedures.html'

    def get_queryset(self):
        """
        Limit the feeds to the logged in user

        :return: QuerySet, the feeds the user has access to.
        """
        return self.request.user.procedure_set.all()


class ProcedureCreate(LoginRequiredMixin, CreateView):
    """
    Manage creation of procedures.
    """
    form_class = ProcedureForm
    model = Procedure
    template_name = 'proc_create_form.html'

    def get_success_url(self):
        """
        On success return the update page for this procedure.

        :return: HTTP, response for update page.
        """
        return reverse('loader:update_proc', kwargs={'pk': self.object.id})

    def get_form_kwargs(self):
        """
        Add the user into the form kwargs.

        :return: dict, arguments for a form.
        """
        initial = super(ProcedureCreate, self).get_form_kwargs()
        initial['user'] = self.request.user

        return initial

    def get_context_data(self, **kwargs):
        """
        Add plugin languages to context.

        :return: dict, context dict for the view.
        """
        ctx = super(ProcedureCreate, self).get_context_data(**kwargs)

        langs = [x[0] for x in ctx['form'].fields['language'].choices if x[0] != '']

        ctx['langs'] = langs

        return ctx

    def form_valid(self, form):
        """
        Add the user to the form.

        :return: bool, is the form valid.
        """
        form.instance.user = self.request.user
        form.instance.save()
        return super(ProcedureCreate, self).form_valid(form)


class ProcedureUpdate(LoginRequiredMixin, UpdateView):
    """
    Manage feed updates
    """
    model = Procedure
    fields = '__all__'
    template_name = 'proc_update_form.html'

    def get_success_url(self):
        """
        On success return the update page for this procedure.

        :return: HTTP, response for update page.
        """
        return reverse('loader:update_proc', kwargs={'pk': self.object.id})


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
            new_upload.get_table_info()
            new_upload.save()

            return redirect('loader:view_file', new_upload.pk)

        return render(request, 'loader.html', {'form': form})


class FileView(LoginRequiredMixin, View):
    """
    A table based view for a file we are loading.
    """
    def get(self, request, pk, *args, **kwargs):
        """
        Parse the file and load on screen.

        :param request: HTTP request.
        :param file_pk: pk of the file we need to load into the view.
        :return: HTTP response, the loaded table
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
            data.append(next(reader))
            header = ['']*len(data[0])
            row_num += 1
            no_cols = len(data[0])

        choices = ""
        for col in special_cols:
            choices += '<option value="{pk}">{name}</option>\n'.format(pk=col.pk, name=col.name)

        template_choice = """<form>
                                 <input name="col_select_{col_num}" type="text" value="{header}">
                             </form>"""
        """
<select class="form-control" name="col_select_{col_num}">
    <option value selected disabled>Special Column</option>
    <option value="None">None</option>
    {choices}
</select>"""

        column_choice_row = []
        for idx in range(no_cols):
            if header:
                column_choice_row.append(template_choice.format(col_num=idx, choices=choices, header=header[idx]))

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
                                              'procedures': procedures,
                                              'file': file_to_load})

    def post(self, request, pk, *args, **kwargs):
        """
        Handle and run the proc we want to use.

        :param request: HTTP request.an_ad['fx_junk'][r] = an_ad['name']
        :param file_pk: pk of the file we need to load into the view.
        :return: HTTP response, the loaded table
        """

        print(request.POST)

        proc_pk = request.POST.get('procedure')

        if proc_pk:
            proc = Procedure.objects.get(pk=proc_pk)
        else:
            raise ValidationError('You need to select a procedure to run.')

        file_to_run = File.objects.get(pk=pk)

        no_cols = len(file_to_run.get_first_lines(1)[0].split(file_to_run.delimiter))

        #cols = self.get_columns(request.POST, no_cols)

        #file_to_run.set_columns(cols)

        file_to_run.save()

        output = proc.run(file_to_run)

        return self.get(request, pk, *args, **kwargs)

    def get_columns(self, data, no_cols):
        """
        Run through the POST data to get all the column data.

        :param data: dict, request.POST data.
        :param no_cols: int, number of columns in table.
        :return: lst, lst of special columns.
        """

        cols = [None] * no_cols
        for key in data:
            if key.startswith('col_select'):
                if data[key] != 'None':
                    cols[int(key.split('_')[-1])] = data[key]

        return colspy