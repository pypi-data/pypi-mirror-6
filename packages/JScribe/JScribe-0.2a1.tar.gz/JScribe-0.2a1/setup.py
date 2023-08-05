# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""* Standard setup module for *pip*.
@module setup
"""

from distutils.core import setup


setup(
    name='JScribe',
    author='Rafał Łużyński',
    author_email='rafalluzynski@prosaur.com',
    version='0.2a1',
    packages=['jscribe',],
    py_modules=['jscribeit'],
    url='http://mindbrave.com/jscribe/docs/',
    license='LICENSE.txt',
    long_description=open('README.txt').read(),
    platforms=['linux', 'unix'],
    requires=[
        "Jinja2 (>=2.7.1)",
        "Markdown (>=2.3.1)",
        "Pygments (>=1.6)",
        "argparse (>=1.2.1)",
    ],
)

# INSTALL MANUAL
"""* Install.

pip install jscribe

@manual install "1. Installing"
"""
