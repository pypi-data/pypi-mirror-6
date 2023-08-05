#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.md').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='config-sci',
    version='0.1.1',
    description='Python script for autoconfig SublimeCodeIntel',
    long_description=readme + '\n\n' + history,
    author='Yohan Graterol',
    author_email='yograterol@fedoraproject.org',
    url='https://github.com/yograterol/config-sci',
    packages=[
        'config_sci',
    ],
    package_dir={'config-sci': 'config-sci'},
    include_package_data=True,
    install_requires=[
    ],
    license="BSD",
    zip_safe=False,
    keywords='config-sci',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    entry_points={
        'console_scripts': [
            'config_sci = config_sci.config_sci:main',
        ]
    }
)
