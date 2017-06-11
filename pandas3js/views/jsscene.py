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
    
    Returns
    -------
    scene : pythreejs.Scene
        scene.children = [gobjcontainer,light]
                        
    Examples
    --------
    
    >>> from pandas3js.models import GeometricCollection, Sphere
    >>> collection = GeometricCollection()
    >>> scene = create_js_scene_view(collection,add_objects=True,add_labels=True)
    >>> container = scene.children[0]
    >>> [type(child) for child in container.children]
    []
                        
    >>> collection.add_object(Sphere(id=1))
    >>> [type(child) for child in container.children]    
    [<class 'traitlets.traitlets.Sprite'>, <class 'traitlets.traitlets.Mesh'>]
                        
    >>> sphere = collection.pop(1)
    >>> [type(child) for child in container.children]
    []
        
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

    # create dummy parent mesh to house all meshes, so we can use single mouse picker
    # NB: it would be better to use groups https://threejs.org/docs/#api/objects/Group
    # but this is not implemented in pythreejs
    gcontainer = js.Mesh(geometry=js.Geometry(), 
                   material=js.BasicMaterial(),
                   position=[0, 0, 0],
                   children=meshes)
            
    
    scenelight = js.AmbientLight(color='#777777')
    scene = js.Scene(children=[gcontainer,scenelight]) 
    
    def gobjects_changed(change):

        old = set(change.old)
        new = set(change.new)
        removed_objects = old.difference(new)
        added_objects = new.difference(old)

        if removed_objects:
            removed_ids = [o.id for o in removed_objects]
            original_children = []
            for child in gcontainer.children:
                if child.gobject_id not in removed_ids:
                    original_children.append(child)
        else:
            original_children = gcontainer.children

        new_meshes = []
        for gobject in added_objects:
            if add_labels:
                new_meshes.append(create_jslabelmesh_view(gobject,gobject_jsmap))
            if add_objects:
                new_meshes.append(create_jsmesh_view(gobject,gobject_jsmap))
                        
        gcontainer.children = new_meshes + original_children

    gcollect.observe(gobjects_changed, names='idobjects')
    
    return scene