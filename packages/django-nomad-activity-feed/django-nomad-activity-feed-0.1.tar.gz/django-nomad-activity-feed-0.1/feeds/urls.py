from django.conf.urls import patterns, url

urlpatterns = patterns('feeds.views',
    url(r'^follow/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$', 'follow', name='follow'),
    url(r'^unfollow/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$', 'unfollow', name='unfollow'),
)
