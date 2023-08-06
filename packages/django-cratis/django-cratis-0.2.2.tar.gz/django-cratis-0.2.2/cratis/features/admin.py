import os
from cratis.features import Feature


class AdminArea(Feature):

    def __init__(self, prefix=r'^admin/'):
        super(AdminArea, self).__init__()
        self.prefix = prefix

    def configure_settings(self, cls):
        cls.INSTALLED_APPS += ('django.contrib.admin',)

    def configure_urls(self, cls, urls):

        from django.conf.urls import patterns, url, include
        from django.contrib import admin

        admin.autodiscover()

        urls += patterns('',
            url(self.prefix, include(admin.site.urls)),
        )


class AdminThemeSuit(Feature):

    def __init__(self, title='My site'):
        self.title = title

    def get_required_packages(self, cls):
        return 'django-suit',


    def configure_settings(self, cls):

        cls.INSTALLED_APPS += ('suit',)

        if not 'django.core.context_processors.request' in cls.TEMPLATE_CONTEXT_PROCESSORS:
            cls.TEMPLATE_CONTEXT_PROCESSORS += ('django.core.context_processors.request',)

        cls.SUIT_CONFIG = {
            'ADMIN_NAME': self.title
        }

        cls.TEMPLATE_DIRS += (os.path.dirname(os.path.dirname(__file__)) + '/templates/suit-feature',)
