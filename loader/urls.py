from django.conf.urls import url

from loader import views

urlpatterns = [
    url(r'^login_to_app/$', views.login_to_app, name='login_to_app'),
    url(r'^logout/$', views.logout_of_app, name='logout_of_app'),
    url(r'^$', views.UserHomeView.as_view(), name='user_home'),
    url(r'^files/$', views.FileListView.as_view(), name='user_files'),
    url(r'^feeds/$', views.FeedListView.as_view(), name='user_feeds'),
    url(r'^feeds/(?P<pk>[0-9]+)/$', views.FeedUpdate.as_view(), name='update_feed'),
    url(r'^feeds/create/$', views.FeedCreate.as_view(), name='create_feed'),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserUpdate.as_view(), name='update_user'),
    url(r'^users/changepass$', views.change_own_pass, name='change_pass'),
    url(r'^users/create/$', views.UserCreate.as_view(), name='create_user'),
    url(r'^procedures/$', views.ProcedureListView.as_view(), name='list_procs'),
    url(r'^procedures/(?P<pk>[0-9]+)/$', views.ProcedureUpdate.as_view(), name='update_proc'),
    url(r'^procedures/create/$', views.ProcedureCreate.as_view(), name='create_proc'),
    url(r'^files/(?P<pk>[0-9]+)/$', views.FileView.as_view(), name='view_file'),
    url(r'^new_file/$', views.LoadFileView.as_view(), name='load_file'),
]
