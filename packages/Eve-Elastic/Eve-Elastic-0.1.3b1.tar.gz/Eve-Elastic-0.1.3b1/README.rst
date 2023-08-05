Eve-Elastic
===========

.. image:: https://travis-ci.org/petrjasek/eve-elastic.png?branch=master
        :target: https://travis-ci.org/petrjasek/eve-elastic

Eve-Elastic is `elasticsearch <http://www.elasticsearch.org>`_ data layer for `eve REST framework <http://python-eve.org>`_.

Features
--------

- fulltext search
- filtering via elasticsearch filter dsl
- facets support
- elasticsearch mapping generator for schema

License
-------
Eve-Elastic is `GPLv3 <http://www.gnu.org/licenses/gpl-3.0.txt>`_ licensed.

Install
-------

.. code-block:: bash

    $ pip install Eve-Elastic

Usage
-----
Set elastic as your eve data layer.

.. code-block:: python

    import eve
    form eve_elastic import Elastic

    app = eve.Eve(data=Elastic)

Config
------
There are 2 options for Eve-Elastic taken from ``app.config``:

- ``ELASTICSEARCH_URL`` (default: ``'http://localhost:9200/'``)
- ``ELASTICSEARCH_INDEX`` - (default: ``'eve'``)

