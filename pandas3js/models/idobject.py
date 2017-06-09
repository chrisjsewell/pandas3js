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
    ... except Exception as err:
    ...     print(err)
    The 'None' trait of a type instance must be a color_like value: hex str, rgb/rgba tuple (0 to 1) or valid html name, but a value of 1 <type 'int'> was specified.
        
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

def vector3(trait_type=trait.CFloat, default=None, **kwargs):
    if default is None:
        default = (0, 0, 0)
    return trait.Tuple(trait.CFloat(),trait.CFloat(),trait.CFloat(),
                    default_value=default, **kwargs)
                                    
class GeometricObject(IDObject):
    """ a geometric object
    x,y,z should represent the centre of volume
    
    Examples
    --------
    
    >>> gobject = GeometricObject()
    >>> gobject.position
    (0.0, 0.0, 0.0)
    
    """
    position = vector3(default=(0,0,0),help='cartesian coordinate of pivot')

    visible = trait.Bool(True)
    color = Color('red')
    transparency = trait.CFloat(1,min=0.0,max=1.0)

    label = trait.CUnicode('-')
    label_visible = trait.Bool(False)
    label_color = Color('red')
    label_transparency = trait.CFloat(1,min=0.0,max=1.0)

class Sphere(GeometricObject):
    """ a spherical object

    Examples
    --------
    
    >>> sphere = Sphere()
    >>> sphere.position
    (0.0, 0.0, 0.0)
    >>> sphere.radius
    1.0

    >>> try:
    ...     sphere.radius = -1
    ... except Exception as err:
    ...     print(err)
    The value of the 'radius' trait of a Sphere instance should not be less than 0.0, but a value of -1.0 was specified
    

    """
    radius = trait.CFloat(1,min=0.)
    

class Line(GeometricObject):
    """ a line object

    Examples
    --------
    
    >>> line = Line()
    >>> line.position
    (0.0, 0.0, 0.0)
    >>> line.end
    (1.0, 1.0, 1.0)

    >>> try:
    ...     line.linewidth = -1
    ... except Exception as err:
    ...     print(err)
    The value of the 'linewidth' trait of a Line instance should not be less than 0.0, but a value of -1.0 was specified
        
    """
    
    end = vector3(default=(1,1,1),help='cartesian coordinate of line end')
    end_color = Color('red')
    linewidth = trait.CFloat(1,min=0.0)

class BoxWire(GeometricObject):
    """ a wireframe object

    Examples
    --------
    
    >>> box = BoxWire()
    >>> box.position
    (0.0, 0.0, 0.0)
    >>> box.a
    (1.0, 0.0, 0.0)

    >>> box.pivot = ''
    Traceback (most recent call last):
     ...
    TraitError: pivot must be at the centre or corner
        
    """
    a = vector3(default=(1,0,0),help='box vector a')
    b = vector3(default=(0,1,0),help='box vector b')
    c = vector3(default=(0,0,1),help='box vector c')
    linewidth = trait.CFloat(1)
    pivot = trait.CUnicode('centre',help='pivot about centre or corner')
    
    @trait.validate('pivot')
    def _valid_pivot(self, proposal):
        pivot = proposal['value']
        if pivot not in ['centre','corner']:
            raise trait.TraitError('pivot must be at the centre or corner')
        return proposal['value']        
    
    
    
    