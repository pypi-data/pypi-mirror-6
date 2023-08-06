#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The Datakortet Javascript package, dk.js.
"""

classifiers = """\
Development Status :: 3 - Alpha
Intended Audience :: Developers
Programming Language :: Python
Topic :: Software Development :: Libraries
"""

import setuptools
from distutils.core import setup

version = eval(open('package.json').read())['version']

setup(
    name='dk',
    version=version,
    requires=[],
    install_requires=[],
    description=__doc__.strip(),
    classifiers=[line for line in classifiers.split('\n') if line],
    long_description=open('README.txt').read(),
    license="LGPL",
    author='Bjorn Pettersen',
    author_email='bp@datakortet.no',
    url='https://github.com/thebjorn/dk',
    download_url='https://github.com/thebjorn/dk',

    packages=['dk'],
    zip_safe=False,
)
