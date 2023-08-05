# coding: utf-8
from pywizard.resources.package_pip import pip_package
from voluptuous import Schema, MultipleInvalid
from cratis.features import Feature


class I18n(Feature):

    def __init__(self, langs=(('en', 'English'),), main_lang='en', admin_lang=None, fallback_translations=False):
        self.main_lang = main_lang
        self.admin_lang = admin_lang if admin_lang else main_lang
        self.langs = langs

        self.fallback_translations = fallback_translations

        try:
            Schema(((str, str),))(langs)
        except MultipleInvalid as e:
            self.report_failure('Parameter "langs" validation error: %s' % str(e))

    def configure_settings(self, cls):

        self.append_apps(cls, ('cratis.app.i18n',))

        cls.USE_FALLBACK_TRANSLATION = self.fallback_translations
        cls.LANGUAGE_CODE = self.main_lang
        cls.USE_I18N = True
        cls.USE_L10N = True

        if self.langs:
            cls.LANGUAGES = self.langs

        cls.MAIN_LANGUAGE = self.main_lang
        cls.ADMIN_LANGUAGE = self.admin_lang

        self.append_middleware(cls, ('cratis.app.i18n.middleware.LocaleRewriteMiddleware',))

        self.append_template_processor(cls, ('cratis.app.i18n.context.i18n_context',))

        cls.USE_FALLBACK_TRANSLATION = False


class I18nAdminUi(Feature):

    def get_required_packages(self, cls):
        return 'django-rosetta',

    def configure_settings(self, cls):
        self.append_apps(cls, [
            'rosetta',
        ])

        cls.ROSETTA_WSGI_AUTO_RELOAD = True
        cls.ROSETTA_MESSAGES_PER_PAGE = 20
        cls.ROSETTA_STORAGE_CLASS = 'rosetta.storage.SessionRosettaStorage'


    def configure_urls(self, cls, urls):
        from django.conf.urls import url, include, patterns

        urls += patterns('',
            url(r'^admin/i18n/', include('rosetta.urls')),
        )



