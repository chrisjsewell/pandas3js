#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" providing trait objects with an id

"""
#TODO inefficient to set x,y,z separately? 
#      ok if hol_trait_notifications and observing all names?

import traitlets as trait
from matplotlib import colors

class IDObject(trait.HasTraits):
    """ an object with an id
    
    """
    id = trait.Int(1)

class Color(trait.TraitType):
    """ a trait type that validates a color_like value:
    hex str, rgb/rgba tuple (0 to 1) or valid html name
    
    Examples
    --------
    
    >>> color = Color()
    >>> color.validate(object, (1,1,1))
    (1, 1, 1)
    >>> color.validate(object, 'red')
    'red'
    >>> color.validate(object, '#ff0000')
    '#ff0000'
    
    >>> try:
    ...     color.validate(object, 1)
    ...     print(True)
    ... except:
    ...     print(False)
    False
        
    """

    info_text = ('a color_like value: '
    'hex str, rgb/rgba tuple (0 to 1) or valid html name')
    default_value = 'red'
    
    def validate(self, obj, value):   
        
        if not colors.is_color_like(value):
            self.error(obj, value)
        
        if isinstance(value,list):
            value = tuple(value)
        
        return value

class GeometricObject(IDObject):
    """ a geometric object
    x,y,z should represent the centre of volume
    
    Examples
    --------
    
    >>> gobject = GeometricObject()
    >>> gobject.x
    0.0
    
    """
    x = trait.CFloat(0,help="x coordinate")
    y = trait.CFloat(0,help="y coordinate")
    z = trait.CFloat(0,help="z coordinate")

    visible = trait.Bool(True)
    color = Color('red')
    transparency = trait.CFloat(1,min=0.0,max=1.0)

    label = trait.CUnicode('-')
    label_visible = trait.Bool(False)
    label_color = Color('red')
    label_transparency = trait.CFloat(1,min=0.0,max=1.0)

class Sphere(GeometricObject):
    """ a spherical object
    """
    radius = trait.CFloat(1,min=0.)
    
def vector3(trait_type=trait.CFloat, default=None, **kwargs):
    if default is None:
        default = [0, 0, 0]
    return trait.List(trait_type, default_value=default, minlen=3, maxlen=3, **kwargs)

class WireBox(GeometricObject):
    """ a wireframe object
    """
    a = vector3(default=(1,0,0),help='box vector a')
    b = vector3(default=(0,1,0),help='box vector b')
    c = vector3(default=(0,0,1),help='box vector c')
    linewidth = trait.CFloat(1)
    
class Line(GeometricObject):
    
    start = vector3(default=(0,0,0))
    end = vector3(default=(1,1,1))
    linewidth = trait.CFloat(1)
    
    
    