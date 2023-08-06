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

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='confgen',
    version='0.1.4',
    description='ConfGen is a little command utility that will \
    help you to generate some configurations thanks to jinja2 templating',
    long_description=readme + '\n\n' + history,
    author='Natjohan',
    author_email='contact@natjohan.info',
    url='https://github.com/natjohan/confgen',
    packages=find_packages(),
    package_dir={'confgen': 'confgen'},
    include_package_data=True,
    install_requires=[
        'Jinja2==2.5',
    ],
    license="BSD",
    zip_safe=False,
    keywords='confgen',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Environment :: Console',
        'Topic :: Utilities',
    ],
    test_suite='tests',
    entry_points={
        "console_scripts": [
          "confgen = confgen.app:main",
        ],
      },
)