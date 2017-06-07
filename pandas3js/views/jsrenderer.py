#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pythreejs as js

def create_jsrenderer(scene, height=400,width=400, background='gray',
                      view=(10,-10, -10, 10), near=-10):
    """
    
    Properties
    ----------
    view : tuple
        view extents: (top, bottom, left, right)
    
    Returns
    -------
    camera : pythreejs.Camera
    renderer : pythreejs.Renderer
                      
    Examples
    --------
    
    >>> import pythreejs as js
    >>> scene = js.Scene(children=[js.AmbientLight(color='#777777')])
    >>> camera, renderer = create_jsrenderer(scene,200,200, 'gray', (1,-1,-1,1))
    >>> type(renderer)
    <class 'pythreejs.pythreejs.Renderer'>
    >>> type(camera)
    <class 'pythreejs.pythreejs.OrthographicCamera'>
    
    """
    top, bottom, left, right = view
    camera = js.OrthographicCamera(position=[0,0,1],
                                top=top, bottom=bottom, left=left, right=right,
                                near=near,far=2000,
                                children=[
                                    js.DirectionalLight(color='white', 
                                        position=[3, 5, 1], intensity=0.5)])
    control = js.OrbitControls(controlling=camera)
    renderer = js.Renderer(camera=camera,background=background,background_opacity=.1,
                        height=str(height),width=str(width),
                        scene=scene,controls=[control])
    return camera, renderer
