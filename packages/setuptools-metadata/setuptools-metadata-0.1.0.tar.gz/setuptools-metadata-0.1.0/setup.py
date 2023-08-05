#!/usr/bin/env python2.7

from setuptools import setup

entry_points = '''
[distutils.commands]
metadata = setuptools_metadata:metadata
'''

setup(
    author='Joost Molenaar',
    author_email='j.j.molenaar@gmail.com',
    url='https://github.com/j0057/setuptools-metadata',
    name='setuptools-metadata',
    version='0.1.0',
    py_modules=['setuptools_metadata'],
    entry_points={
        'distutils.commands': [
            'metadata = setuptools_metadata:metadata'
        ],
        'distutils.setup_keywords': [
            'custom_metadata = setuptools_metadata:validate_dict'
        ]
    })
