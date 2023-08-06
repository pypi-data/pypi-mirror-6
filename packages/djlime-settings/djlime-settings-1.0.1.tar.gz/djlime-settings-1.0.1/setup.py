#!/usr/bin/env python
from os.path import join, dirname
from setuptools import setup, find_packages


def long_description():
    try:
        return open(join(dirname(__file__), 'README.rst')).read()
    except IOError:
        return ''

setup(
    name='djlime-settings',
    version='1.0.1',
    author='Andrey Butenko',
    author_email='whitespysoftware@yandex.ru',
    url='https://github.com/whitespy/djlime-settings',
    description='The application settings.',
    long_description=long_description(),
    packages=find_packages(),
    include_package_data=True,
    platforms='any'
)
