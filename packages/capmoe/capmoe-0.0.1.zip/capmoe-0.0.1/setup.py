#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup


tests_require = [
    'nose',
    'coverage',
    'nose-cov',
    'nose-parameterized',
],

setup(
    name             = 'capmoe',
    description      = 'CapMoe - Cap Beer cap image search, CLI tools and APIs',
    long_description = open('README.rst').read(),
    url              = 'https://github.com/laysakura/capmoe',
    license          = 'LICENSE.txt',
    version          = '0.0.1',
    author           = 'Sho Nakatani',
    author_email     = 'lay.sakura@gmail.com',
    tests_require    = tests_require,
    # Packages required to invoke `capmoe.api` functions.
    # Do not list cv libraries here.
    # They must be installed by hands.
    # This is because other packages who incokes `capmoe.api`
    # does not want to install cv libraries.
    install_requires = [
        'simplejson',
    ],
    extras_require = {
        'testing': tests_require,
    },
    packages = [
        'capmoe',
        'capmoe.api',
        'capmoe.cv',
    ],
    scripts = [
        'bin/capmoe-capdetector.py',
    ],
    classifiers = '''
Programming Language :: Python
Development Status :: 4 - Beta
Programming Language :: Python :: 2.7
Operating System :: POSIX :: Linux
'''.strip().splitlines()
)
