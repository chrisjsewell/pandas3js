#!/usr/bin/env python
"""" contains mapping for pandas3js objects 
to pythreejs objects

keys:
    rep  = representation, 
    var  = static variable mapping, 
    dmap = direct object mapping, 
    fmap = functional mapping

"""

from matplotlib import colors
import numpy as np

gobject_jsmapping = {
'pandas3js.models.idobject.Sphere':
    {'grep':'pythreejs.SphereGeometry',
     'gvar':{},
     'gdmap':{'radius':'radius'}, 
     'gfmap':{},
     
     'matrep':'pythreejs.LambertMaterial', 
     'matvar':{},
     'matdmap':{'visible':'visible','opacity':'transparency'},
     'matfmap':{'transparent':{'vars':('transparency',),
                               'func':'pandas3js.views.jsmapping._transparent'},
                'color':{'vars':('color',),'func':'matplotlib.colors.to_hex'}},

     'meshrep':'pythreejs.Mesh',
     'meshvar':{},
     'meshdmap':{},
     'meshfmap':{'position':{'vars':('x','y','z'),
                             'func':'pandas3js.views.jsmapping._tolist'}},
    
     'show_label':True,                             
     'label_height':'radius',
    },
'pandas3js.models.idobject.WireBox':
    {'grep':'pythreejs.PlainGeometry',
     'gvar':{},
     'gdmap':{}, 
     'gfmap':{'vertices':{'vars':('x','y','z','a','b','c'),
                          'func':'pandas3js.views.jsmapping._make_box_vertices'},
              'colors':{'vars':('color',),
                        'func':'pandas3js.views.jsmapping._make_box_colors'}},
     
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
     'label_height':1,
    },
'pandas3js.models.idobject.Line':
    {'grep':'pythreejs.PlainGeometry',
     'gvar':{},
     'gdmap':{}, 
     'gfmap':{'vertices':{'vars':('start','end'),
                          'func':'pandas3js.views.jsmapping._tolist'},
              'colors':{'vars':('color',),
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
     'label_height':1,
    },

}    

# function for mapping
def _tolist(*args):
    return list(args)
def _transparent(transparency):
    return True if transparency <= 0.999 else False  
def _make_box_vertices(x,y,z,a,b,c):
    """ make box vertices """
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    #have x, y, z at centre of box
    o = np.array([x,y,z]) - (.5*a+.5*b+.5*c)

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
def _make_box_colors(color):
    return [colors.to_hex(color)]*24
def _make_line_vertices(start,end):
    """ make box vertices """
    vertices = [start,end]
    return [v.tolist() for v in vertices]
def _make_line_colors(color):
    return [colors.to_hex(color)]*2
