#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages
    
import os

VERSION = open('VERSION').read().strip()

REQUIRES = open('requirements.txt').read()

README = open('README.md').read()

setup(
    name = "django-piston3",
    version = VERSION,
  ##   url = 'http://bitbucket.org/jespern/django-piston/wiki/Home',
	## download_url = 'http://bitbucket.org/jespern/django-piston/downloads/',
    url = 'https://bitbucket.org/userzimmermann/django-piston3',
    download_url = 'https://pypi.python.org/pypi/django-piston3',
    license = 'BSD',
    ## description = "Piston is a Django mini-framework creating APIs.",
    description = "Piston for Python 3.3+ and Django 1.6+"
                  " - Compatible with Python 2.7",
    long_description = README,
    author = 'Jesper Noehr',
    author_email = 'jesper@noehr.org',
    maintainer = 'Stefan Zimmermann',
    maintainer_email = 'zimmermann.code@gmail.com',
    install_requires = REQUIRES,
    packages = [p.replace('piston', 'piston3')
                for p in find_packages(exclude=['piston3'])],
    package_dir = {'piston3': 'piston'},
    include_package_data = True,
    zip_safe = False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
    ],
    keywords = [
        'django', 'piston3', 'piston',
        'web', 'framework', 'api', 'rest',
        'python3',
    ],
)
