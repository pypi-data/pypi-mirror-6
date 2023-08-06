#!/usr/bin/env python
import os
import urllib

from setuptools import setup, find_packages, Command

import django_sec

setup(
    name = "django-sec",
    version = django_sec.__version__,
    packages = find_packages(),
#    package_data = {
#        'django_sec': [
#            'templates/*.*',
#            'templates/*/*.*',
#            'templates/*/*/*.*',
#            'static/*.*',
#            'static/*/*.*',
#            'static/*/*/*.*',
#        ],
#    },
    author = "Chris Spencer",
    author_email = "chrisspen@gmail.com",
    description = "Parse XBRL filings from the SEC's EDGAR in Python",
    license = "LGPL",
    url = "https://github.com/chrisspen/django-sec",
    #https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    zip_safe = False,
    install_requires = ['Django>=1.4.0', 'lxml'],
)
