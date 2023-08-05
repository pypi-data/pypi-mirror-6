# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns('wirecloud.platform.widget.views',
    url(r'^media/(?P<vendor>[^/]+)/(?P<name>[^/]+)/(?P<version>[^/]+)/(?P<file_path>.+)$',
        'serve_showcase_media',
        name='wirecloud_showcase.media'
    ),
)
