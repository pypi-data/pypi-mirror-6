#!/usr/bin/python
# -*- coding: UTF-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('huron.blog.views',
    url(r'^(?P<day>\d{1,2})/(?P<month>\d{1,2})/(?P<year>\d{4})/(?P<slug>[-\w]+)/$',
     'single'
    ),
    url(r'^page/(?P<page>\d+)/$', 'listing', {'category': None}),
    (r'^(?P<category>[-\w]+)/page/(?P<page>\d+)/$', 'listing'),
    (r'^(?P<category>[-\w]+)/$', 'listing', {'page': 1}),
    url(r'^$', 'listing', {'page': 1, 'category': None}, name='blog_general'),

)