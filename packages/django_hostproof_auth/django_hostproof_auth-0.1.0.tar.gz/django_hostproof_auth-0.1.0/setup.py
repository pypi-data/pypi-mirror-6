#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from hostproof_auth import __version__

setup(
    name='django_hostproof_auth',
    version=__version__,
    description='Secure Host-Proof authentication backend for Django-powered sites',
    author='Jorge Pintado',
    author_email='j.pintado89@gmail.com',
    url='https://github.com/jpintado/django-hostproof-auth',
    long_description=open('README.rst', 'r').read(),
    license="MIT",
    requires=[
        'rsa(>=3.1.2)',
    ],
    install_requires=[
        'rsa >= 3.1.2',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities' 
    ],

    packages=[
        'hostproof_auth'
    ],
    include_package_data=True,
    zip_safe=False,
)

