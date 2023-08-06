#!/usr/bin/env python

import distutils.core

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py
import version

# Setup script for path

kw = {
    'name': 'path_helpers',
    'version': version.getVersion(),
    'description': 'Helper class and functions for working with file path',
    'author': 'Christian Fobel',
    'author_email': 'christian@fobel.net',
    'url': 'http://github.com/cfobel/path_helpers',
    'license': 'MIT License',
    'packages': ['path_helpers'],
    'cmdclass': dict(build_py=build_py),
}


# If we're running Python 2.3, add extra information
if hasattr(distutils.core, 'setup_keywords'):
    if 'classifiers' in distutils.core.setup_keywords:
        kw['classifiers'] = [
            'Development Status :: 5 - Production/Stable',
            'License :: OSI Approved :: MIT License',
            'Intended Audience :: Developers',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Software Development :: Libraries :: Python Modules']
    if 'download_url' in distutils.core.setup_keywords:
        urlfmt = 'http://github.com/cfobel/path_helpers/tarball/%s'
        kw['download_url'] = urlfmt % kw['version']


distutils.core.setup(**kw)
