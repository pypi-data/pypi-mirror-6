#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""* Standard setup module for *pip*.
@module setup
"""

from distutils.core import setup


setup(
    name='JScribe',
    author='Rafał Łużyński',
    author_email='rafalluzynski@prosaur.com',
    version='0.2a4',
    packages=[
        'jscribe', 'jscribe.core', 'jscribe.conf', 'jscribe.generators',
        'jscribe.generators.html',
        'jscribe.templates', 'jscribe.templates.html', 'jscribe.templates.html.default',
        'jscribe.utils',
        'jscribe.test', 'jscribe.test.tests_core', 'jscribe.test.tests_utils'
    ],
    scripts=['jscribeit.py'],
    url='http://mindbrave.com/jscribe/docs/',
    license=open('LICENSE.txt').read(),
    long_description=open('README.txt').read(),
    platforms=['linux', 'unix'],
    data_files=[('templates', [
            'jscribe/templates/html/default/templates/default_element.html',
            'jscribe/templates/html/default/templates/element.html',
            'jscribe/templates/html/default/templates/element_contents.html',
            'jscribe/templates/html/default/templates/list.html',
            'jscribe/templates/html/default/templates/mainframe.html',
            'jscribe/templates/html/default/templates/sourcefile.html',
        ]),
        ('LICENSE.txt'),
        ('styles', ['jscribe/templates/html/default/style.css'])
    ],
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
