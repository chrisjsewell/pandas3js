#!/usr/bin/env python

import math
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

def vector_norm(data, axis=None, out=None):
    """Return length, i.e. eucledian norm, of ndarray along axis.

    >>> v = np.random.random(3)
    >>> n = vector_norm(v)
    >>> np.allclose(n, np.linalg.norm(v))
    True
    >>> v = np.random.rand(6, 5, 3)
    >>> n = vector_norm(v, axis=-1)
    >>> np.allclose(n, np.sqrt(np.sum(v*v, axis=2)))
    True
    >>> n = vector_norm(v, axis=1)
    >>> np.allclose(n, np.sqrt(np.sum(v*v, axis=1)))
    True
    >>> v = np.random.rand(5, 4, 3)
    >>> n = np.empty((5, 3))
    >>> vector_norm(v, axis=1, out=n)
    >>> np.allclose(n, np.sqrt(np.sum(v*v, axis=1)))
    True
    >>> vector_norm([])
    0.0
    >>> vector_norm([1])
    1.0

    """
    data = np.array(data, dtype=np.float64, copy=True)
    if out is None:
        if data.ndim == 1:
            return math.sqrt(np.dot(data, data))
        data *= data
        out = np.atleast_1d(np.sum(data, axis=axis))
        np.sqrt(out, out)
        return out
    else:
        data *= data
        np.sum(data, axis=axis, out=out)
        np.sqrt(out, out)

def angle_between_vectors(v0, v1, directed=True, axis=0):
    """Return angle between vectors.

    If directed is False, the input vectors are interpreted as undirected axes,
    i.e. the maximum angle is pi/2.

    >>> a = angle_between_vectors([1, -2, 3], [-1, 2, -3])
    >>> np.allclose(a, math.pi)
    True
    >>> a = angle_between_vectors([1, -2, 3], [-1, 2, -3], directed=False)
    >>> np.allclose(a, 0)
    True
    >>> v0 = [[2, 0, 0, 2], [0, 2, 0, 2], [0, 0, 2, 2]]
    >>> v1 = [[3], [0], [0]]
    >>> a = angle_between_vectors(v0, v1)
    >>> np.allclose(a, [0, 1.5708, 1.5708, 0.95532])
    True
    >>> v0 = [[2, 0, 0], [2, 0, 0], [0, 2, 0], [2, 0, 0]]
    >>> v1 = [[0, 3, 0], [0, 0, 3], [0, 0, 3], [3, 3, 3]]
    >>> a = angle_between_vectors(v0, v1, axis=1)
    >>> np.allclose(a, [1.5708, 1.5708, 1.5708, 0.95532])
    True

    """
    v0 = np.array(v0, dtype=np.float64, copy=False)
    v1 = np.array(v1, dtype=np.float64, copy=False)
    dot = np.sum(v0 * v1, axis=axis)
    dot /= vector_norm(v0, axis=axis) * vector_norm(v1, axis=axis)
    return np.arccos(dot if directed else np.fabs(dot))

def cartesian_to_fractional(coords, a, b, c,origin=(0,0,0)):
    r""" transform from cartesian to crystal fractional coordinates
    
    Properties
    ------------        
    coords : numpy.array((N,3))
    a : numpy.array(3)
    b : numpy.array(3)
    c : numpy.array(3)
    origin : numpy.array(3)
    
    Examples
    --------
    >>> cartesian_to_fractional([[1,1,6]],[1,0,0],[0,2,0],[0,0,3])
    array([[ 1. ,  0.5,  2. ]])

    Notes
    -----
    From https://en.wikipedia.org/wiki/Fractional_coordinates
    
    .. math::
    
        \begin{bmatrix}x_{frac}\\y_{frac}\\z_{frac}\\\end{bmatrix}=
        \begin{bmatrix}{
        \frac {1}{a}}&-{\frac {\cos(\gamma )}{a\sin(\gamma )}}&{\frac {\cos(\alpha )\cos(\gamma )-\cos(\beta )}{av\sin(\gamma )}}\\
        0&{\frac {1}{b\sin(\gamma )}}&{\frac {\cos(\beta )\cos(\gamma )-\cos(\alpha )}{bv\sin(\gamma )}}\\
        0&0&{\frac {\sin(\gamma )}{cv}}\\\end{bmatrix}
        \begin{bmatrix}x\\y\\z\\\end{bmatrix}
        
    such that v is the volume of a unit parallelepiped defined as:
    
    .. math::

        v={\sqrt {1-\cos ^{2}(\alpha )-\cos ^{2}(\beta )-\cos ^{2}(\gamma )+2\cos(\alpha )\cos(\beta )\cos(\gamma )}}
        
    """
    # move to origin
    coords = np.asarray(coords) - np.asarray(origin)
    
    # create transform matrix
    a_norm = np.linalg.norm(a)
    b_norm = np.linalg.norm(b)
    c_norm = np.linalg.norm(c)

    alpha = angle_between_vectors(b,c)
    beta = angle_between_vectors(a,c)
    gamma = angle_between_vectors(a,b)
    
    if alpha==0 or beta==0 or gamma==0:
        raise ValueError('a,b,c do not form a basis')
    
    sin, cos = math.sin, math.cos
    cos_a = cos(alpha)
    cos_b = cos(beta)
    cos_g = cos(gamma)
    sin_g = sin(gamma)
    
    v = math.sqrt(1-cos_a**2-cos_b**2-cos_g**2+2*cos_a*cos_b*cos_g)
    
    conv_matrix = np.array([
        [1/a_norm, -(cos_g/(a_norm*sin_g)),(cos_a*cos_g-cos_b)/(a_norm*v*sin_g)],
        [0,        1/(b_norm*sin_g),       (cos_b*cos_g-cos_a)/(b_norm*v*sin_g)],
        [0,        0,                      sin_g/(c_norm*v)]])
    
    # transform        
    new_coords = np.dot(conv_matrix,coords.T).T
    
    return new_coords

def fractional_to_cartesian(coords, a, b, c,origin=(0,0,0)):
    r""" transform from crystal fractional coordinates to cartesian
    
    Properties
    ------------        
    coords : numpy.array((N,3))    
    a : numpy.array(3)    
    b : numpy.array(3)    
    c : numpy.array(3)    
    origin : numpy.array(3)
    
    Examples
    --------
    >>> fractional_to_cartesian([[1,1,1]],[1,0,0],[0,2,0],[0,0,3])
    array([[ 1.,  2.,  3.]])
    
    Notes
    -----
    From https://en.wikipedia.org/wiki/Fractional_coordinates
    
    .. math::
    
        \begin{bmatrix}x\\y\\z\\\end{bmatrix}=
        \begin{bmatrix}a&b\cos(\gamma )&c\cos(\beta )\\0&b\sin(\gamma )&c{\frac {\cos(\alpha )-\cos(\beta )\cos(\gamma )}{\sin(\gamma )}}\\0&0&c{\frac {v}{\sin(\gamma )}}\\\end{bmatrix}
        \begin{bmatrix}x_{frac}\\y_{frac}\\z_{frac}\\\end{bmatrix}
        
    such that v is the volume of a unit parallelepiped defined as:
    
    .. math::

        v={\sqrt {1-\cos ^{2}(\alpha )-\cos ^{2}(\beta )-\cos ^{2}(\gamma )+2\cos(\alpha )\cos(\beta )\cos(\gamma )}}
        
    """
    coords = np.asarray(coords)
    
    # create transform matrix
    a_norm = np.linalg.norm(a)
    b_norm = np.linalg.norm(b)
    c_norm = np.linalg.norm(c)

    alpha = angle_between_vectors(b,c)
    beta = angle_between_vectors(a,c)
    gamma = angle_between_vectors(a,b)
    
    if alpha==0 or beta==0 or gamma==0:
        raise ValueError('a,b,c do not form a basis')
    
    sin, cos = math.sin, math.cos
    cos_a = cos(alpha)
    cos_b = cos(beta)
    cos_g = cos(gamma)
    sin_g = sin(gamma)
    
    v = math.sqrt(1-cos_a**2-cos_b**2-cos_g**2+2*cos_a*cos_b*cos_g)
    
    conv_matrix = np.array([
        [a_norm,  b_norm*cos_g,       c_norm*cos_b                    ],
        [0,       b_norm*sin_g,       c_norm*(cos_a-cos_b*cos_a)/sin_g],
        [0,       0,                  c_norm*v/sin_g                  ]])
    
    # transform        
    new_coords = np.dot(conv_matrix,coords.T).T

    # move relative to origin
    coords = np.asarray(coords) + np.asarray(origin)
    
    return new_coords

def rotate_vectors(coords, axis, theta, origin=(0,0,0)):
    """rotate the coordinates clockwise about the given axis direction 
    by theta degrees.
    
    Properties
    ----------
    coords : iterable or list of iterables
        coordinates to rotate [x,y,z] or [[x1,y1,z1],[x2,y2,z2],...]
    axis : iterable
        axis to rotate around [x0,y0,z0] 
    theta : float
        rotation angle in degrees
    
    Examples
    --------
    >>> rotate_vectors([0,1,0],[0,0,1],90).round()
    array([[ 1.,  0.,  0.]])
    
    >>> rotate_vectors([[0,1,0],[1,0,0]],[0,0,1],90).round()
    array([[ 1.,  0.,  0.],
           [ 0., -1.,  0.]])
    
    >>> rotate_vectors([1,1,0],[0,0,1],90,[1,0,0]).round()
    array([[ 2.,  0.,  0.]])
    
    """
    # move to (0,0,0)
    coords = np.asarray(coords) - np.asarray(origin)    
    
    theta = -1*theta
    
    axis = np.asarray(axis)
    theta = np.asarray(theta)*np.pi/180.
    axis = axis/math.sqrt(np.dot(axis, axis))
    a = math.cos(theta/2.0)
    b, c, d = -axis*math.sin(theta/2.0)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
    rotation_matrix = np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                     [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                     [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]]) 
    
    rot_coords = np.array(np.einsum('ij,...j->...i',rotation_matrix,coords),ndmin=2) 
    
    return rot_coords + np.asarray(origin)        
    
