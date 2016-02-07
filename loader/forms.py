from django.forms import ModelForm
from loader.models import File

class FileForm(ModelForm):
    class Meta:
        model = File
        fields = ['data', 'feed']
