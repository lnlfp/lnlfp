from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import login

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/login/$', view=login, kwargs={'template_name': 'login.html'}),
    url(r'^loader/', include('loader.urls', namespace='loader')),
]
