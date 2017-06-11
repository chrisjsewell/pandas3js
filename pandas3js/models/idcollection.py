#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO have way to specify object required without subclassing
#      otherwise might read in from local namespace

import traitlets as trait
import pandas as pd
import numpy as np

from pandas3js.models.idobject import IDObject, GeometricObject
from pandas3js.utils import obj_to_str, str_to_obj

class UniqueIDObjects(trait.TraitType):

    info_text = 'a collection of IDObjects with unique ids'
    default_value = ()
    
    def validate(self, obj, value):   
        
        if not value:
            return ()
        
        # all items must be ID objects
        if not all([isinstance(o, IDObject) for o in value]):
            self.error(obj, value)
        
        # all objects must have a unique id
        ids = [o.id for o in value]
        if len(ids) != len(set(ids)):
            self.error(obj, value)
            
        return tuple(value)
    
class IDCollection(trait.HasTraits):
    """ collection of IDObjects
    
    ensures each object has a unique id
    
    Examples
    --------
    
    >>> from pandas3js.models import IDCollection
    >>> c = IDCollection()
    >>> from pandas3js.models import IDObject
    >>> c.add_object(IDObject(id=1))
    >>> c.add_object(IDObject(id=2))
    >>> c.ids
    [1, 2]

    >>> c.add_object(IDObject(id=2))    
    Traceback (most recent call last):
     ...    
    ValueError: idobject is not a valid object or there is an id clash
    
    >>> c.get(2).id
    2
    >>> obj = c.pop(2)
    >>> c.ids
    [1]
        
    >>> obj  = IDObject(id=3)
    >>> from traitlets import Unicode
    >>> obj.add_traits(tname=Unicode('test'))
    >>> c.add_object(obj)
    >>> df = c.trait_df()
    >>> df
       id other_info                               otype tname
    0   1             pandas3js.models.idobject.IDObject   NaN
    1   3                   traitlets.traitlets.IDObject  test
    
    >>> df = df.set_value(1, 'tname', 'test2')
    >>> c.change_by_df(df, columns=['tname'])
    >>> c.trait_df()
       id other_info                               otype  tname
    0   1             pandas3js.models.idobject.IDObject    NaN
    1   3                   traitlets.traitlets.IDObject  test2
    
    >>> df = df.set_value(2, 'id', 5)
    >>> df.id = df.id.astype(int)
    >>> c.change_by_df(df, columns=['id'])
    >>> c.trait_df()
       id other_info                               otype  tname
    0   1             pandas3js.models.idobject.IDObject    NaN
    1   3                   traitlets.traitlets.IDObject  test2
    2   5             pandas3js.models.idobject.IDObject    NaN
    
    """
    # a list of all ID objects
    idobjects = UniqueIDObjects(read_only=True) 
    # used when reading df to check if valid object type
    _allowed_object = IDObject
        
    def add_object(self, idobject):
        """ add ID object
        """
        try:
            self.set_trait('idobjects', list(self.idobjects) + [idobject])
        except trait.TraitError as err:
            raise ValueError('idobject is not a valid object '
                             'or there is an id clash')          
                             #'or there is an id clash:\n{}'.format(err))
    
    def add_objects(self, idobjects):
        """ add ID objects
        """
        try:
            self.set_trait('idobjects', list(self.idobjects) + idobjects)
        except trait.TraitError as err:
            raise ValueError('idobject is not a valid object '
                             'or there is an id clash')          
                             #'or there is an id clash:\n{}'.format(err))
    
    def _get_ids(self):
        return [o.id for o in self.idobjects]
    ids = property(_get_ids)

    def get(self, id):
        """get idobject by id
        """
        return self.idobjects[self.ids.index(id)]
    
    def pop(self, id):
        """remove and return idobject by id """
        idobjects = list(self.idobjects)
        popped = idobjects.pop(self.ids.index(id))
        self.set_trait('idobjects',idobjects)
        return popped 
    
    def objects_with_trait(self, name, value=None):
        """ get all idobjects with certain trait
        
        name : str
            name of trait
        value
            if not None, only return idobjects with this trait value
        
        """
        idobjects = []
        for obj in self.idobjects:
            if obj.has_trait(name):
                if getattr(obj, name)==value or value is None:
                    idobjects.append(obj)
        return idobjects
            
    def change_by_df(self, df, columns=None, 
                     otype_default='pandas3js.models.IDObject', 
                     otype_column=None,
                    remove_missing=False):
        """ change collection by datafame of idobject traits
                    
        Properties
        ----------
        df : pd.DataFrame
            dataframe containing 'id' column
        columns : None or str
            use only these columns as attr, if None use all
        otype_default : str
            default ID object class to use
        otype_column : None or str
            if str, use this column to set the ID object class
        remove_missing : bool
            remove objects not present in dataframe
        
        """
        assert 'id' in df.columns
        if otype_column is not None:
            assert otype_column in df.columns, 'df does not contain specified otype column; {}'.format(otype_column)
        if not columns is None:
            assert set(df.columns).issuperset(columns), 'required columns not in df'
        assert df.id.nunique() == df.shape[0], "df id's are not unique"
        
        existing_ids = []
        old_objects = []
        
        # remove missing if required
        for obj in self.idobjects:
            existing_ids.append(obj.id)
            if obj.id in df.id.values or not remove_missing:
                old_objects.append(obj)
        
        new_objects = []
        new_traits = []
        
        for idx, s in df.iterrows():
             
            # create new objects
            if not s.id in existing_ids: 
                otype_name = otype_default if otype_column is None else s[otype_column]
                try:
                    idobject = str_to_obj(otype_name)()
                    assert isinstance(idobject, self._allowed_object), (
                        '{0} is not {1}'.format(idobject, self._allowed_object))
                except Exception as err:
                    raise TypeError(
                    '"{0}" (proposed for id {1}) is not a valid object: \n {2}'.format(otype_name, s.id, err))
                                    
                new_objects.append(idobject)
            
            else:
                idobject = self.get(s.id)
                        
            # TODO test object class is still the same
            # the process overhead for such a niche case might not be worth it ?
#            if otype_column is not None:   
#                otype_name = s[otype_column]              
#                try:
#                    newobject = str_to_obj(otype_name)()
#                    assert isinstance(newobject, self._allowed_object), (
#                        '{0} is not {1}'.format(newobject, self._allowed_object))
#                except Exception as err:
#                    raise TypeError(
#                    '"{0}" (proposed for id {1}) is not a valid object: \n {2}'.format(otype_name, s.id, err))
#                if not isinstance(newobject,idobject.__class__):
#                    old_objects.remove(idobject)
#                    new_objects.append(newobject)

            if not columns is None:
                s = s[columns]

            for key, value in s.iteritems():
                try:
                    if np.isnan(value):
                        continue
                except:
                    pass
                if key==otype_column:
                    continue
                if not idobject.has_trait(key):
                    raise trait.TraitError('object with id {0} does not have trait: {1}'.format(s.id, key))
                    
                # wait to set traits until all are objects are tested
                new_traits.append((idobject, key, value))
                    
        # hold trait notifications until all have been updated
        with idobject.hold_trait_notifications():
            for idobject, key, value in new_traits:
                    idobject.set_trait(key, value)

        self.set_trait('idobjects', tuple(old_objects + new_objects))               

        return

    def trait_df(self, traits=None, incl_class=True):
        """create dataframe of idobjects and their traits
        
        traits : None or list
            if not None, only include these traits in dataframe
        incl_class : bool
            if true, include 'otype' column with class type of idobject
        """
        data = []
        for obj in self.idobjects:
            trait_dict = {}
            for name in obj.trait_names():
                if traits is not None:
                    if name not in traits:
                        continue
                value = getattr(obj, name)
                # might break df if cell value is a list
                value = tuple(value) if isinstance(value, list) else value
                trait_dict[name] = value

            if incl_class:
                trait_dict['otype'] = obj_to_str(obj)

            data.append(trait_dict)
            
        return pd.DataFrame(data)

class UniqueGObjects(trait.TraitType):

    info_text = 'a collection of GeometricObjects with unique ids'
    default_value = ()
    
    def validate(self, obj, value):   
        
        if not value:
            return ()
        
        # all items must be ID objects
        if not all([isinstance(o, GeometricObject) for o in value]):
            self.error(obj, value)
        
        # all objects must have a unique id
        ids = [o.id for o in value]
        if len(ids) != len(set(ids)):
            self.error(obj, value)
            
        return tuple(value)

class GeometricCollection(IDCollection):
    """ collection of GeometricObjects
    
    ensures each object has a unique id
    
    Examples
    --------
    
    >>> test_dict = {'id':[0,1,2],
    ...  'position':[(0,0,0),(-1,-1,0),(1,1,1)],
    ... 'color':['red']*3,'transparency':[1]*3,'radius':[1]*3,
    ... 'label':['H']*3, 'otype':['pandas3js.models.Sphere']*3}
    ...
    >>> df = pd.DataFrame(test_dict)
    
    >>> c = GeometricCollection()
    >>> c.change_by_df(df, otype_column='otype')
    >>> trait_df = c.trait_df(traits=['id', 'position','radius','label'])
    >>> trait_df
       id label                             otype           position  radius
    0   0     H  pandas3js.models.idobject.Sphere    (0.0, 0.0, 0.0)     1.0
    1   1     H  pandas3js.models.idobject.Sphere  (-1.0, -1.0, 0.0)     1.0
    2   2     H  pandas3js.models.idobject.Sphere    (1.0, 1.0, 1.0)     1.0
    
    >>> trait_df.radius = 2.5
    >>> trait_df = trait_df.loc[[0,2]]
    >>> c.change_by_df(trait_df, otype_column='otype', remove_missing=True)
    >>> c.trait_df(traits=['id', 'radius'], incl_class=False)
       id  radius
    0   0     2.5
    1   2     2.5
    
    """
    # a list of all geometric objects
    idobjects = UniqueGObjects(read_only=True)
    _allowed_object = GeometricObject
