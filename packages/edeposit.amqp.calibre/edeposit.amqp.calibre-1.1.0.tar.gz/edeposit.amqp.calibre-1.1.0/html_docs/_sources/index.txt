edeposit.amqp.calibre documentation
===================================
This module provides wrapper for Calibre_, to access it's conversion functions
using AMQP protocol.

Module provides only generic wrapper, not AMQP communication itself - that is
handled by Calibredaemon_ from `edeposit.amqp`_ project.

.. image:: _static/uml.png

.. _Calibre: http://calibre-ebook.com
.. _Calibredaemon: https://github.com/edeposit/edeposit.amqp/blob/master/edeposit/amqp/calibreademon.py
.. _edeposit.amqp: http://edeposit-amqp.readthedocs.org

Installation
------------
Module is hosted at GitHub:

- https://github.com/edeposit/edeposit.amqp.calibre

and can be installed using PIP::

    pip install edeposit.amqp.calibre

API
---

.. include:: api/edeposit.amqp.calibre.structures.rst

.. include:: api/edeposit.amqp.calibre.rst


.. Contents:

.. .. toctree::
..    :maxdepth: 4

..    api/edeposit.amqp.calibre



Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

