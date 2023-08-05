|wq.io|

`wq.io <http://wq.io/wq.io>`__ is a collection of Python libraries for
consuming (input) and generating (output) external data resources in
various formats. It thereby facilitates interoperability between the `wq
framework <http://wq.io/>`__ and other systems and formats.

Getting Started
---------------

.. code:: bash

    pip install wq.io
    # Or, if using together with wq.app and/or wq.db
    pip install wq
    # To use wq.io's GIS capabilities also install Shapely and Fiona
    pip install shapely fiona

See `the documentation <http://wq.io/docs/>`__ for more information.

Features
--------

The basic idea behind wq.io is to avoid having to remember the unique
usage of e.g. ``csv``, ``xlrd``, or ``lxml`` every time one needs to
work with an external dataset. Instead, wq.io abstracts these libraries
into a consistent interface that works as an ``iterable`` of
``namedtuples``. The field names for a dataset are automatically
determined from the source file, e.g. the column headers in an Excel
spreadsheet.

.. code:: python

    from wq.io import load_file
    data = load_file('example.xls')
    for row in data:
        print row.name, row.date

When `fiona <https://github.com/Toblerity/Fiona>`__ and
`shapely <https://github.com/Toblerity/Shapely>`__ are available, wq.io
can also open and create shapefiles and other OGR-compatible geographic
data formats.

.. code:: python

    from wq.io import ShapeIO
    data = ShapeIO(filename='sites.shp')
    for id, site in data.items():
        print id, site.geometry.wkt

It is straightforward to `extend wq.io <http://wq.io/docs/custom-io>`__
by subclassing existing functionality with custom implementations.

.. |wq.io| image:: https://raw.github.com/wq/wq/master/images/256/wq.io.png
   :target: http://wq.io/wq.io
