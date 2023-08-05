.. irc3 documentation master file, created by
   sphinx-quickstart on Mon Nov 25 01:03:01 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to irc3's documentation!
================================

irc client based on `asyncio <http://docs.python.org/3.4/library/asyncio.html>`_.

Require python 3.3+

Installation
==============

Using pip::

    $ pip install irc3

Usage
=====

Here is a simple bot:

.. literalinclude:: ../examples/mybot.py

You can also use a config file as an alternative:

.. literalinclude:: ../examples/bot.ini

Then run::

    $ irc3 -h
    $ irc3 bot.ini

Contents
========

.. toctree::
   :maxdepth: 2
   :glob:

   dec
   utils
   rfc
   plugins/*



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

