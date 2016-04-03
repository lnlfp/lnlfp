from django.forms import ModelForm, ValidationError
from loader.models import File


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
