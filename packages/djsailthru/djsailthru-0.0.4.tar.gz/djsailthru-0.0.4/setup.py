#!/usr/bin/env python
from setuptools import setup, find_packages
import os
import re

__doc__ = """
App for using Sailthru as a django email backend.
"""

def parse_requirements(file_name):
    requirements = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'(\s*#)|(\s*$)', line):
            continue
        if re.match(r'\s*-e\s+', line):
            # TODO support version numbers
            requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
        elif re.match(r'\s*-f\s+', line):
            pass
        else:
            requirements.append(line)

    return requirements


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='djsailthru',
    version="0.0.4",
    description=__doc__,
    long_description=read('README.rst'),
    url="https://github.com/fxdgear/djsailthru",
    author="Nick Lang",
    author_email='nick@nicklang.com',
    packages=[package for package in find_packages() if package.startswith('djsailthru')],
    install_requires=parse_requirements('requiremnts.txt'),
    zip_safe=False,
    include_package_data=True,
)
