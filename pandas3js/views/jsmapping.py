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
     'label_height':1,
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
     'label_height':1,
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
     'label_height':1,
    },
'pandas3js.models.idobject.TriclinicSolid':
    {'grep':'pythreejs.FaceGeometry',
     'gvar':{'facen':[
         [0,1,3,2],[0,4,6,2],[0,1,5,4],
         [6,7,3,2],[6,7,5,4],[7,5,1,3]
        ]},
     'gdmap':{}, 
     'gfmap':{'vertices':{'vars':('position','a','b','c','pivot'),
                          'func':'pandas3js.views.jsmapping._make_sbox_vertices'}},
     'matrep':'pythreejs.LambertMaterial', 
     'matvar':{'vertexColors':'FaceColors'},
     'matdmap':{'visible':'visible','opacity':'transparency'},
     'matfmap':{'transparent':{'vars':('transparency',),
                               'func':'pandas3js.views.jsmapping._transparent'},
              'color':{'vars':('color',),'func':'matplotlib.colors.to_hex'}},     

     'meshrep':'pythreejs.Mesh',
     'meshvar':{},
     'meshdmap':{},
     'meshfmap':{},

     'show_label':True,                             
     'label_height':1,
    },
'pandas3js.models.idobject.Plane':
    {'grep':'pythreejs.FaceGeometry',
     'gvar':{'face4':[0,1,2,3]},
     'gdmap':{}, 
     'gfmap':{'vertices':{'vars':('position','normal','width'),
                          'func':'pandas3js.views.jsmapping._make_plane_vertices'}},
     'matrep':'pythreejs.LambertMaterial', 
     'matvar':{'vertexColors':'FaceColors'},
     'matdmap':{'visible':'visible','opacity':'transparency'},
     'matfmap':{'transparent':{'vars':('transparency',),
                               'func':'pandas3js.views.jsmapping._transparent'},
              'color':{'vars':('color',),'func':'matplotlib.colors.to_hex'}},     

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

    vertices = np.array([o,o+c,o+b,o+b+c,o+a,
                o+a+c,o+a+b,o+a+b+c])
    return vertices.flatten().tolist()

def _make_plane_vertices(position,normal,width):
    """make plane vertices"""    

    a,b,c = normal

    if c==0:
        if b==0:
            x1,y1,z1 = 0, 1, 1
        else:
            x1,z1 = 1, 1
            y1 = (- a*x1 - c*z1)/float(b)
    else:
        x1,y1 = 1, 1
        z1 = (- a*x1 - b*y1)/float(c)
    p1 = np.array((x1,y1,z1))/np.linalg.norm((x1,y1,z1))
    p2 = np.cross(normal/np.linalg.norm(normal),p1/np.linalg.norm(p1))

    position = np.array(position)
    v1 = p1*.5*width + position
    v2 = p2*.5*width + position
    v3 = -p1*.5*width + position
    v4 = -p2*.5*width + position

    vertices = np.array([v1,v2,v3,v4])
    return vertices.flatten().tolist()   