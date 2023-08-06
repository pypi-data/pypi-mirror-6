========
firapria
========

.. image:: https://img.shields.io/travis/bfontaine/firapria.png
   :target: https://travis-ci.org/bfontaine/firapria
   :alt: Build status

.. image:: https://img.shields.io/pypi/v/firapria.png
   :target: https://pypi.python.org/pypi/firapria
   :alt: Pypi package


``firapria`` is a lightweight library to extract pollution indices from
Airparif website for IDF (France).

Install
-------

.. code-block::

    pip install firapria

Usage
-----

.. code-block::

    from firapria.pollution import PollutionFetcher
    indices = PollutionFetcher().indices()

It returns three integers, for yesterday’s, today’s and tomorrow’s indices.

The library also include a CLI executable of the same name. Run it with ``-h``
to see its available options.

Tests
-----

Clone this repo, then: ::

    [sudo] make deps
    make check

