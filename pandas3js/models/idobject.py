#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" providing trait objects with an id

"""
#TODO inefficient to set x,y,z separately? 
#      ok if hol_trait_notifications and observing all names?
#TODO to/from pd.Series

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
    
    Examples
    --------
    
    >>> gobject = GeometricObject()
    >>> gobject.x
    0.0
    
    """
    x = trait.CFloat(0,help="the x coordinate")
    y = trait.CFloat(0,help="the y coordinate")
    z = trait.CFloat(0,help="the z coordinate")

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
    
atom = Sphere(transparency=0.1,label='zsdfsd')
atom.label