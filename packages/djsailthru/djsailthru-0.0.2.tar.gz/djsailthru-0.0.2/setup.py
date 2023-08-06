#!/usr/bin/env python
from setuptools import setup, find_packages
import os

__doc__ = """
App for using Sailthru as a django email backend.
"""


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='djsailthru',
    version="0.0.2",
    description=__doc__,
    long_description=read('README.rst'),
    url="https://github.com/fxdgear/djsailthru",
    author="Nick Lang",
    author_email='nick@nicklang.com',
    packages=[package for package in find_packages() if package.startswith('djsailthru')],
    install_requires=[
        'Django>=1.4',
        'sailthru-client>=2.1.3'
    ],
    zip_safe=False,
    include_package_data=True,
)
