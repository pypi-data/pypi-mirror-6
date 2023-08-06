#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import version_info
from distutils.core import setup

if version_info < (3,0):
    raise NotImplementedError('This module works only in Python 3.x versions.')

with open('README.rst') as f:
    readme = f.read()

setup(
    name='python-reCAPTCHA',
    version='0.1.0',
    author='Rafael Bicalho',
    author_email='rbmbika@gmail.com',
    packages=['recaptcha'],
    url='http://pypi.python.org/pypi/python-reCAPTCHA/',
    license='LICENSE.txt',
    description='Python module for reCAPTCHA service.',
    long_description=readme,
)
