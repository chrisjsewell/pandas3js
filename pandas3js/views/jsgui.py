import pandas as pd
import ipywidgets as widgets
import pythreejs as tjs

import pandas3js as pjs

def _create_callback(renderer, option, callback, 
                     gcollect, all_options):
    """create a handler for an option control"""
    def handle_option(change):
        with renderer.hold_trait_notifications():
            all_options[option.description] = option.value
            callback(gcollect, all_options)
                
    return handle_option

def create_gui(geometry=None,callback=None,
               opts_choice=None,
               opts_range=None, opts_color=None,
               main_controls=None,
               height=400,width=400, background='gray',
               orthographic=False, camera_position=[0,0,-10],
               view=(10,-10,-10,10),fov=50,
               add_objects=True, add_labels=True,
               show_object_info=False,
               otype_column=None):
    """ creates simple gui to visualise 3d geometry,
    with a callback to update geometry according to option widgets 

    Properties
    ----------
    geometry : pandas3js.models.GeometricCollection
    callback : function
        callback(GeometricCollection, options_dict)
    opts_choice : None or dict
        {opt_name:list,...} create dropdown boxes with callbacks to callback
    opts_range : None or dict
        {opt_name:list,...} create select slider with callbacks to callback
    opts_color : None or list
        {opt_name:init_color,...} create select color palette with callbacks to callback
    main_controls : None or list
        options that will sit in the main controls section
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
    >>> data = {1:{'id':[0],'position':[(0,0,0)],
    ...              'c1':'red','c2':'blue'},
    ...         2:{'id':[0],'position':[(1,2,3)],
    ...               'c1':'red','c2':'blue'}}
    ...
    >>> def callback(geometry,options):
    ...     df = pd.DataFrame(data[options['config']])
    ...     ctype = options.get('color','c1')
    ...     df['color'] = df[ctype]
    ...     df['label'] = 'myobject'
    ...     df['otype'] = 'pandas3js.models.Sphere'
    ...     geometry.change_by_df(df[['id','position','otype',
    ...                               'color','label']],otype_column='otype')
    ...
    >>> gui, collect = pjs.views.create_gui(callback=callback,
    ...                     opts_choice={'color':['c1','c2']},
    ...                     opts_range={'config':[1,2]})
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
    position                               (0.0, 0.0, 0.0)
    radius                                               1
    transparency                                         1
    visible                                           True
    Name: 0, dtype: object
    >>> config_select = gui.children[0].children[1].children[1]
    >>> pjs.utils.obj_to_str(config_select)
    'ipywidgets.widgets.widget_selection.SelectionSlider'
    >>> config_select.value = 2
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
    position                               (1.0, 2.0, 3.0)
    radius                                               1
    transparency                                         1
    visible                                           True
    Name: 0, dtype: object
    
    """
    ## initialise renderer
    if geometry is None:
        gcollect = pjs.models.GeometricCollection()
    else:
        gcollect = geometry
    scene = pjs.views.create_js_scene_view(gcollect,
                    add_objects=add_objects,add_labels=add_labels)
    camera, renderer = pjs.views.create_jsrenderer(scene,
                                orthographic=orthographic, camera_position=camera_position,
                                view=view,fov=fov,
                                height=height,width=width, background=background)
            
    # creae minimal callback                    
    if callback is None:
        def callback(geometry, options):
            return
         
    ## initialise geometry in renderer                    

    # make sure options are available for initial update
    opts_choice = {} if opts_choice is None else opts_choice
    all_options = {label:options[0] for label, options in opts_choice.items()}
    opts_range = {} if opts_range is None else opts_range
    all_options.update({label:options[0] for label, options in opts_range.items()})
    opts_color = {} if opts_color is None else opts_color
    all_options.update({label:init for label, init in opts_color.items()})
    
    if len(all_options) != len(opts_choice)+len(opts_range)+len(opts_color):
        raise ValueError('options in opts_choice, opts_slide, and opts_color are not unique')
        
    with renderer.hold_trait_notifications():
        callback(gcollect, all_options)
    
    ## Create controls and callbacks
    main_controls = [] if main_controls is None else main_controls
    main_options = []
    other_options = []    

    # a check box for showing labels
    if add_labels:    
        toggle=widgets.Checkbox(
        value=False,
        description='View Label:')
        def handle_toggle(change):
            for obj in gcollect.idobjects:
                obj.label_visible = change.new
        toggle.observe(handle_toggle,names='value')
        main_options.append(toggle)
    
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
        main_options.append(axiszoom)
    
    # add additional options
    
    dd_min=3 # min amount of options before switch to toggle buttons
    for label, options in opts_choice.items():
        if len(options)==2 and True in options and False in options:
            ddown = widgets.Checkbox(value=options[0],
                description=label)
        elif len(options)< dd_min:
            ddown = widgets.ToggleButtons(options=options,
                            description=label,value=options[0])            
        else:
            ddown = widgets.Dropdown(options=options,
                            description=label,value=options[0])
        handle = _create_callback(renderer,ddown,callback, 
                                  gcollect,all_options)
        ddown.observe(handle, names='value')
        if label in main_controls:
            main_options.append(ddown)
        else:
            other_options.append(ddown)
    
    for label, options in opts_range.items():
        slider = widgets.SelectionSlider(description=label,
                    value=options[0],options=list(options), continuous_update=False)
        handle = _create_callback(renderer,slider,callback, 
                                  gcollect,all_options)
        slider.observe(handle, names='value')
        if label in main_controls:
            main_options.append(slider)
        else:
            other_options.append(slider)

    for label, option in opts_color.items():
        color = widgets.ColorPicker(description=label,
                    value=option, concise=False)
        handle = _create_callback(renderer, color,callback, 
                                  gcollect,all_options)
        color.observe(handle, names='value')
        if label in main_controls:
            main_options.append(color)
        else:
            other_options.append(color)
    
    if other_options:
        options = widgets.Tab(
            children=[widgets.VBox(main_options), 
                      widgets.VBox(other_options)])
        options.set_title(0, 'Main')
        options.set_title(1, 'Options')
    else:
        options = widgets.VBox(main_options)
    
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