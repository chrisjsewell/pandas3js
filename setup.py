#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup for pandas3js"""

import io
from importlib import import_module
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with io.open('README.rst') as readme:
    setup(
        name='pandas3js',
        version=import_module('pandas3js').__version__,
        description='a pandas dataframe interface for traitlets and pythreejs',
        long_description=readme.read(),
        install_requires=requirements,
        license='MIT',
        author='Chris Sewell',
        author_email='chrisj_sewell@hotmail.com',
        url='https://github.com/chrisjsewell/pandas3js',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Environment :: Web Environment',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            #'Programming Language :: Python :: 3.2',
            #'Programming Language :: Python :: 3.3', # matplotlib requires Python 3.4 or later
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Topic :: Scientific/Engineering :: Chemistry',
            'Topic :: Scientific/Engineering :: Physics',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
        keywords='pythreejs, traitlets, graphics, 3D, pandas, ipython, jupyter, three.js, webgl',
        zip_safe=True,
        packages = find_packages(),
        package_data={'': ['*.csv','*.json']},
    )

