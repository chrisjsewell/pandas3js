import pandas as pd
import ipywidgets as widgets
import pythreejs as tjs

import pandas3js as pjs
from pandas3js.utils import natural_sort

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
               opts_range=None, 
               opts_color=None,
               tabs=None,
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
        NB : the first item will be initially set and then the list sorted
    opts_range : None or dict
        {opt_name:list,...} create select slider with callbacks to callback
        NB : the first item will be initially set and then the list sorted
    opts_color : None or list
        {opt_name:init_color,...} create select color palette with callbacks to callback
    tabs : None or dict
        {tab_name:list of opt names,..}, by default all go in 'Options' tab
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
    groups                                          (all,)
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
    groups                                          (all,)
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
    groups                                          (all,)
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
    tabs = {} if tabs is None else tabs
    # transpose tab dict
    opt_tab_map = {}
    for tabname,val in tabs.items():
        for item in val:
            if item in opt_tab_map:
                raise ValueError('option name in tabs occurs multiple times; {}'.format(item))
            opt_tab_map[item] = tabname
            
    controls = {}
    
    # a check box for showing labels
    if add_labels:    
        toggle=widgets.Checkbox(
        value=False,
        description='View Label:')
        def handle_toggle(change):
            for obj in gcollect.idobjects:
                obj.label_visible = change.new
        toggle.observe(handle_toggle,names='value')
        controls.setdefault('Main',[])
        controls['Main'].append(toggle)
    
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
            with renderer.hold_trait_notifications():
                camera.left = zoom * left
                camera.right = zoom * right
                camera.top = zoom * top
                camera.bottom = zoom * bottom
        axiszoom.observe(handle_axiszoom,names='value')
        controls.setdefault('Main',[])
        controls['Main'].append(axiszoom)
    
    # add additional options
    
    dd_min=4 # min amount of options before switch to toggle buttons
    for label in natural_sort(opts_choice):
        options = opts_choice[label]
        if (len(options)==2 and True in options and False in options 
            and isinstance(options[0],bool) and isinstance(options[1],bool)):
            ddown = widgets.Checkbox(value=options[0],
                description=label)
        elif len(options)< dd_min:
            ddown = widgets.ToggleButtons(options=natural_sort(options,True),
                            description=label,value=options[0])            
        else:
            ddown = widgets.Dropdown(options=natural_sort(options,True),
                            description=label,value=options[0])
        handle = _create_callback(renderer,ddown,callback, 
                                  gcollect,all_options)
        ddown.observe(handle, names='value')
        
        if label in opt_tab_map:
            controls.setdefault(opt_tab_map[label],[])
            controls[opt_tab_map[label]].append(ddown)
        else:
            controls.setdefault('Other',[])
            controls['Other'].append(ddown)
    
    for label in natural_sort(opts_range):
        options = opts_range[label]
        slider = widgets.SelectionSlider(description=label,
                    value=options[0],options=natural_sort(list(options),True), 
                    continuous_update=False)
        handle = _create_callback(renderer,slider,callback, 
                                  gcollect,all_options)
        slider.observe(handle, names='value')

        if label in opt_tab_map:
            controls.setdefault(opt_tab_map[label],[])
            controls[opt_tab_map[label]].append(slider)
        else:
            controls.setdefault('Other',[])
            controls['Other'].append(slider)

    for label in natural_sort(opts_color):
        option = opts_color[label]
        color = widgets.ColorPicker(description=label,
                    value=option, concise=False)
        handle = _create_callback(renderer, color,callback, 
                                  gcollect,all_options)
        color.observe(handle, names='value')

        if label in opt_tab_map:
            controls.setdefault(opt_tab_map[label],[])
            controls[opt_tab_map[label]].append(color)
        else:
            controls.setdefault('Other',[])
            controls['Other'].append(color)
    
    # add mouse hover information box
    # TODO doesn't work for orthographic https://github.com/jovyan/pythreejs/issues/101
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
        renderer = widgets.HBox([renderer,infobox])
        

    if controls:
        sheets = []
        sheet_names = []
        # main at start, other at end
        if 'Main' in controls:
            sheet_names.append('Main')
            sheets.append(widgets.VBox(controls.pop('Main')))        
        for tab_name, widg in controls.items():
            if tab_name == 'Other':
                continue
            sheet_names.append(tab_name)
            sheets.append(widgets.VBox(widg))            
        if 'Other' in controls:
            sheet_names.append('Other')
            sheets.append(widgets.VBox(controls.pop('Other')))
            
        options = widgets.Tab(children=sheets)
        for i, name in enumerate(sheet_names):
            options.set_title(i, name)
        
        return (widgets.VBox([options, renderer]),gcollect)
    else:
        return (renderer,gcollect)                                 
