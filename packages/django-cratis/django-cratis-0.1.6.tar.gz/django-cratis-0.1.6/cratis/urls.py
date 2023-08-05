# import cms
# from cms.views import details

from django.conf.urls import patterns, include, url
from django.conf import settings


urlpatterns = patterns('',)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
        url(r'^assets/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    )

for feature in settings.FEATURES:
    feature.configure_urls(settings, urlpatterns)

