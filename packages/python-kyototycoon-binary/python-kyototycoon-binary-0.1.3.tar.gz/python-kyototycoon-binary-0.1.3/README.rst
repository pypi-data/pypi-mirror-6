python-kyototycoon-binary
=========================

.. image:: https://badge.fury.io/py/python-kyototycoon-binary.png
    :target: http://badge.fury.io/py/python-kyototycoon-binary

.. image:: https://travis-ci.org/studio-ousia/python-kyototycoon-binary.png?branch=master
    :target: https://travis-ci.org/studio-ousia/python-kyototycoon-binary

A lightweight Python client for accessing `Kyoto Tycoon <http://fallabs.com/kyototycoon/>`_ via its binary protocol.

The specification of the binary protocol is explained `here <http://fallabs.com/blog/promenade.cgi?id=19>`_.

Installation
------------

.. code-block:: bash

    $ pip install Cython
    $ pip install python-kyototycoon-binary

Basic Usage
-----------

.. code-block:: python

    >>> from bkyototycoon import KyotoTycoonConnection
    >>> client = KyotoTycoonConnection()
    >>> client.set_bulk({'key1': 'value1', 'key2': 'value2'})
    2
    >>> client.get_bulk(['key1', 'key2', 'key3'])
    {'key2': 'value2', 'key1': 'value1'}
    >>> client.remove_bulk(['key1', 'key2'])
    1
    >>> client.get_bulk(['key1', 'key2', 'key3'])
    {'key1': 'value1'}

Performance
-----------

In our benchmark tests, *python-kyototycoon-binary* was about **6-8 faster** than *python-kyototycoon*.

.. code-block:: bash

    $ pip install python-kyototycoon
    $ ktserver -dmn
    $ python benchmarks/benchmark.py
    python-kyototycoon-binary get_bulk qps: 30961
    python-kyototycoon-binary set_bulk qps: 40320
    python-kyototycoon-binary get_bulk_with_pool qps: 31722
    python-kyototycoon-binary set_bulk_with_pool qps: 42961
    python-kyototycoon get_bulk qps: 4394
    python-kyototycoon set_bulk qps: 4534

Documentation
-------------

Documentation is available at http://python-kyototycoon-binary.readthedocs.org.
