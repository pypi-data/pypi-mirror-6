import os
from setuptools import setup, find_packages
# from tests import PyTest

setup(
    name='django-cratis',
    version='0.1.1',
    packages=find_packages(),

    namespace_packages=['cratis'],

    url='',
    license='MIT',
    author='Alex Rudakov',
    author_email='ribozz@gmail.com',
    description='Collection of django tools tightly integrated with each other.',
    long_description='',
    install_requires=[
        'django>=1.4',
        'django-configurations',
        'setuptools',
        'dj-database-url',
        'PyYaml',
        'south',
        'voluptuous'
    ],

    entry_points={
        'console_scripts': [
            'cratis = cratis.cli:cratis_cmd',
        ],
    },
)

