#!/usr/bin/env python

from distutils.core import setup

setup(name='vlk-django-jsonfield',
    version='1.2',
    license='MIT',
    author='See README.md',
    description='A model JSONField with an integrated form for django.',
    long_description=open('README.md').read(),
    packages=['vlkjsonfield'],
    url='https://github.com/vialink/vlk-jsonfield',
)
