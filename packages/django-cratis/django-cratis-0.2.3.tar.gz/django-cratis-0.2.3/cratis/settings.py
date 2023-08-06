"""
Default settings for cratis project
"""
import logging
import os
import pywizard.api as pw

from configurations import Configuration, values
import sys
from pywizard.context import Context
from pywizard.cli import yn_choice

import inject

class Common(Configuration):

    @classmethod
    def load_features(cls):
        loaded_features = []
        for feature in cls.FEATURES:

            for requirement in feature.get_required(cls):
                if not requirement in loaded_features:
                    message = '\n Feature %s depends on %s, that is not loaded yet. Order is also important!\n' % (
                        str(type(feature)),
                        str(requirement),
                    )
                    print(message)
                    sys.exit(1)

            feature.configure_settings(cls)

            loaded_features.append(type(feature))

    @classmethod
    def pre_setup(cls):
        super(Common, cls).pre_setup()

        cls.load_features()

        ctx = Context()

        with pw.resource_set(ctx, name='main'):
            for feature in cls.FEATURES:
                requirements = []
                for req in feature.get_required_packages(cls):
                    requirements.append(req)

                if requirements:
                    ctx.apply(
                        pw.pip_package(*requirements)
                    )

        changes = ctx.changeset()

        if changes.needed():

            if len(sys.argv) == 2 and sys.argv[1] == '--requirements':
                print('\nChanges to be applied:\n')
                for item in changes.items:
                    print('\t - %s' % item.description)

                changes.commit()

                exit(0)

            else:
                print('\nSome required packages are not installed:\n')
                for item in changes.items:
                    print('\t - %s' % item.description)

                print 'Execute "cratis --requirements" to install those'

                exit(1)

    @classmethod
    def post_setup(cls):
        super(Common, cls).post_setup()

        def configure_feature_services(binder):
            for feature in cls.FEATURES:
                feature.append_services(binder)

        inject.configure(configure_feature_services)

        for feature in cls.FEATURES:
            feature.on_startup()


    FEATURES = ()


    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    BASE_DIR = os.environ.get('CRATIS_APP_PATH', '.')

    # Quick-start development settings - unsuitable for production
    # See https://docs.djangoproject.com/en/{{ docs_version }}/howto/deployment/checklist/

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = 'testing_only'

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = True

    TEMPLATE_DEBUG = True

    ALLOWED_HOSTS = []

    # Application definition

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.sites',
        'south',
        'cratis.app.utils',
        'django_wsgiserver'
    )

    MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    )

    ROOT_URLCONF = 'cratis.urls'

    # WSGI_APPLICATION = '{{ project_name }}.wsgi.application'

    # Database
    # https://docs.djangoproject.com/en/{{ docs_version }}/ref/settings/#databases
    # http://django-configurations.readthedocs.org/en/latest/values/#configurations.values.DatabaseURLValue
    DATABASES = values.DatabaseURLValue(
        'sqlite://%s' % (os.sep + os.path.join(BASE_DIR, 'var', 'db.sqlite3')),
        environ=True)

    # Internationalization
    # https://docs.djangoproject.com/en/{{ docs_version }}/topics/utils/

    TIME_ZONE = 'UTC'
    USE_TZ = True

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/{{ docs_version }}/howto/static-files/

    LOCALE_PATHS = (
        BASE_DIR + '/locale',
    )

    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR + '/var/static'

    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR + '/var/media'

    STATICFILES_DIRS = ()
    TEMPLATE_DIRS = ()

    SITE_ID = 1
