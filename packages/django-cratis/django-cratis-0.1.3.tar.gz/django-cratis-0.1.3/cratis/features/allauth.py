from django.conf.urls import patterns, include
from cratis.features import Feature


class DjangoAllauth(Feature):

    def get_required_packages(self, cls):
        return ['django-allauth', 'django-bootstrap-form']

    def configure_settings(self, cls):

        cls.AUTHENTICATION_BACKENDS += ("allauth.account.auth_backends.AuthenticationBackend", )

        self.append_template_processor(cls, (
            "allauth.account.context_processors.account",
            "allauth.socialaccount.context_processors.socialaccount",
        ))

        self.append_apps(cls, (
            'allauth',
            'allauth.account',
            'allauth.socialaccount',

            # ... include the providers you want to enable:
            # 'allauth.socialaccount.providers.angellist',
            # 'allauth.socialaccount.providers.bitly',
            # 'allauth.socialaccount.providers.dropbox',
            'allauth.socialaccount.providers.facebook',
            # 'allauth.socialaccount.providers.feedly',
            # 'allauth.socialaccount.providers.github',
            # 'allauth.socialaccount.providers.google',
            # 'allauth.socialaccount.providers.instagram',
            # 'allauth.socialaccount.providers.linkedin',
            # 'allauth.socialaccount.providers.linkedin_oauth2',
            # 'allauth.socialaccount.providers.openid',
            # 'allauth.socialaccount.providers.persona',
            # 'allauth.socialaccount.providers.soundcloud',
            # 'allauth.socialaccount.providers.stackexchange',
            # 'allauth.socialaccount.providers.twitch',
            # 'allauth.socialaccount.providers.twitter',
            # 'allauth.socialaccount.providers.vimeo',
            # 'allauth.socialaccount.providers.vk',
            # 'allauth.socialaccount.providers.weibo',
        ))


    def configure_urls(self, cls, urls):
        urls += patterns('',
            (r'^accounts/', include('allauth.urls')),
            (r'^accounts/', include('cratis.app.profile.urls')),
        )