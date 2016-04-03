from django.conf.urls import url

from loader import views

urlpatterns = [
    url(r'^login_to_app/$', views.login_to_app, name='login_to_app'),
    url(r'^logout/$', views.logout_of_app, name='logout_of_app'),
    url(r'^$', views.UserHomeView.as_view(), name='user_home'),
    url(r'^feeds/$', views.FeedListView.as_view(), name='user_feeds'),
    url(r'^feeds/(?P<pk>[0-9]+)/$', views.FeedUpdate.as_view(), name='update_feed'),
    url(r'^feeds/create/$', views.FeedCreate.as_view(), name='create_feed'),
    url(r'^table/(?P<file_pk>[0-9]+)/$', views.view_file, name='view_file'),
    url(r'^new_file/$', views.LoadFileView.as_view(), name='load_file'),
]
