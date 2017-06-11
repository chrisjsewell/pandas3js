import ipywidgets as widgets
import pythreejs as tjs

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
                        otype_default='pandas3js.models.Sphere',
                                 remove_missing=True)        
    return handle_ddown

def create_gui(change_func, config_dict=None, 
               opts_dd=None,dd_min=3,
               opts_slide=None, opts_color=None,
               height=400,width=400, background='gray',
               orthographic=False, camera_position=[0,0,-10],
               view=(10,-10,-10,10),fov=50,
               add_objects=True, add_labels=True,
               show_object_info=False,
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
    orthographic : bool
        use orthographic camera (True) or perspective (False) 
    camera_position : tuple
        position of camera in scene
    view : tuple
        initial view extents (top,bottom,left,right) (orthographic only)
    fov : float
        camera field of view (perspective only)
    add_objects : bool
        add objects to scene
    add_labels : bool
        add object labels to scene
    show_object_info : bool
        if True, show coordinate of object under mouse (currently only works for Perspective)
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
    >>> gui, collect = pjs.views.create_gui(change_func,config_data,
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
    other_info                                            
    otype                 pandas3js.models.idobject.Sphere
    position                               (1.0, 2.0, 3.0)
    radius                                               1
    transparency                                         1
    visible                                           True
    Name: 0, dtype: object
    >>> config_select = gui.children[0].children[0].children[0]
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
    other_info                                            
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
    other_info                                            
    otype                 pandas3js.models.idobject.Sphere
    position                               (0.0, 0.0, 0.0)
    radius                                               1
    transparency                                         1
    visible                                           True
    Name: 0, dtype: object
    
    """
    ## initialise renderer
    gcollect = pjs.models.GeometricCollection()
    scene = pjs.views.create_js_scene_view(gcollect,
                    add_objects=add_objects,add_labels=add_labels)
    camera, renderer = pjs.views.create_jsrenderer(scene,
                                orthographic=orthographic, camera_position=camera_position,
                                view=view,fov=fov,
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
                    otype_default='pandas3js.models.Sphere',
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
                            otype_default='pandas3js.models.Sphere',
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
    
    # zoom sliders for orthographic
    if orthographic:
        top,bottom,left,right = view
        axiszoom = widgets.FloatSlider(
            value=0,
            min=-10,
            max=10,
            step=0.1,
            description='zoom',
            continuous_update=True,)
        def handle_axiszoom(change):
            if change.new>1:
                zoom = 1./change.new
            elif change.new<-1:
                zoom = -change.new
            else:
                zoom = 1
            camera.left = zoom * left
            camera.right = zoom * right
            camera.top = zoom * top
            camera.bottom = zoom * bottom
        axiszoom.observe(handle_axiszoom,names='value')
        controls.append(axiszoom)
    
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
            children=[widgets.VBox(controls), 
                      widgets.VBox(opt_selectors)])
        options.set_title(0, 'Main Controls')
        options.set_title(1, 'Other Options')
    else:
        options = widgets.VBox(controls)
    
    # TDOD doesn't work for orthographic https://github.com/jovyan/pythreejs/issues/101
    if not orthographic and show_object_info:    
        # create information box
        click_picker = tjs.Picker(root=scene.children[0], event='mousemove')
        infobox = widgets.HTMLMath()
        def change_info(change):
            if click_picker.object:
                infobox.value = 'Object Coordinate: ({1:.3f}, {2:.3f}, {3:.3f})<br>{0}'.format(
                                    click_picker.object.other_info, *click_picker.object.position)
            else:
                infobox.value = ''
        click_picker.observe(change_info, names=['object'])
        renderer.controls = renderer.controls + [click_picker]

        return (widgets.VBox([options,
                             widgets.HBox([renderer,infobox])]), 
                gcollect)
                             
    return (widgets.VBox([options,
                         renderer]), 
           gcollect)