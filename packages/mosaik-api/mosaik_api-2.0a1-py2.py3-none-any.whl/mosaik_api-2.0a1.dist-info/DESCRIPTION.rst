Mosaik API for Python
=====================


This is an implementation of the mosaik API for simulators written in Python.
It hides all the messaging and networking related stuff and provides a simple
base class that you can implement.


Installation
------------

Change to the ``mosaik-api-python`` repo and use `pip
<http://www.pip-installer.org/en/latest/>`_ to install it:

.. sourcecode:: bash

    $ cd mosaik-api-python
    $ pip install .


Documentation
-------------

Please refer to mosaik’s documentation of the API.


Example Simulator
-----------------

This distribution contains an example simulator in the ``example_sim`` package.

It can be started via the ``pyexamplesim`` command; ``pyexamplesim --help``
shows you how to use it.

It can also be run in-process by importing and calling
``example_sim.mosaik.main()``.


Changelog
=========

2.0a1 – 2014-03-26
------------------

- Initial release. Note, that mosaik is still alpha and not yet done.


Authors
=======

The original concepts for the mosaik API were developed by Steffen Schütten and
Stefan Scherfke.

The author of the mosaik API version 2 is Stefan Scherfke.


