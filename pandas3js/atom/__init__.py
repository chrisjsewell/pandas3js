#!/usr/bin/env python

import pandas as pd

from pandas3js.utils import get_data_path
from pandas3js.atom import data

from pandas3js.atom.utils import vectors_from_params

def atomic_data(atomic_number=None):
    """return a dataframe of atomic data, indexed by atomic number
    
    Properties
    ----------
    atomic_number : None or int
        if int, return pandas.Series of data for that atomic_number
    
    Examples
    --------
    
    >>> atomic_data(3).Name
    'Lithium'
    
    """
    path = get_data_path('atomdata_map.csv',module=data)
    df = pd.read_csv(path,comment='#')
    df.rename(columns={'Symb':'Symbol'},inplace=True)
    df.set_index('Num',inplace=True)
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
