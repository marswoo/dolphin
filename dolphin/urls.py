#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from dolphin import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^start/(?P<pair>[\d|_shz]+)/$', views.start, name='start'),
    url(r'^stop/(?P<pair>[\d|_shz]+)/$', views.stop, name='stop'),
    url(r'^start_all/$', views.start_all, name='start_all'),
    url(r'^stop_all/$', views.stop_all, name='stop_all'),
    url(r'^view_assets/$', views.view_assets, name='view_assets'),

    url(r'^detail/(?P<pair>[\dl_shz]+)/(?P<date>[\d-]+)/$', views.detail, name='detail'),

    url(r'^init/$', views.init, name='init'),
    url(r'^get_stockdata/(?P<stockid>[\d|shz]+)/$', views.get_stockdata, name='get_stockdata'),
    url(r'^trade/(?P<functionid>[\w\.]+)/$', views.trade, name='trade'),
    url(r'^clear/(?P<pair>[\d|_shz]+)/$', views.clear, name='clear'),
)

