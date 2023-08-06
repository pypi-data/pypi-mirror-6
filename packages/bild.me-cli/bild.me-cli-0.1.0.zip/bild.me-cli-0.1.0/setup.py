#!/usr/bin/env python
# -*- coding: utf-8 -*-

from codecs import open
import sys
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import bild

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

requirements = [
    'requests>=2.0.1',
    'argparse',
]
packages = [
    'bild',
]


def long_description():
    readme = open('README.rst', encoding='utf8').read()
    text = readme + '\n\n' + open('CHANGELOG.rst', encoding='utf8').read()
    return text

setup(
    name='bild.me-cli',
    version=bild.__version__,
    description=bild.__doc__,
    long_description=long_description(),
    url='https://github.com/mozillazg/bild.me-cli',
    download_url='https://github.com/mozillazg/bild.me-cli/archive/master.zip',
    author=bild.__author__,
    author_email='mozillazg101@gmail.com',
    license=bild.__license__,
    packages=packages,
    package_data={'': ['LICENSE.rst']},
    package_dir={'bild': 'bild'},
    entry_points={
        'console_scripts': [
            'bild = bild.bild:main',
        ],
    },
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Environment :: Console',
        'Topic :: Utilities',
        'Topic :: Terminals',
    ],
    keywords='bild.me, CLI',
)
