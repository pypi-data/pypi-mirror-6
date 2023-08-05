==============
    patois
==============

``patois`` is an MIT-licensed compatibility library designed to smooth
over differences in various Python VMs,
e.g., CPython vs. Jython vs. PyPy vs. IronPython. It provides utility
functions with the goal of making it easier to write Python code that is
compatible with all the major Python VMs. See the documentation for more
information on what is provided.

``patois`` supports Python 2.7, because it is the newest Python that is
widely supported by the major VMs.

Inspiration
-----------

This package was inspired by `Six`_.

.. _Six: http://pythonhosted.org/six/

Installation
------------

To install ``patois``, simply::

    $ pip install patois

Or, if you absolutely must::

    $ easy_install patois

But, you really shouldn't do that.

If you want to vendor the lib for some reason, it's a single file, so just drop
it into your project.

Documentation
-------------

Online documentation is at https://readthedocs.org/patois

How to Contribute
-----------------

Bugs can be reported to https://github.com/gthank/patois

The code can also be found there. Please feel free to fork it and submit pull
requests.

History
-------

0.1.0 (2014-01-08)
******************

* Initial project creation
