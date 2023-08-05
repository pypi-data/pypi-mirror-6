#!/usr/bin/env python

import os
import sys
from setuptools import setup, find_packages


DISTNAME = 'linop'
DESCRIPTION = 'linop: a Pythonic abstraction for linear mathematical operators'
LONG_DESCRIPTION = open('README.md').read()
MAINTAINER = 'Ghislain Vaillant'
MAINTAINER_EMAIL = 'ghisvail@gmail.com'
URL = 'https://github.com/ghisvail/linop'
LICENSE = 'LGPLv2'

version = '0.5'
release = True
if not release:
    version += '-dev'
VERSION = version


try:
    import setuptools
    extra_setuptools_args = dict(test_require=['nose', 'scipy'],
                                 test_suite="nose.collector",
                                 use_2to3=True,
                                 zip_safe=False)
except ImportError:
    extra_setuptools_args = dict()


def setup_package():
    metadata = dict(name=DISTNAME,
                    maintainer=MAINTAINER,
                    maintainer_email=MAINTAINER_EMAIL,
                    description=DESCRIPTION,
                    license=LICENSE,
                    url=URL,
                    version=VERSION,
                    long_description=LONG_DESCRIPTION,
                    classifiers=['Development Status :: 3 - Alpha',
                                 'Intended Audience :: Developers',
                                 'Intended Audience :: Science/Research',
                                 'License :: OSI Approved',
                                 'Programming Language :: Python',
                                 'Topic :: Scientific/Engineering',
                                 'Topic :: Software Development',
                                 'Operating System :: OS Independent',
                                 'Programming Language :: Python',
                                 'Programming Language :: Python :: 3',
                                 ],
                    **extra_setuptools_args)

    try:
        from setuptools import setup
    except ImportError:
        from distutils.core import setup

    metadata['packages'] = ['linop']
    setup(**metadata)


if __name__ == '__main__':
    setup_package()
