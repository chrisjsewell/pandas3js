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
    other_info = trait.CUnicode('',help='other information about the object as HTML')

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
    ...     print('validated')
    ... except:
    ...     print('not validated')
    not validated
        
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

class Vector3(trait.TraitType):
    """ converts numpy arrays 
    """
    info_text = 'a 3d vector'
    default_value = (0.,0.,0.)
    def validate(self, obj, value):
        if isinstance(value,list) or isinstance(value,tuple):
            if len(value) != 3:
                self.error(value, value)
            else:
                new_value = value
        elif hasattr(value,'shape') and hasattr(value,'tolist'):
            if value.shape != (3,):
                self.error(obj, value)
            new_value = value.tolist()
        try:
            new_value = tuple([float(i) for i in new_value])
        except:
            self.error(obj, value)
        return new_value
                                    
class GeometricObject(IDObject):
    """ a geometric object
    x,y,z should represent the centre of volume
    
    Examples
    --------
    
    >>> gobject = GeometricObject()
    >>> gobject.position
    (0.0, 0.0, 0.0)
    
    """
    position = Vector3(default_value=(0,0,0),help='cartesian coordinate of pivot')

    visible = trait.Bool(True)
    color = Color('red')
    transparency = trait.CFloat(1,min=0.0,max=1.0)

    label = trait.CUnicode('-')
    label_visible = trait.Bool(False)
    label_color = Color('red')
    label_transparency = trait.CFloat(1,min=0.0,max=1.0)

def default_viewmap(label_height=None):
    """ a wrapper to signal that all
    subclass attributes should be directly linked to 
    the default view mapping
    
    Properties
    ----------
    label_height : None or str
        the attribute to link to label height
        if None, no label is created
    
    """
    def decorator(klass):
        setattr(klass, '_use_default_viewmap',label_height)
        return klass
    return decorator

@default_viewmap('radius')
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

# TODO orientation of default geometries
@default_viewmap('height')
class Box(GeometricObject):
    """ a spherical object

    Examples
    --------
    
    >>> object = Box()
    >>> object.position
    (0.0, 0.0, 0.0)

    """
    width = trait.CFloat(1)
    height = trait.CFloat(1)
    depth = trait.CFloat(1)

@default_viewmap('radius')
class Octahedron(GeometricObject):
    """ a spherical object

    Examples
    --------
    
    >>> object = Circle()
    >>> object.position
    (0.0, 0.0, 0.0)

    """
    radius = trait.CFloat(1)
    detail = trait.CFloat(0)    

@default_viewmap('radius')
class Icosahedron(GeometricObject):
    """ a spherical object

    Examples
    --------
    
    >>> object = Circle()
    >>> object.position
    (0.0, 0.0, 0.0)

    """
    radius = trait.CFloat(1)
    detail = trait.CFloat(0)    

@default_viewmap('radius')
class Circle(GeometricObject):
    """ a spherical object

    Examples
    --------
    
    >>> object = Circle()
    >>> object.position
    (0.0, 0.0, 0.0)

    """
    radius = trait.CFloat(1)
    segments = trait.CFloat(36)    

class Plane(GeometricObject):
    """ a plane object

    Examples
    --------
    
    >>> object = Plane()
    >>> object.position
    (0.0, 0.0, 0.0)

    """
    normal = Vector3(default_value=(0,0,1),help='the normal vector of the plane')
    width = trait.CFloat(1,min=0.0)

    @trait.validate('normal')
    def _valid_normal(self, proposal):
        x,y,z = proposal['value']
        if x==0 and y==0 and z==0:
            raise trait.TraitError('normal cannot be (0,0,0)')
        return proposal['value']        
    
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
    
    end = Vector3(default_value=(1,1,1),help='cartesian coordinate of line end')
    end_color = Color('red')
    linewidth = trait.CFloat(1,min=0.0)

# TDOD only development version of PlainGeometry exposes face colors
class TriclinicSolid(GeometricObject):
    """ a wireframe object

    Examples
    --------
    
    >>> box = TriclinicSolid()
    >>> box.position
    (0.0, 0.0, 0.0)
    >>> box.a
    (1.0, 0.0, 0.0)

    >>> try:
    ...     box.pivot = ''
    ... except Exception as err:
    ...     print(err)
    pivot must be at the centre or corner
        
    """
    a = Vector3(default_value=(1,0,0),help='box vector a')
    b = Vector3(default_value=(0,1,0),help='box vector b')
    c = Vector3(default_value=(0,0,1),help='box vector c')
    pivot = trait.CUnicode('centre',help='pivot about centre or corner')
    
    @trait.validate('pivot')
    def _valid_pivot(self, proposal):
        pivot = proposal['value']
        if pivot not in ['centre','corner']:
            raise trait.TraitError('pivot must be at the centre or corner')
        return proposal['value']        

class TriclinicWire(TriclinicSolid):
    """ a wireframe object

    Examples
    --------
    
    >>> box = TriclinicWire()
    >>> box.position
    (0.0, 0.0, 0.0)
    >>> box.a
    (1.0, 0.0, 0.0)

    >>> try:
    ...     box.linewidth = ''
    ... except:
    ...     print('not valid')
    not valid
        
    """
    linewidth = trait.CFloat(1)

    
    
    
    