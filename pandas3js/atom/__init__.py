#!/usr/bin/env python

# python 2/3 compatibility
try:
    basestring
except NameError:
    basestring = str

import pandas as pd

from pandas3js.utils import get_data_path
from pandas3js.atom import data

from pandas3js.atom.utils import (lattice_from_params, 
                color_by_value, color_by_category, 
                find_bonds, repeat_cell)

def map_atoms(values,variable,index='Number'):
    """ map atoms to variable in atomic_data
    
    Properties
    ----------
    values : iter
    variable : str
        see below
    index : str
        Number, Symbol or Name

    Available Variables:
    Number - atomic number
    Symbol - elemental symbol                                                         
    Name - element name (in English)                                                 
    color - (r,g,b) defaults for visualization                              
    ARENeg - Allred and Rochow electronegativity  0.0 if unknown                     
    RCov - covalent radii (in Angstrom)         1.6 if unknown                     
      from http://dx.doi.org/10.1039/b801115j                              
    RBO - "bond order" radii -- ignored, but included for compatibility          
    RVdW - van der Waals radii (in Angstrom)       2.0 if unknown                     
      from http://dx.doi.org/10.1021/jp8111556                             
    MaxBnd - maximum bond valence           6 if unknown                                 
    Mass - IUPAC recommended atomic masses (in amu)                                 
    ElNeg - Pauling electronegativity           0.0 if unknown                         
    Ionization - ionization potential (in eV)         0.0 if unknown                    
    ElAffinity - electron affinity (in eV)            0.0 if unknown                    
    
    Examples
    --------
    >>> map_atoms([1,2,20],'Name')
    ['Hydrogen', 'Helium', 'Calcium']

    >>> map_atoms(['H','He','Ca'],'Mass',index='Symbol')
    [1.00794, 4.002602, 40.078]
    
    """
    assert index in ['Number', 'Symbol' or 'Name']
    if isinstance(values,int) or isinstance(values,basestring):
        values = [values]
        one_value = True
    else:
        one_value = False
    
    path = get_data_path('atomdata_map.csv',module=data)
    # initially leave as string, to avoid floating point issues
    df = pd.read_csv(path,comment='#',dtype=str)
    
    if variable=='color':
        red = df.Red
        green = df.Green
        blue = df.Blue    
        df['color'] = [(float(r),float(g),float(b)) for r,g,b in 
                        zip(red.values,green.values,blue.values)]                      
    
    df.set_index(index,inplace=True)
    vmap = df[variable].to_dict()

    if variable in ['Name', 'Symbol','color']:
        mapping = [vmap[str(v)] for v in values]
    else:
        mapping = [float(vmap[str(v)]) for v in values]
        
    return mapping[0] if one_value else mapping    
    
def atomic_data(atomic_number=None):
    """return a dataframe of atomic data, indexed by atomic number
    
    Properties
    ----------
    atomic_number : None or int
        if int, return pandas.Series of data for that atomic_number
    
    Available Columns:
    Symbol - elemental symbol                                                         
    Name - element name (in English)                                                 
    color - (r,g,b) defaults for visualization                              
    ARENeg - Allred and Rochow electronegativity  0.0 if unknown                     
    RCov - covalent radii (in Angstrom)         1.6 if unknown                     
      from http://dx.doi.org/10.1039/b801115j                              
    RBO - "bond order" radii -- ignored, but included for compatibility          
    RVdW - van der Waals radii (in Angstrom)       2.0 if unknown                     
      from http://dx.doi.org/10.1021/jp8111556                             
    MaxBnd - maximum bond valence           6 if unknown                                 
    Mass - IUPAC recommended atomic masses (in amu)                                 
    ElNeg - Pauling electronegativity           0.0 if unknown                         
    Ionization - ionization potential (in eV)         0.0 if unknown                    
    ElAffinity - electron affinity (in eV)            0.0 if unknown                    

    Examples
    --------
    
    >>> atomic_data(3).Name
    'Lithium'
    
    """
    path = get_data_path('atomdata_map.csv',module=data)
    df = pd.read_csv(path,comment='#')
    df.set_index('Number',inplace=True)
    df.index.name = 'atomic number'
    
    red = df.Red
    green = df.Green
    blue = df.Blue
    
    df['color'] = [(r,g,b) for r,g,b in 
                    zip(red.values,green.values,blue.values)]
                      
    df.drop(['Red','Green','Blue'],axis=1,inplace=True)
    
    if atomic_number is None:
        return df
    else:
        return df.loc[atomic_number]
