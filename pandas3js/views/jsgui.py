import ipywidgets as widgets

import pandas3js as pjs

def _create_callback(renderer, config_dict, select, ddown,
                     change_func, gcollect, all_options,
                     otype_column):
    def handle_ddown(change):
        with renderer.hold_trait_notifications():
            all_options[ddown.description] = ddown.value
            if config_dict is not None:
                geometry_df = change_func(config_dict[select.value], 
                                       all_options)
            else:
                geometry_df = change_func(None, all_options)
                
            gcollect.change_by_df(geometry_df,otype_column=otype_column,
                        otype_default='pandas3js.Sphere',
                                 remove_missing=True)        
    return handle_ddown

def create_gui(change_func, config_dict=None, 
               opts_dd=None,dd_min=3,
               opts_slide=None, opts_color=None,
               height=400,width=400, background='gray',
               view=(10,-10,-10,10),near=-10,
               add_objects=True, add_labels=True,
               otype_column=None):
    """ creates simple gui to handle geometric configuration changes,
    with a callback to update geometry according to options 

    Properties
    ----------
    change_func : function
        change_func(cdata,options_dict) -> pandas.DataFrame
        of geometric objects and traits
    config_dict : None or dict
        {config_name:cdata,...} pairs, 
        if not None, cdata is parsed to change_func for config_name selected
    opts_dd : None or dict
        {opt_name:list,...} create dropdown boxes with callbacks to change_func
    dd_min : int
        labels with less options will be displayed as 
        toggle buttons (therefore all visible)
    opts_slide : None or dict
        {opt_name:list,...} create select slider with callbacks to change_func
    opts_color : None or list
        {opt_name:init_color,...} create select color palette with callbacks to change_func
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
    >>> config_data = {'1':{'id':[0],'position':[(0,0,0)],
    ...                     'c1':'red','c2':'blue'},
    ...                '2':{'id':[0],'position':[(1,2,3)],
    ...                     'c1':'red','c2':'blue'}}
    ...
    >>> def change_func(cdata,options):
    ...     indf = pd.DataFrame(cdata)
    ...     ctype = options.get('color','c1')
    ...     indf['color'] = indf[ctype]
    ...     indf['label'] = 'myobject'
    ...     return indf[['id','position','color','label']]
    ...
    >>> gui, collect = pjs.create_gui(change_func,config_data,
    ...                     opts_dd={'color':['c1','c2']},
    ...                     opts_slide={'dummy':[1,2,3]})
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
    position                               (1.0, 2.0, 3.0)
    radius                                               1
    transparency                                         1
    visible                                           True
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
    position                               (0.0, 0.0, 0.0)
    radius                                               1
    transparency                                         1
    visible                                           True
    Name: 0, dtype: object
    >>> color_select = gui.children[0].children[1].children[0]
    >>> pjs.utils.obj_to_str(color_select)
    'ipywidgets.widgets.widget_selection.ToggleButtons'
    >>> color_select.value = 'c2'
    >>> collect.trait_df().loc[0]
    color                                             blue
    id                                                   0
    label                                         myobject
    label_color                                        red
    label_transparency                                   1
    label_visible                                    False
    otype                 pandas3js.models.idobject.Sphere
    position                               (0.0, 0.0, 0.0)
    radius                                               1
    transparency                                         1
    visible                                           True
    Name: 0, dtype: object
    
    """
    ## initialise renderer
    gcollect = pjs.GeometricCollection()
    scene = pjs.create_js_scene_view(gcollect,
                    add_objects=add_objects,add_labels=add_labels)
    camera, renderer = pjs.create_jsrenderer(scene,view=view,near=near,
                                height=height,width=width, background=background)
         
    ## initialise geometry in renderer                    

    # make sure options are available for initial update
    opts_dd = {} if opts_dd is None else opts_dd
    all_options = {label:options[0] for label, options in opts_dd.items()}
    opts_slide = {} if opts_slide is None else opts_slide
    all_options.update({label:options[0] for label, options in opts_slide.items()})
    opts_color = {} if opts_color is None else opts_color
    all_options.update({label:init for label, init in opts_color.items()})
    
    if len(all_options) != len(opts_dd)+len(opts_slide)+len(opts_color):
        raise ValueError('options in opts_dd, opts_slide, and opts_color are not unique')
    
    
    if not config_dict is None:    
        # sort number strings correctly
        dkeys = sorted(config_dict.keys(), key=pjs.utils.natural_keys)
        init_data = config_dict[dkeys[-1]]
    else:
        init_data = None
        

    with renderer.hold_trait_notifications():
        geometry_df = change_func(init_data,all_options)
        gcollect.change_by_df(geometry_df,otype_column=otype_column,
                    otype_default='pandas3js.Sphere',
                    remove_missing=True)      
    
    ## Create controls and callbacks
    controls = []

    # a slider for selecting the configuration
    if not config_dict is None:
        select = widgets.SelectionSlider(description='Configuration:',
                    value=dkeys[-1],options=dkeys, continuous_update=False)
        def handle_slider(change):
            with renderer.hold_trait_notifications():
                geometry_df = change_func(config_dict[change.new],all_options)
                gcollect.change_by_df(geometry_df,otype_column=otype_column,
                            otype_default='pandas3js.Sphere',
                            remove_missing=True)  
        select.observe(handle_slider,names='value')
        controls.append(select)
    else:
        select = None

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
        step=abs(right-left)/100.,
        description='axis range',
        readout_format='.1f',
        continuous_update=True,)
    def handle_axiszoom(change):
        camera.left =  camera.bottom = change.new[0]
        camera.right = camera.top = change.new[1]
    axiszoom.observe(handle_axiszoom,names='value')
    
    # add additional options
    opt_selectors = []

    for label, options in opts_dd.items():
        if len(options)==2 and True in options and False in options:
            ddown = widgets.Checkbox(value=options[0],
                description=label)
        elif len(options)< dd_min:
            ddown = widgets.ToggleButtons(options=options,
                            description=label,value=options[0])            
        else:
            ddown = widgets.Dropdown(options=options,
                            description=label,value=options[0])
        handle = _create_callback(renderer, config_dict, select, ddown,
                                 change_func, gcollect,all_options,
                                 otype_column)
        ddown.observe(handle, names='value')
        opt_selectors.append(ddown)
    
    for label, options in opts_slide.items():
        slide = widgets.SelectionSlider(description=label,
                    value=options[0],options=options, continuous_update=False)
        handle = _create_callback(renderer, config_dict, select, slide,
                                 change_func, gcollect,all_options,
                                 otype_column)
        slide.observe(handle, names='value')
        opt_selectors.append(slide)

    for label, option in opts_color.items():
        color = widgets.ColorPicker(description=label,
                    value=option, concise=False)
        handle = _create_callback(renderer, config_dict, select, color,
                                 change_func, gcollect,all_options,
                                 otype_column)
        color.observe(handle, names='value')
        opt_selectors.append(color)
        
    
    if opt_selectors:
        options = widgets.Tab(
            children=[widgets.VBox([widgets.HBox(controls),
                                   axiszoom]), 
                      widgets.VBox(opt_selectors)])
        options.set_title(0, 'Main Controls')
        options.set_title(1, 'Other Options')
    else:
        options = widgets.VBox([widgets.HBox(controls),
                               axiszoom])
    
    return widgets.VBox([options,
                         renderer]), gcollect