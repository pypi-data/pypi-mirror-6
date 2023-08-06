#!/bin/env python

import sys

from setuptools import setup


VERSION = '0.5'


install_requires = [
    'requests',
    'pytz'
]

if sys.version_info < (3, 0):
    install_requires.append("email")

setup(
    name='kirrupt-tv',
    version=VERSION,
    description='A Python client for the Kirrupt TV API.',
    install_requires=install_requires,
    author='Kirrupt',
    author_email='info@kirrupt.com',
    url='https://github.com/kirrupt/kirrupt-tv-python-client',
    license='MIT',
    packages=['kirrupt_tv'],
    package_data={'': []},
    classifiers=(
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
)
