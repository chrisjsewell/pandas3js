#!/usr/bin/env python
# -*- coding: utf-8 -*-

#TODO this doesn't work in doctest >>> import pandas as pd; str_to_obj('pd.DataFrame')  
#     but this does str_to_obj('pandas.DataFrame')


import os, sys, inspect
import importlib
import re
from matplotlib.colors import to_rgb
import numpy as np

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
def _natural_keys(text):
    return [text] if isinstance(text,float) else [_atoi(c) for c in re.split('(\d+)',str(text))]    
def natural_sort(iterable):
    """human order sorting of number strings 

    Examples
    --------
    
    >>> sorted(['011','1', '21'])
    ['011', '1', '21']
    
    >>> natural_sort(['011','1', '21'])
    ['1', '011', '21']
        
    """
    return sorted(iterable, key=_natural_keys)
    
def lighter_color(color, fraction=0.1):
    '''returns a lighter color
    
    Properties
    ----------
    color
        (r,g,b) tuple, hex or html color name
    fraction : float
        fraction to lighten by
        
    Examples
    --------
    >>> r,g,b = lighter_color('red')
    >>> '{0:.1f}, {1:.1f}, {2:.1f}'.format(r,g,b)
    '1.0, 0.1, 0.1'
        
    '''
    color = to_rgb(color)
    if fraction == 0.:
        return color
    assert fraction>0 and fraction<=1, 'fraction must be between 0 and 1'
    white = np.array([1., 1., 1.])
    vector = white-color
    r,g,b = color + vector * fraction
    return (r,g,b)

def tuple_to_df(df,col_name,value,index=None):
    """ a helper function for setting pandas dataframe 
    cell values as tuples
    
    df : pandas.DataFrame
    col_name : string
        name of column (can be new)
    value : tuple
    index : any
        if None set whole column
    
    """
    value = tuple(value)
    
    if col_name not in df:
        df[col_name] = np.nan
    df[col_name] = df[col_name].astype(object)
    if isinstance(index,list):
        for i in index:
            df.set_value(i,col_name,value)
    elif index is not None:
        df.set_value(index,col_name,value)
    else:
        for i in df.index:
            df.set_value(i,col_name,value)
    return
    
    
