#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""a pandas dataframe interface for traitlets and pythreejs

"""

__version__ = '0.1.4.1'

from pandas3js import models
from pandas3js import views
from pandas3js import utils
from pandas3js import atom

def _run_nose_tests(doctests=True, verbose=True):
    """ 
    mimics nosetests --with-doctest -v --exe pandas3js 
    also use:
    pylint --output-format html pandas3js > pandas3js_pylint.html
    """
    import os, sys, pandas3js, nose
    nose_argv = sys.argv
    nose_argv += ['--detailed-errors', '--exe']
    if verbose:
        nose_argv.append('-v')
    if doctests:
        nose_argv.append('--with-doctest')
    nose_argv.append('pandas3js')
    initial_dir = os.getcwd()
    my_package_file = os.path.abspath(pandas3js.__file__)
    print(my_package_file)
    my_package_dir = os.path.dirname(os.path.dirname(my_package_file))
    print(my_package_dir)
    os.chdir(my_package_dir)
    try:
        nose.run(argv=nose_argv)
    finally:
        os.chdir(initial_dir)

