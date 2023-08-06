#!/usr/bin/env python


# FIXME: dirty hack to allow dist building on vagrant
# source: http://bugs.python.org/issue8876
# to build: $ python setup.py register sdist upload
import os
del os.link

# FIXME: hack to prevent stack trace at the end of nose test run
# source: http://bugs.python.org/issue15881#msg170215
try:
    import multiprocessing
except ImportError:
    pass


import sys
from setuptools import setup, find_packages
from touchpaper._version import get_version

setup(
    name='touchpaper',
    version=get_version(),
    description='A command-line utility to quickly launch EC2 instances. A tasty accompaniment to Fabric.',
    author='James Tiplady',
    url='http://github.com/BigglesZX/touchpaper',
    packages=find_packages(),
    test_suite='nose.collector',
    tests_require=['nose==1.3.1', 'mock==1.0.1'],
    install_requires=['boto==2.23.0', 'colorama==0.2.7'],
    entry_points={
        'console_scripts': [
            'touchpaper = touchpaper.main:main',
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
)
