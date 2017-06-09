#!/usr/bin/env python
"""" contains mapping for pandas3js objects 
to pythreejs objects

keys:
    g = mapping to pythreejs.Geometry
    mat = mapping to pythreejs.Material
    mesh = mapping to pythreejs.Mesh

    rep  = subclass representation, 
    var  = static variable mapping, 
    dmap = direct object mapping, 
    fmap = functional mapping

    show_label = whether labels are required
    label_height = trait to link to label height

"""

from matplotlib import colors
import numpy as np

gobject_jsmapping = {
    
'default':
    {'grep':None,
     'gvar':{},
     'gdmap':{}, 
     'gfmap':{},
     
     'matrep':'pythreejs.LambertMaterial', 
     'matvar':{},
     'matdmap':{'visible':'visible','opacity':'transparency'},
     'matfmap':{'transparent':{'vars':('transparency',),
                               'func':'pandas3js.views.jsmapping._transparent'},
                'color':{'vars':('color',),'func':'matplotlib.colors.to_hex'}},

     'meshrep':'pythreejs.Mesh',
     'meshvar':{},
     'meshdmap':{'position':'position'},
     'meshfmap':{},
    
     'show_label':False,                             
     'label_height':None,
    },

'pandas3js.models.idobject.Line':
    {'grep':'pythreejs.PlainGeometry',
     'gvar':{},
     'gdmap':{}, 
     'gfmap':{'vertices':{'vars':('position','end'),
                          'func':'pandas3js.views.jsmapping._tolist'},
              'colors':{'vars':('color', 'end_color'),
                        'func':'pandas3js.views.jsmapping._make_line_colors'}},
     
     'matrep':'pythreejs.LineBasicMaterial', 
     'matvar':{'vertexColors':'VertexColors'},
     'matdmap':{'visible':'visible','opacity':'transparency','linewidth':'linewidth'},
     'matfmap':{'transparent':{'vars':('transparency',),
                               'func':'pandas3js.views.jsmapping._transparent'}},

     'meshrep':'pythreejs.Line',
     'meshvar':{'type':'LinePieces'},
     'meshdmap':{},
     'meshfmap':{},

     'show_label':False,                             
     'label_height':None,
    },
'pandas3js.models.idobject.TriclinicWire':
    {'grep':'pythreejs.PlainGeometry',
     'gvar':{},
     'gdmap':{}, 
     'gfmap':{'vertices':{'vars':('position','a','b','c','pivot'),
                          'func':'pandas3js.views.jsmapping._make_wbox_vertices'},
              'colors':{'vars':('color',),
                        'func':'pandas3js.views.jsmapping._make_wbox_colors'}},
     
     'matrep':'pythreejs.LineBasicMaterial', 
     'matvar':{'vertexColors':'VertexColors'},
     'matdmap':{'visible':'visible','opacity':'transparency','linewidth':'linewidth'},
     'matfmap':{'transparent':{'vars':('transparency',),
                               'func':'pandas3js.views.jsmapping._transparent'}},

     'meshrep':'pythreejs.Line',
     'meshvar':{'type':'LinePieces'},
     'meshdmap':{},
     'meshfmap':{},

     'show_label':False,                             
     'label_height':None,
    },
'pandas3js.models.idobject.TriclinicSolid':
    {'grep':'pythreejs.PlainGeometry',
     'gvar':{'faces':[
            [0, 1, 3],
            [0, 2, 3],
            [0, 2, 4],
            [2, 4, 6],
            [0, 1, 4],
            [1, 4, 5],
            [2, 3, 6],
            [3, 6, 7],
            [1, 3, 5],
            [3, 5, 7],
            [4, 5, 6],
            [5, 6, 7]
        ]},
     'gdmap':{}, 
     'gfmap':{'vertices':{'vars':('position','a','b','c','pivot'),
                          'func':'pandas3js.views.jsmapping._make_sbox_vertices'},
              'colors':{'vars':('color',),
                        'func':'pandas3js.views.jsmapping._make_sbox_colors'}},
# Not in current version
              # 'faceColors':{'vars':('color',),
              #           'func':'pandas3js.views.jsmapping._make_box_fcolors'}},
     
     'matrep':'pythreejs.LambertMaterial', 
     'matvar':{'vertexColors':'VertexColors'},
     'matdmap':{'visible':'visible','opacity':'transparency'},
     'matfmap':{'transparent':{'vars':('transparency',),
                               'func':'pandas3js.views.jsmapping._transparent'}},

     'meshrep':'pythreejs.Mesh',
     'meshvar':{},
     'meshdmap':{},
     'meshfmap':{},

     'show_label':True,                             
     'label_height':1,
    },
}    

# functions for mapping
def _tolist(*args):
    return list(args)
def _transparent(transparency):
    return True if transparency <= 0.999 else False  

def _make_line_colors(startcolor,endcolor):
    return [colors.to_hex(startcolor),colors.to_hex(endcolor)]

def _make_wbox_vertices(position,a,b,c,pivot):
    """ make box vertices """
    o = np.array(position)
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    if pivot == 'centre':
        o = o - (.5*a+.5*b+.5*c)
    elif not pivot == 'corner':
        raise ValueError('pivot must be centre or corner')

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
def _make_wbox_colors(color):
    return [colors.to_hex(color)]*24

def _make_sbox_vertices(position,a,b,c,pivot):
    """ make box vertices """
    o = np.array(position)
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    if pivot == 'centre':
        o = o - (.5*a+.5*b+.5*c)
    elif not pivot == 'corner':
        raise ValueError('pivot must be centre or corner')

    vertices = [o,o+c,o+b,o+b+c,o+a,
                o+a+c,o+a+b,o+a+b+c]
    return [v.tolist() for v in vertices]

def _make_sbox_colors(color):
    return [colors.to_hex(color)]*36
    