#!/usr/bin/env python

from setuptools import setup, find_packages

setup ( \
    name = 'python-ovrsdk',
    version = '0.1.3',
    description = 'Python wrapper for Oculus VR SDK.',
    long_description = open('README.md', 'r').read(),
    author = 'Rye Terrell',
    author_email = 'wwwtyro@gmail.com',
    url = 'https://github.com/wwwtyro/python-ovrsdk',
    packages = ['ovrsdk', 'ovrsdk.windows'],
    package_data = {'': ['libovr.dll']}
)