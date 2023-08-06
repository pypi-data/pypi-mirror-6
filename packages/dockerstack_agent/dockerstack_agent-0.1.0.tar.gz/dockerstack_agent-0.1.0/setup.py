#!/usr/bin/env python

import dockerstack_agent.builder

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

packages = [
    'dockerstack_agent'
]

setup(
    name='dockerstack_agent',
    version=dockerstack_agent.builder.__version__,
    description='Build dockerfiles without docker',
    long_description='',
    author='Adam Thurlow',
    author_email='thurloat@gmail.com',
    url='https://bitbucket.org/clouda/dockerstack',
    packages=packages,
    scripts=['bin/dockerstack'],
    classifiers=(
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
)
