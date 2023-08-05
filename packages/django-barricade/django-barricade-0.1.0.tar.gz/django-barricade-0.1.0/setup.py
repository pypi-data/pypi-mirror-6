#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

__version__ = '0.1.0'
__author__ = 'WanCW'
__email__ = 'wancw.wang@gmail.com'

setup(
    name='django-barricade',
    version=__version__,
    description="Simulate a slow connection",
    author=__author__,
    author_email=__email__,
    url='http://github.com/wancw/django-barricade',
    license='MIT',
    packages=['django_barricade'],
    include_package_data=True,
    install_requires = [
        "django >= 1.4",
    ],
    test_suite='run_tests.main',
    test_require=['Django'],
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
        "Environment :: Web Environment",
    ],
    keywords='django,network',
)