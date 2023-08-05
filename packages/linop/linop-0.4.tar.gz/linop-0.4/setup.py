#!/usr/bin/env python

import os
import sys


DISTNAME = 'linop'
DESCRIPTION = 'linop: a Pythonic abstraction for linear mathematical operators'
LONG_DESCRIPTION = open('README.md').read()
MAINTAINER = 'Ghislain Vaillant'
MAINTAINER_EMAIL = 'ghisvail@gmail.com'
URL = 'https://github.com/ghisvail/linop'
LICENSE = 'LGPLv2'

version = '0.4'
release = True
if not release:
    version += '-dev'
VERSION = version


def configuration(parent_package='', top_path=None):
    # BEFORE importing distutils, remove MANIFEST. distutils doesn't properly
    # update it when the contents of directories change.
    if os.path.exists('MANIFEST'):
        os.remove('MANIFEST')
    from numpy.distutils.misc_util import Configuration
    config = Configuration(None, parent_package, top_path)
    config.set_options(ignore_setup_xxx_py=True,
                       assume_default_configuration=True,
                       delegate_options_to_subpackages=True,
                       quiet=True)
    config.add_subpackage('linop')
    return config


try:
    import setuptools
except ImportError:
    extra_setuptools_args = dict(
        zip_safe=False,
    )
else:
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
                    classifiers=["Development Status :: 3 - Alpha",
                                 'Intended Audience :: Developers',
                                 'Intended Audience :: Science/Research',
                                 'License :: OSI Approved',
                                 'Programming Language :: Python',
                                 'Topic :: Scientific/Engineering',
                                 'Topic :: Software Development',
                                 "Operating System :: OS Independent",
                                 'Programming Language :: Python :: 2',
                                 'Programming Language :: Python :: 2.6',
                                 'Programming Language :: Python :: 2.7',
                                 ],
                    **extra_setuptools_args)

    from numpy.distutils.core import setup
    metadata['configuration'] = configuration
    setup(**metadata)


if __name__ == '__main__':
    setup_package()
