#!/usr/bin/env python


# FIXME: dirty hack to allow dist building on vagrant
# source: http://bugs.python.org/issue8876
# to build: $ python setup.py register sdist upload
import os
del os.link


import sys
from setuptools import setup, find_packages
from zlist._version import get_version

setup(
    name='zlist',
    version=get_version(),
    description='Parses your CSS files for z-index declarations and builds an ordered list of them.',
    author='James Tiplady',
    url='http://github.com/BigglesZX/zlist',
    packages=find_packages(),
    install_requires=['cssutils==1.0',],
    entry_points={
        'console_scripts': [
            'zlist = zlist.main:main',
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Information Technology',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Utilities',
    ],
)
