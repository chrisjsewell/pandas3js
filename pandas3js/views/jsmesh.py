#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

# rep=representation, var=static variable, 
# dmap=direct-mapping, fmap=functional-mapping
gobject_jsmapping = {
'pandas3js.models.idobject.Sphere':
    {'grep':'pythreejs.SphereGeometry',
     'gvar':{},
     'gdmap':{'radius':'radius'}, 
     'gfmap':{},
     
     'matrep':'pythreejs.LambertMaterial', 
     'matvar':{},
     'matdmap':{'visible':'visible','opacity':'transparency'},
     'matfmap':{'transparent':{'vars':('transparency',),
                               'func':'pandas3js.views.jsmesh._transparent'},
                'color':{'vars':('color',),'func':'matplotlib.colors.to_hex'}},

     'meshrep':'pythreejs.Mesh',
     'meshvar':{},
     'meshdmap':{},
     'meshfmap':{'position':{'vars':('x','y','z'),
                             'func':'pandas3js.views.jsmesh._tolist'}},
    
     'show_label':True,                             
     'label_height':'radius',
    },
'pandas3js.models.idobject.WireBox':
    {'grep':'pythreejs.PlainGeometry',
     'gvar':{},
     'gdmap':{}, 
     'gfmap':{'vertices':{'vars':('x','y','z','a','b','c'),
                          'func':'pandas3js.views.jsmesh._make_box_vertices'},
              'colors':{'vars':('color',),
                        'func':'pandas3js.views.jsmesh._make_box_colors'}},
     
     'matrep':'pythreejs.LineBasicMaterial', 
     'matvar':{'vertexColors':'VertexColors'},
     'matdmap':{'visible':'visible','opacity':'transparency','linewidth':'linewidth'},
     'matfmap':{'transparent':{'vars':('transparency',),
                               'func':'pandas3js.views.jsmesh._transparent'}},

     'meshrep':'pythreejs.Line',
     'meshvar':{'type':'LinePieces'},
     'meshdmap':{},
     'meshfmap':{},

     'show_label':False,                             
     'label_height':1,
    },
'pandas3js.models.idobject.Line':
    {'grep':'pythreejs.PlainGeometry',
     'gvar':{},
     'gdmap':{}, 
     'gfmap':{'vertices':{'vars':('start','end'),
                          'func':'pandas3js.views.jsmesh._tolist'},
              'colors':{'vars':('color',),
                        'func':'pandas3js.views.jsmesh._make_line_colors'}},
     
     'matrep':'pythreejs.LineBasicMaterial', 
     'matvar':{'vertexColors':'VertexColors'},
     'matdmap':{'visible':'visible','opacity':'transparency','linewidth':'linewidth'},
     'matfmap':{'transparent':{'vars':('transparency',),
                               'func':'pandas3js.views.jsmesh._transparent'}},

     'meshrep':'pythreejs.Line',
     'meshvar':{'type':'LinePieces'},
     'meshdmap':{},
     'meshfmap':{},

     'show_label':False,                             
     'label_height':1,
    },

}    

# function for mapping
def _tolist(*args):
    return list(args)
def _transparent(transparency):
    return True if transparency <= 0.999 else False  
def _make_box_vertices(x,y,z,a,b,c):
    """ make box vertices """
    o = np.array([x,y,z])
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    vertices = [o,o+a,
               o,o+b,
               o,o+c,
               o+b, o+b+a,
               o+b, o+b+c,
               o+a, o+b+a,
               o+a, o+a+c,
               o+c, o+c+a,
               o+c, o+c+b,
               o+b+c+a, o+b+c,
               o+b+c+a, o+b+a,
               o+b+c+a, o+c+a,
               ]
    return [v.tolist() for v in vertices]
def _make_box_colors(color):
    return [colors.to_hex(color)]*24
def _make_line_vertices(start,end):
    """ make box vertices """
    vertices = [start,end]
    return [v.tolist() for v in vertices]
def _make_line_colors(color):
    return [colors.to_hex(color)]*2


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
    class_str = obj_to_str(gobject)
    if not class_str in gobject_jsmapping:
        raise ValueError('No mapping available for {}'.format(class_str))
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

    mesh.add_traits(gobject_id=trait.Int())
    mesh.gobject_id = gobject.id
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
    class_str = obj_to_str(gobject)
    if not class_str in gobject_jsmapping:
        raise ValueError('No mapping available for {}'.format(class_str))
    class_map = gobject_jsmapping[class_str]
    
    text_map = js.TextTexture(string=gobject.label, 
                        color=colors.to_hex(gobject.label_color), 
                        size=100, squareTexture=False)
    material = js.SpriteMaterial(map=text_map,opacity=gobject.label_transparency,
                                transparent=False,depthTest=False,depthWrite=True)
    height = class_map['label_height']
    height_attr = getattr(gobject,height) if isinstance(height,basestring) else height
    mesh = js.Sprite(material=material, position=[gobject.x,gobject.y,gobject.z], 
                  scaleToTexture=True, 
                  scale=[1, height_attr, 1])
    mesh.add_traits(gobject_id=trait.Int())
    mesh.gobject_id = gobject.id
    
    if not class_map['show_label']:
        mesh.visible = True
        return mesh

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
