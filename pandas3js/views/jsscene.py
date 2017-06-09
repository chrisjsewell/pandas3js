#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pythreejs as js

from pandas3js.utils import str_to_obj, obj_to_str
from pandas3js.views.jsmesh import (create_jsmesh_view, 
                                create_jslabelmesh_view)
from pandas3js.models.idcollection import GeometricCollection


def create_js_scene_view(gcollect, add_objects=True, add_labels=False,
                        gobject_jsmap=None):
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
        if None use default gobject->jsobject mapping
                        
    Examples
    --------
    
    >>> from pandas3js.models import GeometricCollection, Sphere
    >>> collection = GeometricCollection()
    >>> scene = create_js_scene_view(collection,add_objects=True,add_labels=True)
    >>> [type(child) for child in scene.children]
    [<class 'pythreejs.pythreejs.AmbientLight'>]
                        
    >>> collection.add_object(Sphere(id=1))
    >>> [type(child) for child in scene.children]    
    [<class 'traitlets.traitlets.Sprite'>, <class 'traitlets.traitlets.Mesh'>, <class 'pythreejs.pythreejs.AmbientLight'>]
                        
    >>> sphere = collection.pop(1)
    >>> [type(child) for child in scene.children]
    [<class 'pythreejs.pythreejs.AmbientLight'>]
        
    """    
    assert isinstance(gcollect, GeometricCollection), 'gcollect must be a GeometricCollection'
    
    meshes = []
    for gobject in gcollect.idobjects:
        if add_labels:
            lmesh = create_jslabelmesh_view(gobject,gobject_jsmap)
            meshes.append(lmesh)
        if add_objects:
            gmesh = create_jsmesh_view(gobject,gobject_jsmap)
            meshes.append(gmesh)

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
            if add_labels:
                new_meshes.append(create_jslabelmesh_view(gobject,gobject_jsmap))
            if add_objects:
                new_meshes.append(create_jsmesh_view(gobject,gobject_jsmap))
                        
        scene.children = new_meshes + original_children

    gcollect.observe(gobjects_changed, names='idobjects')
    
    return scene