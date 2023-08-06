import os
from setuptools import setup, find_packages
# from tests import PyTest

setup(
    name='django-cratis',
    version='0.1.9',
    packages=find_packages(),

    namespace_packages=['cratis'],

    url='',
    license='MIT',
    author='Alex Rudakov',
    author_email='ribozz@gmail.com',
    description='Collection of django tools tightly integrated with each other.',
    long_description='',
    install_requires=[
        'django==1.5.5',
        'django-configurations',
        'setuptools',
        'dj-database-url',
        'PyYaml',
        'pywizard',
        'html5lib',
        'django-wsgiserver',
        'south',
        'voluptuous'
        #'-e git://github.com/ribozz/django-cms.git@aa43b1715bdb39ac507d4ffac53e7c6bf7998e48#egg=django-cms',
    ],

    entry_points={
        'console_scripts': [
            'cratis = cratis.cli:cratis_cmd',
        ],
    },
)

