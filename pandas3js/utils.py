#!/usr/bin/env python
# -*- coding: utf-8 -*-

#TODO this doesn't work in doctest >>> import pandas as pd; str_to_obj('pd.DataFrame')  
#     but this does str_to_obj('pandas.DataFrame')


import sys
import importlib
# python 2/3 compatibility
try:
    import builtins
except ImportError:
    import __builtin__ as builtins
from functools import reduce
    
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
    
    >>> print(str_to_obj('float'))
    <type 'float'>
    
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

def obj_to_classstr(obj):
    """ get class string from object 
    
    Examples
    --------
    
    >>> print(obj_to_classstr([1,2,3]))
    __builtin__.list
    
    >>> import numpy as np
    >>> print(obj_to_classstr(np.array([1,2,3])))
    numpy.ndarray
       
    """
    mod_str = obj.__class__.__module__
    name_str = obj.__class__.__name__
    if mod_str=='__main__':
        return name_str 
    else :
        return '.'.join([mod_str,name_str])
