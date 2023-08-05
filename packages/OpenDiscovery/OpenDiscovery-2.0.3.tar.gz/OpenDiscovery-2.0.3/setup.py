#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

long_description = 'OpenDiscovery'
if os.path.exists('README.txt'):
    long_description = open('README.txt').read()

setup(
    name='OpenDiscovery',
    version='2.0.3',
    release='0',
    description='Computational Drug Discovery Software',
    long_description=long_description,
    author='Gareth Price',
    author_email='gareth.price@warwick.ac.uk',
    url='https://github.com/iamgp/OpenDiscovery',
    packages=['OpenDiscovery', 'OpenDiscovery.pyPDB'],
    package_dir={'OpenDiscovery': 'OpenDiscovery'},
    package_data={'OpenDiscovery': ['lib/vina-osx/*', 'lib/vina-linux/*', 'lib/*.aw']},
    include_package_data=True,
    install_requires=[],
    license="GPL",
    keywords='OpenDiscovery',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
    ],
    scripts=['odscreen.py']
)