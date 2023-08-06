========
firapria
========

.. image:: https://img.shields.io/travis/bfontaine/firapria.png
   :target: https://travis-ci.org/bfontaine/firapria
   :alt: Build status

.. image:: https://img.shields.io/coveralls/bfontaine/firapria/master.png
   :target: https://coveralls.io/r/bfontaine/firapria?branch=master
   :alt: Coverage status

.. image:: https://img.shields.io/pypi/v/firapria.png
   :target: https://pypi.python.org/pypi/firapria
   :alt: Pypi package


``firapria`` is a lightweight library to extract pollution indices from
Airparif website for IDF (France).

Install
-------

.. code-block::

    pip install firapria

Since version 0.1.1, ``firapria`` supports both Python 2.x and 3.x.

Usage
-----

.. code-block::

    from firapria.pollution import get_indices
    indices = get_indices()

It returns three integers, for yesterday’s, today’s and tomorrow’s indices. It
might return only two integers sometimes, it’s when no prevision is available
for tomorrow’s indice, usually before 11 AM.

The library also include a simple CLI of the same name:

.. code-block::

    $ firapria
    Pollution:
        Yesterday: 42
        Today: 40
        Tomorrow: 40

Before 0.1.1
~~~~~~~~~~~~

``get_indices`` was introduced in version 0.1.1. Before that one, another API
was used. It’s still supported, but the new API is easier. ::

    from firapria.pollution import PollutionFetcher
    indices = PollutionFetcher().indices()

Tests
-----

Clone this repo, then: ::

    [sudo] make deps
    make check

