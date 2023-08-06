#!/usr/bin/env python

import os
import sys

import shams

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

packages = [
    'shams',
]

requires = [
    'factory-boy>=2.3.1',
    'django-localflavor==1.0',
]

with open('README.md') as f:
    readme = f.read()
with open('LICENSE') as f:
    license = f.read()

setup(
    name='shams',
    version=shams.__version__,
    description='A Python library for generating fake data',
    long_description=readme,
    author='David Gouldin',
    author_email='david@gould.in',
    url='https://github.com/dgouldin/python-shams',
    packages=packages,
    package_data={'': ['LICENSE']},
    package_dir={'shams': 'shams'},
    include_package_data=True,
    install_requires=requires,
    license=license,
    zip_safe=False,
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
)
