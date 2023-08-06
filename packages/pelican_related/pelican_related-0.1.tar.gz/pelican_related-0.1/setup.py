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
    name="pelican_related",
    py_modules = ('pelican_related',),
    version="0.1",
    author='Takahiro Fujiwara',
    author_email='email@wuta.li',
    url='https://github.com/wutali/pelican_related',
    download_url='https://github.com/wutali/pelican_related/tarball/master',
    description="A Pelican plugin to make a list of related posts from your meta tags and settings.",
    long_description=README,
    include_package_data=True,
    install_requires=requires,
    classifiers=[],
)
