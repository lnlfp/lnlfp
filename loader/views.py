from django.shortcuts import render

from loader.forms import FileForm
from loader.models import File

def load_file(request):
    form = FileForm()
    return render(request, 'loader.html', {'form':form})
