[![Build Status](https://travis-ci.org/chrisjsewell/pandas3js.svg?branch=master)](https://travis-ci.org/chrisjsewell/pandas3js)
[![Coverage Status](https://coveralls.io/repos/github/chrisjsewell/pandas3js/badge.svg?branch=master)](https://coveralls.io/github/chrisjsewell/pandas3js?branch=master)
[![PyPI](https://img.shields.io/pypi/v/pandas3js.svg)](https://pypi.python.org/pypi/pandas3js/)

# pandas3js

An extension for [traitlets](https://traitlets.readthedocs.io/en/stable/index.html) and [pythreejs](https://github.com/jovyan/pythreejs), which provides a 2-way [pandas](http://pandas.pydata.org/) dataframe interface for trait objects and creates bespoke GUIs in the Jupyter Notebook with only a few lines of code.

Employing a meta Model/View design; Unique geometry objects are stored in a `GeometryCollection` **model** object, 
which can be viewed as (and modified by) a `pandas.DataFrame`, containing objects (by row) and traits/object_type (by column). 
The `GeometryCollection` (and its objects) can then be directionally synced to a `pythreejs.Scene` (and `pythreejs.3DObject`s) **view**, *via* a json mapping specification.
    
## Examples

![pandas3js_example.ipynb](/pandas3js_example.ipynb)

![IPYNB Example](/pandas3js_example.gif)

For more information, all functions contain docstrings with tested examples.

## Installation

    $ pip install pandas3js
    $ jupyter nbextension enable --py --sys-prefix pythreejs
	
`pandas3js` is integration tested against python versions 2.7, 3.4, 3.5 and 3.6
