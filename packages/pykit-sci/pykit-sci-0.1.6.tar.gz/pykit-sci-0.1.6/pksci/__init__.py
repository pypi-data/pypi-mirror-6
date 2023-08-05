# -*- coding: utf-8 -*-
"""
====================================================
pykit-sci: python package for science (:mod:`pksci`)
====================================================

Documentation is available online at `pksci_doc`_.

.. _pksci_doc: http://projects.geekspin.net/pksci/doc

Contents
--------
pykit-sci provides the following sub-packages.

Sub-packages
------------

::

 chemistry           --- abstract data structure for chemistry
 nanosci             --- nano-science tools
 physics             --- physics tools

::

 __version__   --- pykit-sci version string

"""
from __future__ import print_function, absolute_import

__all__ = ['chemistry', 'nanosci', 'physics']

from pksci.version import version as __version__
