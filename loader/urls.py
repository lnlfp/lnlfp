from django.conf.urls import include, url

from loader import views

urlpatterns = [
    url(r'^login_to_app$', views.login_to_app, name='login_to_app'),
    url(r'^logout$', views.logout_of_app, name='logout_of_app'),
    url(r'^table/(?P<file_pk>[0-9]+)$', views.view_file, name='view_file'),
    url(r'^$', views.load_file, name='load_file'),
]
