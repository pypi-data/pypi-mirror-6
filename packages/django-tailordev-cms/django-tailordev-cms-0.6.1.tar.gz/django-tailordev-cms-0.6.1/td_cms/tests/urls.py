# -*- coding: utf-8 -*-
"""
Urls for testing purpose
"""
from django.conf.urls import include, patterns, url

from .views import NotCMSTestView, RootTestView


urlpatterns = patterns('',
    # Test views
    url(r'^$',
        RootTestView.as_view(),
        name='root_view'),

    url(r'^this/is/a/testing_pattern/',
        NotCMSTestView.as_view(),
        name='not_cms_test_view'),

    # TD_CMS views
    url(r'', include('td_cms.urls')),
)
