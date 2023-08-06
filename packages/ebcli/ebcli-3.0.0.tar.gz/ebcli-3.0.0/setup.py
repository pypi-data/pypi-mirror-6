#!/usr/bin/env python
import sys

from setuptools import setup
requires = ['requests>=2.2.1']

if sys.version_info[:2] == (2, 6):
    # For python2.6 we have to require argparse since it
    # was not in stdlib until 2.7.
    requires.append('argparse>=1.1')

setup_options = dict(
    name='ebcli',
    version='3.0.0',
    description='Command Line tool for ElasticBox.',
    long_description=open('README.rst').read(),
    author='ElasticBox',
    author_email='support@elasticbox.com',
    url='http://elasticbox.com',
    scripts=['eb'],
    py_modules=['ebcli'],
    install_requires=requires,
    license="Apache License 2.0",
    classifiers=(
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
)

setup(**setup_options)
