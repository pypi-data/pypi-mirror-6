#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name='django-tiendata',
    version='0.0.1',
    description='Django-based online store',
    license='GPLv2',
    keywords='ecommerce online-store store vitural-shop shop',
    author='Nando Quintana',
    author_email='nando@tiendata.com',
    url='http://www.tiendata.com/',
    packages=[
        'tiendata',
    ],
    classifiers=['Development Status :: 3 - Alpha',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Utilities'],
)
