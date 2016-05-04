from django import forms
from django.forms import Form, ModelForm, ValidationError
from django.contrib.auth import authenticate, login

from loader.models import File, Procedure


class FileForm(ModelForm):
    """
    Manage the creation of files here.

    We are only interested in uploading the file and attaching it to a feed and user.

    We may do some preemptive analysis. But most of the column definitions come later.
    """
    class Meta:
        model = File
        fields = ['data', 'feed']

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(FileForm, self).__init__(*args, **kwargs)

    def clean(self):
        """
        We need to do some model validation to ensure the User given is acceptable.

        We also need to make sure we actually have a file.

        :return: dict, the data needed for the model.
        """

        cleaned_data = super(FileForm, self).clean()

        feed = cleaned_data.get('feed')

        if feed:
            if self.user not in feed.users.all():
                raise ValidationError('This User is not authorised to upload files to this feed!')
        else:
            raise ValidationError('No valid feed given')

        if not cleaned_data.get('data'):
            raise ValidationError('No file input given.')

        cleaned_data['user'] = self.user

        return cleaned_data


class ProcedureForm(ModelForm):
    """
    Monitor the creation of a procedure.
    """
    class Meta:
        model = Procedure
        exclude = ['user']

    def __init__(self, user, *args, **kwargs):
        super(ProcedureForm, self).__init__(*args, **kwargs)

        self.user = user

    def clean(self):
        """
        We need to make sure that the procedure extension matches that of the language given.

        Also need to add the user to the cleaned_data.

        :return: dict, the data needed for the model.
        """
        cleaned_data = super(ProcedureForm, self).clean()

        if not cleaned_data['procedure'].name.endswith(Procedure.LANGUAGE_EXTENSIONS[cleaned_data['language']]):
            raise ValidationError('The file extension does not match the language picked!')

        cleaned_data['user'] = self.user

        print(cleaned_data, self.user.id)

        return cleaned_data

class LoginForm(Form):
    """
    Manage logins to the app.
    """
    username = forms.CharField()
    password = forms.CharField()

    def clean(self):
        """
        Make sure the login worked.

        :return: dict, the cleaned_data.
        """
        user = self.login()

        if not user or not user.is_active:
            raise ValidationError('Sorry that was an invalid login. Please try again.')

        return self.cleaned_data

    def login(self):
        """
        Authenticate the user for logging in.

        :return: User, the authenticated user.
        """
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)

        return user