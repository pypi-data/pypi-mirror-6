# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='linh',
    version='0.0.1',
    author=u'André Farzat',
    author_email='andrefarzat@gmail.com',
    packages=find_packages(),
    url='http://pypi.python.org/pypi/linh/',
    license='LICENSE',
    description='Linh is not HTML',
    long_description=open('README.md').read(),
    install_requires=["Django >= 1.5.0",],
    include_package_data=True,
    zip_safe=False,
)
