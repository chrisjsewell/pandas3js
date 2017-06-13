#!/usr/bin/env python

#import math
import numpy as np
from numpy import radians, cos, sin, arccos, array
from matplotlib import cm
from matplotlib.colors import Normalize
import pandas as pd

def lattice_from_params(a, b, c, alpha, beta, gamma):
    """
    Compute lattice vectors from unit cell lengths and angles (in degrees).

    Properties
    ----------
    a : float
        *a* lattice parameter.
    b : float
        *b* lattice parameter.
    c : float
        *c* lattice parameter.
    alpha : float
        *alpha* angle in degrees.
    beta : float
        *beta* angle in degrees.
    gamma : float
        *gamma* angle in degrees.

    Returns
    -------
    lattice : list
        [array(ax,ay,az),array(bx,by,bz),array(cx,cy,cz)]
    
    Examples
    --------
    
    >>> a, b, c = lattice_from_params(1,2,3,90,90,90)
    >>> a.round()
    array([ 1.,  0.,  0.])
    
    >>> b= b.round()
    >>> b+0.
    array([ 0.,  2.,  0.])
    
    >>> c.round()
    array([ 0.,  0.,  3.])
        
    """
    alpha_r = radians(alpha)
    beta_r = radians(beta)
    gamma_r = radians(gamma)
    val = (cos(alpha_r) * cos(beta_r) - cos(gamma_r))\
        / (sin(alpha_r) * sin(beta_r))
    # Sometimes rounding errors result in |values| slightly > 1.
    val = val if val <= 1. else 1.
    val = val if val >= -1. else -1.
    
    gamma_star = arccos(val)
    vector_a = [a * sin(beta_r), 0.0, a * cos(beta_r)]
    vector_b = [-b * sin(alpha_r) * cos(gamma_star),
                b * sin(alpha_r) * sin(gamma_star),
                b * cos(alpha_r)]
    vector_c = [0.0, 0.0, float(c)]
    return [array(v) for v in (vector_a, vector_b, vector_c)]
    
def color_by_value(values, lbound=None, ubound=None, cmap='jet'):
    """ apply color map to values

    Properties
    ----------
    values : iter
        iterable of values
    lbound : float or None
        if not None, all values below will be same color
    ubound : float or None
        if not None, all values above will be same color
    cmap : str
        matplotlib colormap
    
    Returns
    -------
    colors : list of tuples
        r,g,b colors
    
    Examples
    --------
    >>> color_by_value([0,1])
    [(0.0, 0.0, 0.5), (0.5, 0.0, 0.0)]
    
    >>> color_by_value([-1,2],lbound=0,ubound=1)
    [(0.0, 0.0, 0.5), (0.5, 0.0, 0.0)]
    
    """
    colormap = cm.get_cmap(cmap)
    lbound = min(values) if lbound is None else lbound
    ubound = max(values) if ubound is None else ubound
    norm = Normalize(float(lbound),float(ubound),clip=True)
    colors = colormap(norm(values))
    # remove alphas
    return [tuple(col[:3]) for col in colors]

def color_by_category(values, cmap='jet'):
    """ apply color map to categories

    Properties
    ----------
    values : iter
        iterable of values
    cmap : str
        matplotlib colormap
    
    Returns
    -------
    colors : list of tuples
        r,g,b colors
    
    Examples
    --------
    >>> color_by_category(['a','b','b','a'])
    [(0.0, 0.0, 0.5), (0.5, 0.0, 0.0), (0.5, 0.0, 0.0), (0.0, 0.0, 0.5)]
    
    """
    colormap = cm.get_cmap('jet')
    cats = sorted(set(values))
    ncat = float(len(cats))
    cmap = {c:colormap(i/(ncat-1))[:3] for i,c in enumerate(cats)}
    return [cmap[v] for v in values]

def find_bonds(positions, ubound=4, 
               index=None, include_dist=False):
    """ find nearest-neighbour pairs
    
    Properties
    ----------
    positions : list of tuples
    ubound : float
        upper bound for nearest neighbour distance
    index : None or list
    include_dist : bool
        if True, include distance in tuple
    
    Examples
    --------
    >>> find_bonds([(0,0,0),(2,0,0),(5,0,0)])
    [((0, 0, 0), (2, 0, 0)), ((2, 0, 0), (5, 0, 0))]
    
    >>> find_bonds([(0,0,0),(2,0,0),(5,0,0)],
    ...            index=['a','b','c'])
    ...
    [('a', 'b'), ('b', 'c')]

    >>> find_bonds([(0,0,0),(2,0,0),(5,0,0)],
    ...            include_dist=True)
    ...
    [((0, 0, 0), (2, 0, 0), 2.0), ((2, 0, 0), (5, 0, 0), 3.0)]
    
    """
    try:
        import scipy
    except ImportError:
        return ImportError('scipy package required, please install') 
    from scipy.spatial import cKDTree
    from scipy.spatial.distance import euclidean
        
    if index is not None:
        assert len(positions)==len(index)
    
    tree = cKDTree(positions)
    pairs = tree.query_pairs(ubound)
    
    
    if index is not None:
        bonds = [tuple(sorted((index[i],index[j]))) for i,j in pairs]
    else:
        bonds = [(positions[i],positions[j]) for i,j in pairs]
        
    if include_dist:
        dists = [euclidean(positions[i],positions[j]) for i,j in pairs]
        bonds = [(i,j,d) for (i,j),d in zip(bonds,dists)]
    
    return bonds
 
def _new_id(id, current_ids):
    if isinstance(id, tuple):
        original = id[0]
    else:
        original = id
    
    new = (original, 1)
    while new in current_ids:
        new = (new[0],new[1]+1)
    return new

def repeat_cell(geometry,vector=[1,0,0],n=1):
    """ repeat geometry n times in vector direction
    ids are returned as tuple of (original, new)
    
    Examples
    --------
    
    >>> from pandas3js.models import GeometricObject, GeometricCollection
    >>> g = GeometricCollection()
    >>> g.add_object(GeometricObject(id=1,position=(0,0,0)))
    >>> g.add_object(GeometricObject(id=2,position=(0,0,1)))
    >>> repeat_cell(g,vector=[1,0,0],n=1)
    >>> repeat_cell(g,vector=[0,1,0],n=1)
    >>> for obj in g:
    ...     print('{0}: {1}'.format(obj.id,obj.position))
    ...
    1: (0.0, 0.0, 0.0)
    2: (0.0, 0.0, 1.0)
    (1, 1): (1.0, 0.0, 0.0)
    (2, 1): (1.0, 0.0, 1.0)
    (1, 2): (0.0, 1.0, 0.0)
    (2, 2): (0.0, 1.0, 1.0)
    (1, 3): (1.0, 1.0, 0.0)
    (2, 3): (1.0, 1.0, 1.0)
    
    """
    vector = np.array(vector)
    if n<0:
        n = abs(n)
        vector = -vector
    
    df = geometry.trait_df()
    new_df = repeat_cell_df(df,vector,n)
    
    geometry.change_by_df(new_df, otype_column='otype')

def repeat_cell_df(df,vector=[1,0,0],n=1):
    """ repeat geometry n times in vector direction
    ids are returned as tuple of (original, new)
    
    Examples
    --------
    see repeat_cell function
        
    """
    vector = np.array(vector)
    if n<0:
        n = abs(n)
        vector = -vector
    
    new_df = df.copy()

    for i in range(1,n+1):
        repeat_df = df.copy()
        current_ids = new_df.id.values.tolist()
        new_ids = []
        for id in repeat_df.id.values.tolist():
            new = _new_id(id,current_ids)
            new_ids.append(new)
            current_ids.append(new)
        repeat_df.id = new_ids
        repeat_df.position = repeat_df.position + vector*i
        new_df = pd.concat([new_df,repeat_df])
    
    return new_df

    
       
    
    
