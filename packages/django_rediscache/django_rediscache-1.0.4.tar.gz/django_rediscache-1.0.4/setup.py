# -*- coding: utf-8 -*-
import codecs
import django_rediscache
import os.path

requires = (
    str('redis>=2.4.13'),
)
try:
    from setuptools import setup
    kwargs = {
        str('install_requires'): requires}
except ImportError:
    from distutils.core import setup
    kwargs = {
        str('requires'): requires}

version = ".".join((
    str(v) for v in django_rediscache.VERSION))

setup(
    name='django_rediscache',
    version=version,
    author_email='linkofwise@gmail.com',
    author='Michael Vorotyntsev',
    maintainer_email='linkofwise@gmail.com',
    packages=['django_rediscache'],
    long_description=codecs.open(
        os.path.realpath(
            os.path.join(
                os.path.dirname(__file__),
                'README.txt'))).read(),
    include_package_data=True,
    install_requires=[
        str('redis>=2.4.13'),
    ],
)
