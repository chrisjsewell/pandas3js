import ipywidgets as widgets

import pandas3js as pjs

def _create_callback(renderer, data, select, ddown,
                     change_func, gcollect, all_options,
                     otype_column):
    def handle_ddown(change):
        with renderer.hold_trait_notifications():
            all_options[ddown.description] = ddown.value
            geometry = change_func(data[select.value], 
                                   all_options)
            gcollect.change_by_df(geometry,otype_column=otype_column,
                        otype_default='pandas3js.Sphere',
                                 remove_missing=True)        
    return handle_ddown

def create_config_gui(data, change_func, 
                      height=400,width=400, background='gray',
                      view=(10,-10,-10,10),near=-10,
                      add_objects=True, add_labels=True,
                      add_options=None,
                      otype_column=None):
    """ creates simple gui to handle geometric configuration changes

    Properties
    ----------
    data : dict
        {config_name:cdata} pairs
    change_func : function
        change_func(cdata,options_dict) -> pandas.DataFrame
        of geometric objects and traits
    height : int
        renderer height
    width : int
        renderer width
    background : str
        renderer background color (html)
    view : tuple
        initial view extents (top,bottom,left,right)
    near : int
        camera distance from origin    
    add_objects : bool
        add objects to scene
    add_labels : bool
        add object labels to scene
    add_options : None or dict
        additional option lists, to create dropdown boxes 
        with callbacks to change_func as options dict
    otype_column : str
        column name for object type 
        in dataframe from change_func
    
    Returns
    -------
    gui : widgets.Box
        containing rendered scene and option widgets
    gcollect : pandas3js.GeometricCollection
        the collection of current geometric objects
        
    Examples
    --------

    >>> import pandas3js as pjs
    >>> import pandas as pd
    >>> data = {'1':{'id':[0],'x':[0],'y':[0],'z':[0],
    ...              'c1':'red','c2':'blue'},
    ...         '2':{'id':[0],'x':[1],'y':[2],'z':[3],
    ...              'c1':'red','c2':'blue'}}
    ...
    >>> def change_func(cdata,options):
    ...     indf = pd.DataFrame(cdata)
    ...     ctype = options.get('color','c1')
    ...     indf['color'] = indf[ctype]
    ...     indf['label'] = 'myobject'
    ...     return indf[['id','x','y','z','color','label']]
    ...
    >>> gui, collect = pjs.create_config_gui(data,change_func,
    ...                     add_options={'color':['c1','c2']})
    ...
    >>> [pjs.utils.obj_to_str(c) for c in gui.children]
    ['ipywidgets.widgets.widget_selectioncontainer.Tab', 'pythreejs.pythreejs.Renderer']
    >>> collect.trait_df().loc[0]
    color                                              red
    id                                                   0
    label                                         myobject
    label_color                                        red
    label_transparency                                   1
    label_visible                                    False
    otype                 pandas3js.models.idobject.Sphere
    radius                                               1
    transparency                                         1
    visible                                           True
    x                                                    1
    y                                                    2
    z                                                    3
    Name: 0, dtype: object
    >>> config_select = gui.children[0].children[0].children[0].children[0]
    >>> pjs.utils.obj_to_str(config_select)
    'ipywidgets.widgets.widget_selection.SelectionSlider'
    >>> config_select.value = '1'
    >>> collect.trait_df().loc[0]
    color                                              red
    id                                                   0
    label                                         myobject
    label_color                                        red
    label_transparency                                   1
    label_visible                                    False
    otype                 pandas3js.models.idobject.Sphere
    radius                                               1
    transparency                                         1
    visible                                           True
    x                                                    0
    y                                                    0
    z                                                    0
    Name: 0, dtype: object
    >>> color_select = gui.children[0].children[1].children[0]
    >>> pjs.utils.obj_to_str(color_select)
    'ipywidgets.widgets.widget_selection.Dropdown'
    >>> color_select.value = 'c2'
    >>> collect.trait_df().loc[0]
    color                                             blue
    id                                                   0
    label                                         myobject
    label_color                                        red
    label_transparency                                   1
    label_visible                                    False
    otype                 pandas3js.models.idobject.Sphere
    radius                                               1
    transparency                                         1
    visible                                           True
    x                                                    0
    y                                                    0
    z                                                    0
    Name: 0, dtype: object
    
    """
    controls = []
    all_options = {}
    
    # sort number strings correctly
    dkeys = sorted(data.keys(), key=pjs.utils.natural_keys)

    gcollect = pjs.GeometricCollection()
    scene = pjs.create_js_scene_view(gcollect,
                    add_objects=add_objects,add_labels=add_labels)
    camera, renderer = pjs.create_jsrenderer(scene,view=view,near=near,
                                height=height,width=width, background=background)
    
    # a slider for selecting the configuration
    select = widgets.SelectionSlider(description='Configuration:',
                options=dkeys, continuous_update=False)
    def handle_slider(change):
        with renderer.hold_trait_notifications():
            geometry = change_func(data[change.new],all_options)
            gcollect.change_by_df(geometry,otype_column=otype_column,
                        otype_default='pandas3js.Sphere',
                        remove_missing=True)        
    select.observe(handle_slider,names='value')
    select.value = dkeys[-1]
    controls.append(select)

    # a check box for showing labels
    if add_labels:    
        toggle=widgets.Checkbox(
        value=False,
        description='View Label:')
        def handle_toggle(change):
            for obj in gcollect.idobjects:
                obj.label_visible = change.new
        toggle.observe(handle_toggle,names='value')
        controls.append(toggle)
    
    # a zoom slider
    top,bottom,left,right = view
    axiszoom = widgets.FloatRangeSlider(
        value=[left,right],
        min=left,
        max=right,
        step=abs(right-left)/100,
        description='axis range',
        readout_format='.1f',
        continuous_update=True,)
    def handle_axiszoom(change):
        camera.left =  camera.bottom = change.new[0]
        camera.right = camera.top = change.new[1]
    axiszoom.observe(handle_axiszoom,names='value')
    
    # add additional options
    opt_dropdowns = []
    add_options = {} if add_options is None else add_options
    for label, options in add_options.items():
        ddown = widgets.Dropdown(options=options,
                        description=label,value=options[-1])
        handle = _create_callback(renderer, data, select, ddown,
                                 change_func, gcollect,all_options,
                                 otype_column)
        ddown.observe(handle, names='value')
        opt_dropdowns.append(ddown)
        ddown.value = options[0]
    
    if opt_dropdowns:
        options = widgets.Tab(
            children=[widgets.VBox([widgets.HBox(controls),
                                   axiszoom]), 
                      widgets.VBox(opt_dropdowns)])
        options.set_title(0, 'Main Controls')
        options.set_title(1, 'Other Options')
    else:
        options = widgets.VBox([widgets.HBox(controls),
                               axiszoom])
    
    return widgets.VBox([options,
                         renderer]), gcollect