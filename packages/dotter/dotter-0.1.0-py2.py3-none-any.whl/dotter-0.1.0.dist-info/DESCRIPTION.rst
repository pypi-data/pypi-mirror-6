dotter
======

.. image:: https://travis-ci.org/paetzke/dotter.png?branch=master
  :target: https://travis-ci.org/paetzke/dotter
.. image:: https://coveralls.io/repos/paetzke/dotter/badge.png?branch=master
  :target: https://coveralls.io/r/paetzke/dotter?branch=master

Copyright (c) 2013, Friedrich Paetzke (f.paetzke@gmail.com)
All rights reserved.

Dotter is a graphviz wrapper for Python 2 and 3. In order to use it you need graphviz.
On Debian/Ubuntu you can install it by typing:

.. code:: bash

    $ apt-get install graphviz

After that install ``dotter`` via ``pip``.

.. code:: bash

    $ pip install dotter

An usage example:

.. code:: python

    from dotter import Dotter


    dotter = Dotter()

    dotter.add_node('a', label='b')
    dotter.add_node('b', label='c')
    dotter.add_edge('a', 'b')
    dotter.close()

.. image:: https://d2weczhvl823v0.cloudfront.net/paetzke/dotter/trend.png
  :target: https://bitdeli.com/free



