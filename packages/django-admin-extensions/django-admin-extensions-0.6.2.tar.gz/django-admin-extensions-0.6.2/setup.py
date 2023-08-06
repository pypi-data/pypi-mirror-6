#!/usr/bin/env python
"""
Install django-admin-extensions using setuptools
"""

from adminextensions import __version__

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='django-admin-extensions',
    version=__version__,
    description='Simple tools to extend the django admin site',
    author='Ionata Web Solutions',
    author_email='webmaster@ionata.com.au',
    url='https://bitbucket.org/ionata/django-admin-extensions',

    packages=find_packages(),

    package_data={ },
    include_package_data=True,

    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)
