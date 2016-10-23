"""
Super Simple Static Site Generator
------
"""
import sys
from setuptools import setup, find_packages


# get the version information
exec(open('ssssg/version.py').read())

setup(
    name = 'ssssg',
    packages = find_packages(),
    version = __version__,
    description = 'Static Site Generator number 1,000,000,000',
    url = 'https://github.com/emehrkay/ssssg',
    author = 'Mark Henderson',
    author_email = 'emehrkay@gmail.com',
    long_description = __doc__,
    classifiers = [],
)
