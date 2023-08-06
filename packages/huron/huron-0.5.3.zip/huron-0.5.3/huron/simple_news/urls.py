#!/usr/bin/python
# -*- coding: UTF-8 -*-
from django.conf.urls import patterns, url


urlpatterns = patterns('huron.simple_news.views',
                       url(r'^$', 'listing', {'page': 1, 'cat': None},
                           name="list_news"),
                       url(r'^page/(?P<page>\d+)/$', 'listing',
                           {'cat': None}, name="list_news_paged"),
                       url(r'^(?P<slug>[-\w]+)/$', 'single',
                           name='single_news'),
                       url(r'^category/(?P<cat>[-\w]+)/$', 'listing',
                           {'page': 1}, name="list_news_categ"),
                       url(r'^category/(?P<cat>[-\w]+)/page/(?P<page>\d+)/$',
                           'listing', name="list_news_categ_paged"),
                       )
