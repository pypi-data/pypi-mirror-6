import os
from setuptools import setup, find_packages
# from tests import PyTest

setup(
    name='django-cratis',
    version='0.1.8',
    packages=find_packages(),

    namespace_packages=['cratis'],

    url='',
    license='MIT',
    author='Alex Rudakov',
    author_email='ribozz@gmail.com',
    description='Collection of django tools tightly integrated with each other.',
    long_description='',
    install_requires=[
        #'django==1.5.5',
        #'django-configurations',
        #'setuptools',
        #'dj-database-url',
        #'PyYaml',
        #'pywizard',
        #'html5lib',
        #'django-wsgiserver',
        #'south',
        #'voluptuous'

        'Django==1.5.5',
        'Jinja2==2.7.1',
        'MarkupSafe==0.18',
        'Pillow==2.3.0',
        'PyYAML==3.10',
        'South==0.8.4',
        'argparse==1.2.1',
        'cmsplugin-filer==0.9.5',
        'dj-database-url==0.2.2',
        'django-allauth==0.15.0',
        'django-bootstrap-form==3.1',
        'django-classy-tags==0.4',
        'django-configurations==0.7',
        'django-debug-toolbar==1.0',
        'django-filer==0.9.5',
        'django-mptt==0.6.0',
        'django-polymorphic==0.5.3',
        'django-rosetta==0.7.3',
        'django-sekizai==0.7',
        'django-suit==0.2.5',
        'django-wsgiserver==0.8.0rc1',
        'easy-thumbnails==1.4',
        'html5lib==0.999',
        'iniparse==0.4',
        'oauthlib==0.6.0',
        'psutil==1.2.1',
        'python-openid==2.2.5',
        'requests==2.2.0',
        'requests-oauthlib==0.4.0',
        'six==1.4.1',
        'sqlparse==0.1.10',
        'voluptuous==0.8.4',
        'wsgiref==0.1.2',
        'django-cratis>=0.1.4',
        'django-cms',
        #'-e git://github.com/ribozz/django-cms.git@aa43b1715bdb39ac507d4ffac53e7c6bf7998e48#egg=django-cms',
    ],

    entry_points={
        'console_scripts': [
            'cratis = cratis.cli:cratis_cmd',
        ],
    },
)

