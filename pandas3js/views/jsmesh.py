#!/usr/bin/env python
# -*- coding: utf-8 -*-

#TODO: sphere still hides label, even if opacity < 1
       # see: https://stackoverflow.com/a/15995475
       # ideally need to add renderorder to source code

import pythreejs as js
import traitlets as trait 
from matplotlib import colors


from pandas3js.utils import str_to_obj

def create_jsmesh_view(gobject, 
    grepr='pythreejs.SphereGeometry',gmap={'radius':'radius'},
    mrepr='pythreejs.LambertMaterial'):
    """create PyThreeJS Text Mesh for GeometricObject
    and with one-way synchronisation
    
    Properties
    ----------
    gobject : GeometricObject
    grepr : str
        pythreejs.Object3d representation 
    gmap : dict
        gobject attribute (key) to 
        pythreejs.Object3d representation attribute (value)
    mrepr : str
        pythreejs.Material representation
    
    Examples
    --------
    
    >>> from pandas3js import Sphere
    >>> sphere = Sphere()
    >>> mesh = create_jsmesh_view(sphere)
    >>> mesh.position
    [0.0, 0.0, 0.0]
    >>> str(mesh.material.color)
    '#ff0000'
    
    >>> sphere.x = 1.0
    >>> mesh.position
    [1.0, 0.0, 0.0]
    
    >>> sphere.color = (1,1,1)
    >>> str(mesh.material.color)
    '#ffffff'
    
    """
    gkwargs = {v:getattr(gobject, k) for k,v in gmap.items()}
    geometry = str_to_obj(grepr)(**gkwargs)

    material = str_to_obj(mrepr)(color=colors.to_hex(gobject.color),
                     opacity=gobject.transparency, transparent=True)

    mesh = js.Mesh(geometry=geometry,
                  material=material,
                  position=[gobject.x,gobject.y,gobject.z])
    mesh.add_traits(gobject_id=trait.Int())
    mesh.gobject_id = gobject.id

    # add directional synchronisation
    trait.dlink((gobject, 'visible'), (mesh, 'visible'))
    trait.dlink((gobject, 'color'), (material, 'color'), colors.to_hex)
    trait.dlink((gobject, 'transparency'), (material, 'opacity'))
    trait.dlink((gobject, 'transparency'), (material, 'transparent'),
               lambda t: True if t <= 0.999 else False)
    
    def change_position(change):
        mesh.position = [gobject.x,gobject.y,gobject.z]
    gobject.observe(change_position,names=['x','y','z'])

    for gattr, jsattr in gmap.items():
        trait.dlink((gobject, gattr), (geometry, jsattr))
    
    return mesh

def create_jslabelmesh_view(gobject,
                  height='radius'):
    """create PyThreeJS Text Mesh for GeometricObject
    and with one-way synchronisation

    Properties
    ----------
    gobject : GeometricObject
    height: float or str 
        if string, link to that gobject attribute

    Examples
    --------
    
    >>> from pandas3js import Sphere
    >>> sphere = Sphere()
    >>> lmesh = create_jslabelmesh_view(sphere)
    >>> lmesh.position
    [0.0, 0.0, 0.0]
    >>> str(lmesh.material.map.string)
    '-'
    >>> lmesh.scale
    [1.0, 1.0, 1.0]
    
    >>> sphere.x = 1.0
    >>> lmesh.position
    [1.0, 0.0, 0.0]
    
    >>> sphere.label = 'test'
    >>> str(lmesh.material.map.string)
    'test'
                  
    >>> sphere.radius = 3.0
    >>> lmesh.scale
    [1.0, 3.0, 1.0]

    """
    text_map = js.TextTexture(string=gobject.label, 
                        color=colors.to_hex(gobject.label_color), 
                        size=100, squareTexture=False)
    material = js.SpriteMaterial(map=text_map,opacity=gobject.label_transparency,
                                transparent=False)
    height_attr = getattr(gobject,height) if isinstance(height,basestring) else height
    mesh = js.Sprite(material=material, position=[gobject.x,gobject.y,gobject.z], 
                  scaleToTexture=True, 
                  scale=[1, height_attr, 1])
    mesh.add_traits(gobject_id=trait.Int())
    mesh.gobject_id = gobject.id

    # add directional synchronisation
    trait.dlink((gobject, 'label'), (text_map, 'string'))
    trait.dlink((gobject, 'label_visible'), (mesh, 'visible'))
    trait.dlink((gobject, 'label_color'), (text_map, 'color'), colors.to_hex)
    trait.dlink((gobject, 'label_transparency'), (material, 'opacity'))
    trait.dlink((gobject, 'label_transparency'), (material, 'transparent'),
               lambda t: True if t <= 0.999 else False)

    def change_position(change):
        mesh.position = [gobject.x,gobject.y,gobject.z]
    gobject.observe(change_position,names=['x','y','z'])

    if isinstance(height,basestring):
        def change_height(change):
            mesh.scale = [1, change.new, 1]
        gobject.observe(change_height,names=height)

    return mesh