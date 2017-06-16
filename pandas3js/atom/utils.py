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
    
    Returns
    -------
    new_df : pandas.DataFrame
    
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

def matgen_struct(space_grp, species, fcoords, site_properties=None,
                     a=1, b=None,c=None,alpha=90,beta=None,gamma=None):
    """generate pymatgen structure
    
    Examples
    --------
    >>> struct = matgen_struct(229,['Fe'],[[0,0,0]],a=2.866)
    >>> struct.cart_coords
    array([[ 0.   ,  0.   ,  0.   ],
           [ 1.433,  1.433,  1.433]])
    >>> struct.atomic_numbers
    [26, 26]
    
    """
    try:
        import pymatgen.core.surface as surf
    except ImportError:
        raise ImortError('pymatgen is not installed')
                     
    b = a if b is None else b
    c = a if c is None else c
    beta = alpha if beta is None else beta
    gamma = alpha if gamma is None else gamma
    cell = surf.Lattice.from_parameters(
                a, b, c, alpha, beta, gamma)
    return surf.Structure.from_spacegroup(
                space_grp,cell,species, fcoords, site_properties)


def _align_rot_matrix(v1, v2):
    """get 3D rotation matrix to align v1 to v2
    
    v1 : np.array((3,))
    v2 : np.array((3,))
    
    From http://www.j3d.org/matrix_faq/matrfaq_latest.html#Q38
    """ 
    # Normalize vector length
    i_v_norm = v1 / np.linalg.norm(v1)
    f_v_norm = v2 / np.linalg.norm(v2)
    # Get axis
    uvw = np.cross(i_v_norm, f_v_norm)
    # compute trig values - no need to go through arccos and back
    rcos = np.dot(i_v_norm, f_v_norm)
    rsin = np.linalg.norm(uvw)
    #normalize and unpack axis
    if not np.isclose(rsin, 0):
        uvw /= rsin
    u, v, w = uvw
    # Compute rotation matrix - re-expressed to show structure
    return (
        rcos * np.eye(3) +
        rsin * np.array([
            [ 0,  w, -v],
            [-w,  0,  u],
            [ v, -u,  0]]) +
        (1.0 - rcos) * uvw[:,None] * uvw[None,:])

def realign_vectors(vectors,current_align,new_align):
    """
    vectors : np.array((N,3))
    current_align : np.array((3,))
    new_align : np.array((3,))
    
    Examples
    --------
    >>> realign_vectors(
    ...      [[1,0,0],[0,1,0],[0,0,1]],
    ...      [1,0,0],[0,1,0])
    ...
    array([[ 0.,  1.,  0.],
           [-1.,  0.,  0.],
           [ 0.,  0.,  1.]])
    
    """
    R = _align_rot_matrix(current_align,new_align)
    return np.einsum('...jk,...k->...j',R.T,vectors)    

def slice_mask(points, vector, 
               ubound=None, lbound=None,
              origin=(0,0,0)):
    """compute mask for points within the lower and upper planes
    
    Properties
    ----------
    points : array((N,3))
    vector : array((3,))
        the vector normal to the slice planes
    ubound : None or float
        the fractional length (+/-) along the vector to create the upper slice plane
    lbound : None or float
        the fractional length (+/-) along the vector to create the lower slice plane
    origin : array((3,))
        the origin of the vector
        
    Examples
    --------
    >>> points = [[0,0,-5],[0,0,0],[0,0,5]]
    >>> slice_mask(points,[0,0,1],ubound=1)
    array([ True,  True, False], dtype=bool)
    
    >>> slice_mask(points,[0,0,1],lbound=1)
    array([False, False,  True], dtype=bool)
    
    >>> slice_mask(points,[0,0,1],lbound=-1,ubound=1)
    array([False,  True, False], dtype=bool)
    
    >>> slice_mask(points,[0,0,1],lbound=1,origin=[0,0,2])
    array([False, False,  True], dtype=bool)
    
    """
    mask = np.array([True for _ in points])

    if ubound is not None:
        cpoints = np.array(points) - np.array(origin) - np.array(vector) * ubound
        mask = mask & (np.einsum('j,ij->i',vector,cpoints) <=0)
    if lbound is not None:
        cpoints = np.array(points) - np.array(origin) - np.array(vector) * lbound
        mask = mask & (np.einsum('j,ij->i',vector,cpoints) >=0)

    return mask        
    
