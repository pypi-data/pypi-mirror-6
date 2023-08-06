#!/usr/bin/env python
from setuptools import setup, find_packages

import django_shareable

setup(
    name = "django-shareable",
    version = django_shareable.__version__,
    description = "Templatetags for 'tweet this' and 'share on facebook'",
    packages = find_packages(),
    package_data = {
        'django_shareable': [
            'templates/*.*',
            'templates/*/*.*',
            'templates/*/*/*.*',
            'static/*.*',
            'static/*/*.*',
            'static/*/*/*.*',
        ],
    },
    url = 'https://github.com/chrisspen/django-shareable',
    license = 'MIT',
    author = 'Chris Spencer',
    author_email = 'chrisspen@gmail.com',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    zip_safe = False,
    install_requires = ['Django>=1.4.0'],
)
