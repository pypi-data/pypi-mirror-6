#!/usr/bin/env python
from os.path import join, dirname
from setuptools import setup

with open(join(dirname(__file__), 'README.rst')) as f:
    long_description = f.read()

setup(
    name='google_play',
    author='Igor Skrynkovskyy',
    author_email='skrynkovskyy@gmail.com',
    description='Google Play app fetcher',
    long_description=long_description,
    license="MIT",
    url='https://github.com/h2rd/google_play',
    version='0.1',
    packages=['google_play'],
    test_suite='tests',
    install_requires=(
        'grab==0.4.13',
        'lxml==3.3.1',
        'requests==2.2.1'
    )
)
