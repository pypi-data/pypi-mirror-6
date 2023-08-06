# -*- coding: utf-8 -*-

"""
    Custom Accounts Urls
    Author  :   Alvaro Lizama Molina <nekrox@gmail.com>
"""

from django.conf.urls import patterns, url
from .settings import LOGOUT_REDIRECT_URL

urlpatterns = patterns('',
        url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
        url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': LOGOUT_REDIRECT_URL}, name='logout'),
        url(r'^register/$', 'accounts.views.register', name='register'),
        url(r'^activation/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            'accounts.views.activation_confirm',
            name='activation_confirm'),
        url(r'^password_reset/$', 'django.contrib.auth.views.password_reset', name='password_reset'),
        url(r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done', name='password_reset_done'),
        url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            'django.contrib.auth.views.password_reset_confirm',
            name='password_reset_confirm'),
        url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete', name='password_reset_complete'),
        )
