.. _getting_started:

===============
Getting started
===============

.. _installation:

Installation
============

Required Dependencies
---------------------

* `Python 2.7+ <http://python.org/download/>`_

Modules:

* `numpy 1.8+ <http://sourceforge.net/projects/numpy/files/>`_
* `pint 0.4+ <https://pypi.python.org/pypi/Pint/>`_

Installing pykit-sci
-----------------------

You can install the latest stable release from the
`Python Package Index <http://pypi.python.org/pypi/pykit-sci>`_
using :command:`pip`::

    > pip install pykit-sci

Alternatively you can download a source code tarball from
http://pypi.python.org/pypi/pykit-sci or clone the source code
from the `github repository <http://github.com/androomerrill/pykit-sci>`_
using :command:`git`::

    > git clone https://github.com/androomerrill/pykit-sci.git

:command:`cd` into the source code directory and run::

    > python setup.py install

These commands will probabily fail if you don't have *admin privileges*.
In that case, try installing to the user base directory.
Using :command:`pip`::

    > pip install --user pykit-sci

Or from source::

    > python setup.py install --user
