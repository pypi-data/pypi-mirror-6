# -*- coding:utf-8 -*-

from django.conf.urls import include, patterns, url
from .views import IndexView
from .views import UserMessageView, UserMessagesView, SendMessageView
from .views import PublicProfileView, ProfileView, EditProfileView
from .views import CategoryView, ForumView

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),

    # your own profile
    url(r'^profile/$', ProfileView.as_view(), name='profile'),

    url(r'^profile/register/',
        'forum.views.register_profile_view', name='register_profile'),

    # edit your own profile
    url(r'^profile/edit/$', EditProfileView.as_view(), name='edit_profile'),

    # someones profile
    url(r'^profile/(?P<nickname>[\w\-\+\.@]+)/$',
        PublicProfileView.as_view(), name='profile'),

    # send someone a message
    url(r'^profile/(?P<nickname>[\w\-\+\.@]+)/send_message/$',
        SendMessageView.as_view(), name='send_message'),

    # see your own messages
    url(r'^messages/$', UserMessagesView.as_view(), name='messages'),

    # read your own message
    url(r'^message/(?P<pk_message>\d+)/$', UserMessageView.as_view(), name='messages'),

    # see forum under this category
    url(r'^category/(?P<pk_category>[\w\-\+\.@]+)/$',
        CategoryView.as_view(), name='category'),

    # see forum
    url(r'^(?P<pk_forum>\d+)/$', ForumView.as_view(), name='expose'),

    # post a new thread
    url(r'^(?P<pk_forum>\d+)/threads/new/$',
        'forum.views.new_thread_view', name='new_thread'),

    # read a thread
    url(r'^(?P<pk_forum>\d+)/threads/(?P<pk_thread>\d+)/$',
        'forum.views.thread_view', name='thread'),
#
#    # edit a thread
#    (r'^(?P<pk_forum>\d+)/threads/(?P<pk_thread>\d+)/edit/$',
#        'edit_thread_view', {}, 'edit_thread'),

    # reply to a thread
    url(r'^(?P<pk_forum>\d+)/threads/(?P<pk_thread>\d+)/reply/$',
        'forum.views.reply_view', name='reply'),

#    # rate a thread
#    (r'^(?P<pk_forum>\d+)/threads/(?P<pk_thread>\d+)/reply/(?P<pk_reply>\d+)/rate/$',
#        'rate_reply_view', {}, 'rate'),
)
