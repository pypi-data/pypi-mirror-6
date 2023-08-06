dotter
======

.. image:: https://travis-ci.org/paetzke/dotter.png?branch=master
  :target: https://travis-ci.org/paetzke/dotter
.. image:: https://coveralls.io/repos/paetzke/dotter/badge.png?branch=master
  :target: https://coveralls.io/r/paetzke/dotter?branch=master
.. image:: https://pypip.in/v/dotter/badge.png
  :target: https://pypi.python.org/pypi/dotter/

Copyright (c) 2013, Friedrich Paetzke (f.paetzke@gmail.com)
All rights reserved.

Dotter is a graphviz wrapper for Python 2 and 3. In order to use it you need graphviz.
On Debian/Ubuntu you can install it by typing:

.. code:: bash

    $ apt-get install graphviz

After that install ``dotter`` via ``pip``.

.. code:: bash

    $ pip install dotter

.. image:: http://vanneva.com/static/images/dotter.png

An usage example:

.. code:: python

    from dotter import Dotter
    
    
    dotter = Dotter()
    
    dotter.add_node('a', label='b')
    dotter.add_node('b', label='c')
    dotter.add_edge('a', 'b')
    dotter.close()

CREDITS
-------

Thanks to:

* Russ Warren (https://github.com/rwarren) for adding style support

CHANGELOG
---------

0.4.0
~~~~~

* Add support for styling nodes

0.3.0
~~~~~

* Add method ``set_position()`` for setting position of a node.
* Switch from README.org to README.rst This enables you to install this package directly from a git repository.

0.2.0
~~~~~

* Enable setting output type by taking file extension

0.1.0
~~~~~

* Add PyPy support.

.. image:: https://d2weczhvl823v0.cloudfront.net/paetzke/dotter/trend.png
  :target: https://bitdeli.com/free

