=======================
Tools for plotting data
=======================

*This tutorial is a work in progress and there are lots of incomplete and
otherwise illegible and/or incomplete sentences*

Design Principles
=================

My goal here is to have a tool which allows the user to plot his or her data
without having to learn anything about programming.

The data files are parsed, and for each file,
a :py:class:`~pksci.tools.datautils.DataSet` object is
populated with the numerical data. The
:py:class:`~pksci.tools.mpltools.PlotGenerator` class
is designed to take :py:class:`~pksci.tools.datautils.DataSet` objects
and plot them.

Almost all of my plot utilities rely on the matplotlib library.

Plot config files and parsing
==============================

.. include:: ../../../pksci/configfiles/configspecs/xyplot.cfg
   :code: cfg

.. include:: ../../../pksci/configfiles/templates/xyplot.cfg
   :code: cfg
