#!/usr/bin/env python
"""
Flask-Cache
-----------

Adds cache support to your Flask application

"""

from setuptools import setup

setup(
    name='Flask-Cache-Latest',
    version='0.12',
    url='https://github.com/thadeusb/flask-cache/tree/18cd9ebdb20e4d0f8f0900b971fcb8d48e27737d',
    license='BSD',
    author='Thadeus Burgess',
    author_email='thadeusb@thadeusb.com',
    description='Adds cache support to your Flask application',
    long_description=__doc__,
    packages=[
        'flask_cache',
    ],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    test_suite='test_cache',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
