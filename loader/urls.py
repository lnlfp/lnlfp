from django.conf.urls import include, url

from loader import views

urlpatterns = [
    url(r'^$', views.load_file, name='load_file'),
]
