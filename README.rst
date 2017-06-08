===========
pandas3js
===========

**Project**: https://github.com/chrisjsewell/pandas3js

.. image:: https://travis-ci.org/chrisjsewell/pandas3js.svg?branch=master
    :target: https://travis-ci.org/chrisjsewell/pandas3js

An extension for `traitlets <https://traitlets.readthedocs.io/en/stable/index.html>`_ and `pythreejs <https://github.com/jovyan/pythreejs>`_, which provides a 2-way `pandas <http://pandas.pydata.org/>`_ dataframe interface 
for trait objects and creates bespoke GUIs in the Jupyter Notebook with only a few lines of code.

Employing a meta Model/View design; Unique geometry objects are stored in a ``GeometryCollection`` **model** object, 
which can be viewed as (and modified by) a ``pandas.DataFrame``, containing objects (by row) and traits/object_type (by column). 
The ``GeometryCollection`` (and its objects) can then be directionally synced to a ``pythreejs.Scene`` (and ``pythreejs.3DObjects``) 
**view**, *via* a json mapping specification.

Installation
------------

.. parsed-literal::

    $ pip install pandas3js
    $ jupyter nbextension enable --py --sys-prefix pythreejs
	
``pandas3js`` is integration tested against python versions 2.7, 3.4, 3.5 and 3.6
    
Examples
---------

`pandas3js_example.ipynb <https://github.com/chrisjsewell/pandas3js/raw/master/pandas3js_example.ipynb>`_

.. image:: https://github.com/chrisjsewell/pandas3js/raw/master/pandas3js_example.gif

For more information, all functions contain docstrings with tested examples.


