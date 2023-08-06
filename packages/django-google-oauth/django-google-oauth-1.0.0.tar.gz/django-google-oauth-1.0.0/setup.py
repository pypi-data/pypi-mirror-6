#!/usr/bin/env python

import os
import sys

from setuptools import setup
from setuptools import find_packages

__author__ = 'Marco trik Marche <marco.marche@gnucoop.com>'
__version__ = '1.0.0'

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

setup(
    name='django-google-oauth',
    version=__version__,
    install_requires=['google-api-python-client', 'django'],
    author='Marco trik Marche',
    author_email='marco.marche@gnucoop.com',
    license=open('LICENSE').read(),
    url='https://bitbucket.org/trik82/django-google-oauth/tree/master',
    keywords='google google+ api auth oauth2 django integration',
    description='Django Integration for Google+ OAuth2',
    long_description=open('README.rst').read(),
    include_package_data=True,
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',
        'Topic :: Internet'
    ]
)
