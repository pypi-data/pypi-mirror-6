#!/usr/bin/python
from setuptools import setup, find_packages

from nested_inlines import __version__

github_url = 'https://github.com/phySi0/django-nested-inlines'
dl_url = 'https://github.com/phySi0/django-nested-inlines/archive/0.1.tar.gz'
long_desc = open('README.md').read()

setup(
    name = 'django-nested-inlines',
    version = '.'.join(str(v) for v in __version__),
    description = 'Adds nested inline support in Django admin',
    long_description = long_desc,
    url = github_url,
    download_url = dl_url,
    author = 'Alain Trinh',
    author_email = 'i.am@soaa.me',
    packages = find_packages(exclude=['tests']),
    include_package_data = True,
    license = 'MIT License',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)

