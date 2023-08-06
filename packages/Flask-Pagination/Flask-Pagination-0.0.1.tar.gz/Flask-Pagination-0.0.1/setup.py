#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

requires = [
    'Flask>=0.9'
]

with open('README.rst') as f:
    readme = f.read()
with open('HISTORY.rst') as f:
    history = f.read()

setup(
    name='Flask-Pagination',
    version='0.0.1',
    description='Pagination Helpers for Flask Apps',
    long_description=readme + '\n\n' + history,
    author='Rhys Elsmore',
    author_email='me@rhys.io',
    url='https://github.com/rhyselsmore/flask-pagination',
    package_data={'': ['LICENSE', 'NOTICE']},
    py_modules=['flask_pagination'],
    include_package_data=True,
    install_requires=requires,
    license='Apache 2.0',
    zip_safe=False,
    classifiers=(
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
)