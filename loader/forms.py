from django.forms import ModelForm, ValidationError
from loader.models import File, Procedure


class FileForm(ModelForm):
    class Meta:
        model = File
        fields = ['data', 'feed']

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(FileForm, self).__init__(*args, **kwargs)

    def clean(self):
        """
        We need to do some model validation to ensure the User given is acceptable.
        """

        cleaned_data = super(FileForm, self).clean()

        feed = cleaned_data.get('feed')

        if feed:
            if self.user not in feed.users.all():
                raise ValidationError('This User is not authorised to upload files to this feed!')
        else:
            raise ValidationError('No valid feed given')

        data = cleaned_data.get('data')

        if not data:
            raise ValidationError('No file input given.')

        cleaned_data['user'] = self.user

        return cleaned_data


class ProcedureForm(ModelForm):
    class Meta:
        model = Procedure
        exclude = ['user']

    def __init__(self, user, *args, **kwargs):
        super(ProcedureForm, self).__init__(*args, **kwargs)

        self.user = user

    def clean(self):

        cleaned_data = super(ProcedureForm, self).clean()

        if not cleaned_data['procedure'].name.endswith(Procedure.LANGUAGE_EXTENSIONS[cleaned_data['language'].language]):
            raise ValidationError('The file extension does not match the language picked!')

        cleaned_data['user'] = self.user

        return cleaned_data