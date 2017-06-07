#!/usr/bin/env python
# -*- coding: utf-8 -*-

#TODO this doesn't work in doctest >>> import pandas as pd; str_to_obj('pd.DataFrame')  
#     but this does str_to_obj('pandas.DataFrame')


import os, sys, inspect
import importlib
import re

# python 2/3 compatibility
try:
    basestring
except NameError:
    basestring = str
try:
    import builtins
except ImportError:
    import __builtin__ as builtins
from functools import reduce
    
def get_data_path(data, module, check_exists=True):
    """return a directory path to data within a module

    data : str or list of str
        file name or list of sub-directories and file name (e.g. ['lammps','data.txt'])   
    """
    basepath = os.path.dirname(os.path.abspath(inspect.getfile(module)))
    
    if isinstance(data, basestring): data = [data]
    
    dirpath = os.path.join(basepath, *data)
    
    if check_exists:
        assert os.path.exists(dirpath), '{0} does not exist'.format(dirpath)
    
    return dirpath

def str_to_obj(class_str):
    """ get object from string
    
    creates object from string of module, 
    but without using unsecure eval operator
    
    Properties
    ----------
    class_str : str
        a string of an object
    
    Examples
    --------
    
    >>> print(str_to_obj('float')(2))
    2.0
    
    >>> print(str_to_obj('math.sqrt')(4.0))
    2.0
    
    >>> print(str_to_obj('numpy.array')([1,2,3]))
    [1 2 3]
    
    """
    
    # first try builtins like float, int, ...
    try:
        return reduce(getattr, 
                      class_str.split("."), 
                      builtins)
    except:
        pass

    # try obtaining from local namespace
    try:
        return reduce(getattr, 
                      class_str.split("."), 
                      sys.modules[__name__])      
    except:
        pass  
        
    if class_str.split(".")[0] in globals():
        module = globals()[class_str.split(".")[0]]
    else:
        module = importlib.import_module(class_str.split(".")[0])

    return reduce(getattr,class_str.split(".")[1:], module)

def obj_to_str(obj):
    """ get class string from object 
    
    Examples
    --------
    
    >>> print(obj_to_str([1,2,3]).split('.')[-1])
    list
    
    >>> import numpy as np
    >>> print(obj_to_str(np.array([1,2,3])))
    numpy.ndarray
       
    """
    mod_str = obj.__class__.__module__
    name_str = obj.__class__.__name__
    if mod_str=='__main__':
        return name_str 
    else :
        return '.'.join([mod_str,name_str])

def _atoi(text):
    return int(text) if text.isdigit() else text
def natural_keys(text):
    """human order sorting of number strings
    
    Examples
    --------
    
    >>> sorted(['011','1', '21'])
    ['011', '1', '21']
    
    >>> sorted(['011','1', '21'], key=natural_keys)
    ['1', '011', '21']
    
    """
    return [_atoi(c) for c in re.split('(\d+)',str(text))]
