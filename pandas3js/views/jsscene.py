#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO think about using other objects to minimise render cost
#   in newer (unpublished pythreejs) their is buffergeometry and point 
#   https://github.com/jovyan/pythreejs/pull/68/commits/ff5e2d647132c747fc29f1d4594345aa01b9d8e3
#      BufferGeometry, https://threejs.org/docs/#api/core/BufferGeometry
#            NB: but might not be that fast when rendering a scene with many unique geometries;
#            https://github.com/mrdoob/three.js/issues/5186

import pythreejs as js

from pandas3js.utils import str_to_obj, obj_to_classstr
from pandas3js.views.jsmesh import (create_jsmesh_view, 
                                create_jslabelmesh_view)
from pandas3js.models.idcollection import GeometricCollection

gobject_jsmapping = {
'pandas3js.models.idobject.Sphere':{'grepr':'pythreejs.SphereGeometry',
        'gmap':{'radius':'radius'},
        'mrepr':'pythreejs.LambertMaterial'}   
}

glabel_jsmapping = {
'pandas3js.models.idobject.Sphere':{'height':'radius'}
}

def create_js_scene_view(gcollect, add_objects=True, add_labels=False,
                        gobject_jsmap=None, glabel_jsmap=None):
    """create PyThreeJS Scene for GeometricCollection
    and one-way link all GeometricObject attributes and creation/deletion

    Properties
    ----------
    gcollect : GeometricCollection
    add_objects: bool 
        add objects to scene
    add_labels : bool
        add object labels to scene
    gobject_jsmap : None or dict
        a mapping of object strings to create_jsmesh_view kwargs
    glabel_jsmap : None or dict
        a mapping of object strings to create_jslabelmesh_view kwargs
                        
    Examples
    --------
    
    >>> from pandas3js import GeometricCollection, Sphere
    >>> collection = GeometricCollection()
    >>> scene = create_js_scene_view(collection,add_objects=True,add_labels=True)
    >>> [type(child) for child in scene.children]
    [<class 'pythreejs.pythreejs.AmbientLight'>]
                        
    >>> collection.add_object(Sphere(id=1))
    >>> [type(child) for child in scene.children]    
    [<class 'traitlets.traitlets.Mesh'>, <class 'traitlets.traitlets.Sprite'>, <class 'pythreejs.pythreejs.AmbientLight'>]
                        
    >>> sphere = collection.pop(1)
    >>> [type(child) for child in scene.children]
    [<class 'pythreejs.pythreejs.AmbientLight'>]
        
    """    
    assert isinstance(gcollect, GeometricCollection), 'gcollect must be a GeometricCollection'
    if gobject_jsmap is None:
        gobject_jsmap = gobject_jsmapping
    if glabel_jsmap is None:
        glabel_jsmap = glabel_jsmapping
    
    meshes = []
    for gobject in gcollect.idobjects:
        if add_objects:
            gmesh = create_jsmesh_view(gobject,
                    **gobject_jsmap[obj_to_classstr(gobject)])
            meshes.append(gmesh)
        if add_labels:
            lmesh = create_jslabelmesh_view(gobject,
                    **glabel_jsmap[obj_to_classstr(gobject)])
            meshes.append(lmesh)

    scene = js.Scene(children=meshes+[js.AmbientLight(color='#777777')]) 
    
    def gobjects_changed(change):

        old = set(change.old)
        new = set(change.new)
        removed_objects = old.difference(new)
        added_objects = new.difference(old)

        if removed_objects:
            removed_ids = [o.id for o in removed_objects]
            original_children = []
            for child in scene.children:
                if child.has_trait('gobject_id'):
                    if child.gobject_id not in removed_ids:
                        original_children.append(child)
                else:
                    original_children.append(child)
        else:
            original_children = scene.children

        new_meshes = []
        for gobject in added_objects:
            if add_objects:
                new_meshes.append(create_jsmesh_view(gobject,
                    **gobject_jsmap[obj_to_classstr(gobject)]))
            if add_labels:
                new_meshes.append(create_jslabelmesh_view(gobject,
                    **glabel_jsmap[obj_to_classstr(gobject)]))
                        
        scene.children = new_meshes + original_children

    gcollect.observe(gobjects_changed, names='idobjects')
    
    return scene