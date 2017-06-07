#!/usr/bin/env python

#import math
from numpy import radians, cos, sin, arccos, array

def vectors_from_params(a, b, c, alpha, beta, gamma):
    """
    Create a lattice using unit cell lengths and angles (in degrees).

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
        lattice with the specified lattice parameters
    
    Examples
    --------
    
    >>> a, b, c = vectors_from_params(1,2,3,90,90,90)
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
