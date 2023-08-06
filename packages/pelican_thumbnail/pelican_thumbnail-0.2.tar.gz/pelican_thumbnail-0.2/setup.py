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
    name="pelican_thumbnail",
    py_modules = ('pelican_thumbnail',),
    version="0.2",
    author='Takahiro Fujiwara',
    author_email='email@wuta.li',
    url='https://github.com/wutali/pelican_thumbnail',
    download_url='https://github.com/wutali/pelican_thumbnail/tarball/master',
    description="A Pelican plugin to add a thumbnail for the article.",
    long_description=README,
    include_package_data=True,
    install_requires=requires,
    classifiers=[],
)
