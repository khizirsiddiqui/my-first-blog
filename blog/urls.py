from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^$', views.post_list, name='post_list'),
    url(r'^drafts/$', views.post_draft_list, name='post_draft_list'),

    url(r'^post/(?P<pk>\d+)/$', views.post_detail, name='post_detail'),
    url(r'^post/new/$', views.post_new, name='post_new'),

    url(r'^post/(?P<pk>\d+)/edit/$', views.post_edit, name='post_edit'),
    url(r'^post/(?P<pk>\d+)/remove/$', views.post_remove, name='post_remove'),
    url(r'^post/(?P<pk>\d+)/publish/$', views.post_publish,
        name='post_publish'),

    url(r'^post/(?P<pk>\d+)/rep_author/$', views.rep_author,
        name='rep_author'),
    url(r'^post/(?P<pk>\d+)/upvote/$', views.post_upvote, name='post_upvote'),

    url(r'^login/$', views.user_login, name='user_login'),
    url(r'^logout/$', views.user_logout, name='user_logout'),
    url(r'^register/$', views.user_register, name='user_register'),
    url(r'^accounts/update/(?P<pk>[\-\w]+)/$',
        views.edit_user, name='account_update'),

    url(r'^accounts/', include('allauth.urls')),
    url(r'profile/(?P<username>[a-zA-Z0-9]+)$',
        views.get_user_profile, name='user_profile'),

    url(r'^comment/(?P<pk>\d+)/approve/$',
        views.comment_approve, name='comment_approve'),
    url(r'^comment/(?P<pk>\d+)/remove/$',
        views.comment_remove, name='comment_remove'),
]
