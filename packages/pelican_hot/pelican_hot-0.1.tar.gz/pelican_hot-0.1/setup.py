#!/usr/bin/env python
import os
from setuptools import setup

requires = ['pelican']

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
except IOError:
    README = ''

setup(
    name="pelican_hot",
    py_modules = ('pelican_hot',),
    version="0.1",
    author='Takahiro Fujiwara',
    author_email='email@wuta.li',
    url='https://github.com/wutali/pelican_hot',
    download_url='https://github.com/wutali/pelican_hot/tarball/master',
    description="A Pelican plugin to make a list of hot posts by social media.",
    long_description=README,
    include_package_data=True,
    install_requires=requires,
    classifiers=[],
)
