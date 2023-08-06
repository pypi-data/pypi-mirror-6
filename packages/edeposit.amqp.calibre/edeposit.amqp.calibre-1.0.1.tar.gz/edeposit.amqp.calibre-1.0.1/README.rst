Introduction
============

This module provides wrapper for Calibre, to access it’s conversion functions using AMQP protocol.

Module provides only generic wrapper, not AMQP communication itself - that is handled by Calibredaemon from edeposit.amqp project.

`Full module documentation <http://edeposit-amqp-calibre.readthedocs.org/en/latest/>`_ is hosted at the ReadTheDocs.

Installation
------------

Package can be installed using `PIP <http://en.wikipedia.org/wiki/Pip_%28package_manager%29>`_:

::

   pip install edeposit.amqp.calibre

Source codes are located at `GitHub <https://github.com/>`_: https://github.com/jstavel/edeposit.amqp.calibre.


Acceptance tests
----------------

`Robot Framework <http://robotframework.org/>`__ is used to test the sources, which are stored in ``src/edeposit/amqp/aleph/tests`` directory.

You can run them manually (from the root of the package):

::

    $ pybot -W 80 --pythonpath src/edeposit/amqp/calibre/tests/:src src/edeposit/amqp/calibre/tests/

Or continuously using nosier:

::

    $ nosier -p src -b 'export' "pybot -W 80 --pythonpath src/edeposit/amqp/calibre/tests/ --pythonpath src src/edeposit/amqp/calibre/tests/"

.. Status of acceptance tests
.. ++++++++++++++++++++++++++

.. You can see the results of the tests here:

.. http://edeposit-amqp-calibre.readthedocs.org/cs/latest/\_downloads/log.html

.. http://edeposit-amqp-calibre.readthedocs.org/cs/latest/\_downloads/report.html

.. Results are currently (12.03.2014) outdated, but some form of continuous integration framework will be used in the future.