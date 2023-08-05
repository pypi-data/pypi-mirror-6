#!/usr/bin/env python

sdict = {
    'name': 'unicode_tex',
    'version': "0.1.0",
    'license': 'MIT',
    'py_modules': ['unicode_tex'],
    'zip_safe': False,
    'author': 'Lichun',
    'url': 'https://gitcafe.com/yuexue/unicode_tex',
    'classifiers': [
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python']
}

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(**sdict)
