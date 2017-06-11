#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy

# python 3 to 2 compatibility
try:
    basestring
except NameError:
    basestring = str

import pythreejs as js
import traitlets as trait 
from matplotlib import colors
import numpy as np

from pandas3js.utils import str_to_obj, obj_to_str
from pandas3js.views.jsmapping import gobject_jsmapping

def _create_trait_dlink(dic, key, gobject, jsobject):
    # sync for jsobject to gobject trait value
    def trait_dlink(change):
        func = str_to_obj(dic['func'])
        value = func(*[getattr(gobject,v) for v in dic['vars']])
        jsobject.set_trait(key, value)
    # initialise jsobject to correct trait value
    trait_dlink(None)
    return trait_dlink

def create_jsmesh_view(gobject,mapping=None):
    """create PyThreeJS Mesh for GeometricObjects
    and with one-way synchronisation
    
    Properties
    ----------
    gobject : GeometricObject
    mapping : None or dict
        if None, use default gobject->jsobject mapping
    
    Examples
    --------
    
    >>> import pandas3js as pjs
    >>> sphere = pjs.models.Sphere()
    >>> mesh = create_jsmesh_view(sphere)
    >>> mesh.position
    [0.0, 0.0, 0.0]
    >>> str(mesh.material.color)
    '#ff0000'
    
    >>> sphere.position = (1,0,0)
    >>> mesh.position
    [1.0, 0.0, 0.0]
    
    >>> sphere.color = (1,1,1)
    >>> str(mesh.material.color)
    '#ffffff'
    
    >>> lmesh = create_jsmesh_view(pjs.models.Box())
    >>> lmesh = create_jsmesh_view(pjs.models.Line())
    >>> bsmesh = create_jsmesh_view(pjs.models.TriclinicSolid())
    >>> bwmesh = create_jsmesh_view(pjs.models.TriclinicWire())
    >>> cmesh = create_jsmesh_view(pjs.models.Circle())
    >>> mesh = create_jsmesh_view(pjs.models.Octahedron())
    >>> mesh = create_jsmesh_view(pjs.models.Icosahedron())
    >>> mesh = create_jsmesh_view(pjs.models.Plane())
    
    """
    class_str = obj_to_str(gobject)
    if hasattr(gobject, '_use_default_viewmap'):
        class_map = copy.deepcopy(gobject_jsmapping['default'])
        class_map['grep'] = 'pythreejs.{}Geometry'.format(class_str.split('.')[-1])
        # directly link all traits to geometry object traits
        for trait_name in gobject.class_own_traits():
            class_map['gdmap'][trait_name] = trait_name
        if gobject._use_default_viewmap is not None:
            class_map['show_label']=True
            class_map['label_height'] = gobject._use_default_viewmap
    elif not class_str in gobject_jsmapping:
        raise ValueError('No pythreejs mapping available for {}'.format(class_str))
    else:
        class_map = gobject_jsmapping[class_str]
    
    # create geometry
    geometry = str_to_obj(class_map['grep'])()
    
    for key, val in class_map['gvar'].items():
        geometry.set_trait(key, val)
    for key, val in class_map['gdmap'].items():
        trait.dlink((gobject, val), (geometry, key))
    for gkey, gdic in class_map['gfmap'].items():
        handle = _create_trait_dlink(gdic, gkey, gobject, geometry)
        gobject.observe(handle,names=gdic['vars'])
     
    # create material
    material = str_to_obj(class_map['matrep'])()
    
    for key, val in class_map['matvar'].items():
        material.set_trait(key, val)
    for key, val in class_map['matdmap'].items():
        trait.dlink((gobject, val), (material, key))
    for mkey, mdic in class_map['matfmap'].items():
        handle = _create_trait_dlink(mdic, mkey, gobject, material)
        gobject.observe(handle,names=mdic['vars'])

    # create mesh
    mesh = str_to_obj(class_map['meshrep'])(
                geometry=geometry,material=material)
    
    for key, val in class_map['meshvar'].items():
        mesh.set_trait(key, val)
    for key, val in class_map['meshdmap'].items():
        trait.dlink((gobject, val), (mesh, key))
    for skey, sdic in class_map['meshfmap'].items():
        handle = _create_trait_dlink(sdic, skey, gobject, mesh)
        gobject.observe(handle,names=sdic['vars'])

    # add special traits
    mesh.add_traits(gobject_id=trait.Int())
    mesh.gobject_id = gobject.id
    mesh.add_traits(other_info=trait.CUnicode())
    trait.dlink((gobject, 'other_info'), (mesh, 'other_info'))        
    
    return mesh

def create_jslabelmesh_view(gobject, mapping=None):
    """create PyThreeJS Text Mesh for GeometricObject
    and with one-way synchronisation

    Properties
    ----------
    gobject : GeometricObject
    mapping : None or dict
        if None, use default gobject->jsobject mapping

    Examples
    --------
    
    >>> import pandas3js as pjs
    >>> sphere = pjs.models.Sphere()
    >>> lmesh = create_jslabelmesh_view(sphere)
    >>> lmesh.position
    [0.0, 0.0, 0.0]
    >>> str(lmesh.material.map.string)
    '-'
    >>> lmesh.scale
    [1.0, 1.0, 1.0]
    
    >>> sphere.position = (1,0,0)
    >>> lmesh.position
    [1.0, 0.0, 0.0]
    
    >>> sphere.label = 'test'
    >>> str(lmesh.material.map.string)
    'test'
                  
    >>> sphere.radius = 3.0
    >>> lmesh.scale
    [1.0, 3.0, 1.0]
    
    """
    class_str = obj_to_str(gobject)
    if hasattr(gobject, '_use_default_viewmap'):
        class_map = copy.deepcopy(gobject_jsmapping['default'])
        class_map['grep'] = 'pythreejs.'+class_str.split('.')[-1]
        # directly link all traits to geometry object
        for trait_name in gobject.class_own_traits():
            class_map['gdmap'][trait_name] = trait_name
        if gobject._use_default_viewmap is not None:
            class_map['show_label']=True
            class_map['label_height'] = gobject._use_default_viewmap
    elif not class_str in gobject_jsmapping:
        raise ValueError('No pythreejs mapping available for {}'.format(class_str))
    else:
        class_map = gobject_jsmapping[class_str]
    
    text_map = js.TextTexture(string=gobject.label, 
                        color=colors.to_hex(gobject.label_color), 
                        size=100, squareTexture=False)
    material = js.SpriteMaterial(map=text_map,opacity=gobject.label_transparency,
                                transparent=False,depthTest=False,depthWrite=True)
    height = class_map['label_height']
    height_attr = getattr(gobject,height) if isinstance(height,basestring) else height
    mesh = js.Sprite(material=material, position=gobject.position, 
                  scaleToTexture=True, 
                  scale=[1, height_attr, 1])

    # add special traits
    mesh.add_traits(gobject_id=trait.Int())
    mesh.gobject_id = gobject.id
    mesh.add_traits(other_info=trait.CUnicode())    
    
    if not class_map['show_label']:
        mesh.visible = False
        return mesh

    # add directional synchronisation
    trait.dlink((gobject, 'other_info'), (mesh, 'other_info'))        
    trait.dlink((gobject, 'label'), (text_map, 'string'))
    trait.dlink((gobject, 'position'), (mesh, 'position'))
    trait.dlink((gobject, 'label_visible'), (mesh, 'visible'))
    trait.dlink((gobject, 'label_color'), (text_map, 'color'), colors.to_hex)
    trait.dlink((gobject, 'label_transparency'), (material, 'opacity'))
    trait.dlink((gobject, 'label_transparency'), (material, 'transparent'),
               lambda t: True if t <= 0.999 else False)

    if isinstance(height,basestring):
        def change_height(change):
            mesh.scale = [1, change.new, 1]
        gobject.observe(change_height,names=height)

    return mesh
