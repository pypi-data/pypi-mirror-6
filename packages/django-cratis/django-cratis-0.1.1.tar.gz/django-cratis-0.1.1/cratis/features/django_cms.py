from pywizard.resources.package_pip import pip_package
from cratis.features import Feature, require
#
#from cms.appresolver import applications_page_check
#
#
#class LazyPage(object):
#    def __get__(self, request, obj_type=None):
#        from cms.utils.page_resolver import get_page_from_request
#        if not hasattr(request, '_current_page_cache'):
#            request._current_page_cache = get_page_from_request(request)
#            if not request._current_page_cache:
#                # if this is in a apphook
#                # find the page the apphook is attached to
#                request._current_page_cache = applications_page_check(request)
#        return request._current_page_cache
#
#
#class CurrentPageMiddleware(object):
#    def process_request(self, request):
#        request.__class__.current_page = LazyPage()
#        return None

from cratis.features.i18n import I18n


@require(I18n)
class Cms(Feature):
    def get_required_packages(self, cls):
        return ('django-mptt',
                'django-cms',
                'Pillow',
                #'django-filer',
                #'cmsplugin-filer',

                #'easy_thumbnails',
                )

    def configure_settings(self, cls):
        self.append_apps(cls, [
            'cms',
            'mptt',
            'menus',
            'south',
            'sekizai',

            'cms.plugins.flash',
            'cms.plugins.googlemap',
            'cms.plugins.link',
            'cms.plugins.text',
            'cms.plugins.twitter'
        ])

        self.append_middleware(cls, [
            'cms.middleware.page.CurrentPageMiddleware',
            'cms.middleware.user.CurrentUserMiddleware',
            'cms.middleware.toolbar.ToolbarMiddleware',
            'cms.middleware.language.LanguageCookieMiddleware'
        ])

        self.append_template_processor(cls, [
            'cms.context_processors.media',
            'sekizai.context_processors.sekizai'
        ])

        cls.CMS_TEMPLATES = ()


    def configure_urls(self, cls, urls):

        from django.conf.urls import url, patterns
        from cms.views import details
        from django.views.decorators.cache import cache_page
        from cratis.app.i18n.utils import localize_url as _

        if cls.DEBUG:
            urls += patterns('',
                             url(_(r'^$'), details, {'slug': ''}, name='pages-root'),
                             url(_(r'^(?P<slug>[0-9A-Za-z-_.//]+)$'), details, name='pages-details-by-slug'),
            )
        else:
            urls += patterns('',
                             url(_(r'^$'), cache_page(60 * 24)(details), {'slug': ''}, name='pages-root'),
                             url(_(r'^(?P<slug>[0-9A-Za-z-_.//]+)$'), cache_page(60 * 24)(details),
                                 name='pages-details-by-slug'),
            )
