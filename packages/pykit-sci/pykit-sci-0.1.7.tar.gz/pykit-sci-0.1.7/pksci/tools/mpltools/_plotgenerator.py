# -*- coding: utf-8 -*-
"""
===============================================================================
Classes for generating plots (:mod:`pksci.tools.mpltools._plotgenerator`)
===============================================================================

.. currentmodule:: pksci.tools.mpltools._plotgenerator

"""
from __future__ import division, print_function, absolute_import

__docformat__ = 'restructuredtext'

import matplotlib as mpl
import matplotlib.image as image
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, FormatStrFormatter
from mpl_toolkits.axes_grid1.inset_locator import mark_inset, \
    zoomed_inset_axes

import numpy as np

from .._fiofuncs import get_fpath
from .._mathfuncs import rounddown2nearestN, roundup2nearestN, round2nearestN

from ._plotcfgparser import XYPlotConfigParser, PlotConfigParserError
from ._plotfuncs import plot_dropshadow
from ._profiles import get_mpl_rcParams

__all__ = ['PlotGenerator', 'XYPlotGenerator', 'MPLPlot',
           'XYPlot', 'XYGridPlot']


class PlotGenerator(object):
    """Base class for generating plots.

    Parameters
    ----------
    datasets : dict
    plotconfig : `PlotConfig`
    argparser : :py:class:`~python:argparse.ArgumentParser`, optional
    plotcfgparser : `PlotConfigParser`, optional
    plotcfgfile : str, optional
    insetcfgfile : str, optional
    overlaycfgfile : str, optional

    """
    def __init__(self, datasets=None, plotconfig=None, argparser=None,
                 plotcfgparser=None, plotcfgfile=None, insetcfgfile=None,
                 overlaycfgfile=None):
        self._datasets = datasets
        self._plotconfig = plotconfig
        self._argparser = argparser
        self._plotcfgparser = plotcfgparser
        self._plotcfgfile = plotcfgfile
        self._insetcfgfile = insetcfgfile
        self._overlaycfgfile = overlaycfgfile

    @property
    def datasets(self):
        return self._datasets

    @property
    def plotconfig(self):
        return self._plotconfig

    @property
    def plotcfgparser(self):
        return self._plotcfgparser


class XYPlotGenerator(PlotGenerator):
    """Plot config parser for standard 2D X-Y plots.

    Parameters
    ----------
    datasets : dict
    plotconfig : `PlotConfig`
    argparser : :py:class:`~python:argparse.ArgumentParser`, optional
    plotcfgparser : `PlotConfigParser`, optional
    plotcfgfile : str, optional
    insetcfgfile : str, optional
    overlaycfgfile : str, optional
    autoplot : bool, optional

    """
    def __init__(self, datasets=None, plotconfig=None, argparser=None,
                 plotcfgparser=None, plotcfgfile=None, insetcfgfile=None,
                 overlaycfgfile=None, autoplot=False):

        super(XYPlotGenerator, self).__init__(
            datasets=datasets, plotconfig=plotconfig, argparser=argparser,
            plotcfgparser=plotcfgparser, plotcfgfile=plotcfgfile,
            insetcfgfile=insetcfgfile, overlaycfgfile=overlaycfgfile)

        if datasets is None and plotconfig is None:
            if plotcfgparser is None:
                self._plotcfgparser = \
                    XYPlotConfigParser(argparser=self._argparser,
                                       plotcfgfile=self._plotcfgfile,
                                       insetcfgfile=self._insetcfgfile,
                                       overlaycfgfile=self._overlaycfgfile)

            self._datasets = self._plotcfgparser.datasets
            self._plotconfig = self._plotcfgparser.config

        #args = self._plotcfgparser.parsed_args
        #XYPlot.plot(datasets, plotconfig, **vars(args))

        if hasattr(self._plotconfig, 'plotgrid'):
            self._xyplot = XYGridPlot(self._plotconfig.plotgrid,
                                      self._datasets,
                                      self._plotconfig)
        else:
            self._xyplot = XYPlot(self._datasets, self._plotconfig)

        if autoplot:
            self._xyplot.plot()

            XYPlot.set_axes_labels(plotconfig=self._plotconfig,
                                   axes=self._xyplot.axes,
                                   figkwargs=self._xyplot.figkwargs)

            XYPlot.savefig(plotconfig=self._plotconfig,
                           figure=self._xyplot.figure,
                           figkwargs=self._xyplot.figkwargs)

    @property
    def xyplot(self):
        return self._xyplot


class MPLPlot(object):
    """Base class for matplotlib plots."""
    def __init__(self, datasets=None, plotconfig=None, figure=None, axes=None,
                 rows=1, cols=1):
        self._datasets = datasets
        self._plotconfig = plotconfig
        self._figure = figure
        self._axes = axes
        self._mpl = mpl

        self._figkwargs = \
            get_mpl_rcParams(mpl, profile=plotconfig.profile,
                             usetex=plotconfig.usetex,
                             fontfamily=plotconfig.fontfamily,
                             aspectratio=plotconfig.aspectratio)

        if axes is None:
            if rows == 1 and cols == 1:
                squeeze = True
            else:
                squeeze = False

            self._figure, self._axes = \
                plt.subplots(rows, cols, squeeze=squeeze)

    @property
    def figure(self):
        return self._figure

    @figure.deleter
    def figure(self):
        del self._figure

    @property
    def axes(self):
        return self._axes

    @axes.deleter
    def axes(self):
        del self._axes

    @property
    def figkwargs(self):
        return self._figkwargs

    @figkwargs.deleter
    def figkwargs(self):
        del self._figkwargs

    @property
    def mpl(self):
        return self._mpl

    @mpl.deleter
    def mpl(self):
        del self._mpl


class XYPlot(MPLPlot):
    """Make 2D XY plot.

    Parameters
    ----------
    datasets : dict
    plotconfig : `PlotConfig`
    figure : `matplotlib.figure`
    axes : `matplotlib.axes`
    rows, cols : int, optional

    """

    def __init__(self, datasets=None, plotconfig=None, figure=None, axes=None):
        super(XYPlot, self).__init__(
            datasets=datasets, plotconfig=plotconfig, figure=figure, axes=axes)

    def plot(self):
        """Generate 2D plot."""
        xmax = 0
        xmin = np.inf
        ymax = 0
        ymin = np.inf

        plots = []
        offsets = []

        for dataset_id, dataset in self._datasets.iteritems():

            if dataset.ydata is None:
                dataset.ydata = \
                    dataset.data[:, dataset.headers.index(
                        self._plotconfig.input.headers.yvar)] * \
                    self._plotconfig.datasets.yscale_factor

            if dataset.xdata is None:
                if self._plotconfig.input.headers.xvar is not None:
                    dataset.xdata = \
                        dataset.data[:, dataset.headers.index(
                            self._plotconfig.input.headers.xvar)] * \
                        self._plotconfig.datasets.yscale_factor
                else:
                    dataset.xdata = \
                        np.arange(0, len(dataset.ydata)) * \
                        self._plotconfig.datasets.xscale_factor

            xdata = dataset.xdata
            ydata = dataset.ydata

            xmax = max(xmax, xdata.max())
            xmin = min(xmin, xdata.min())
            ymax = max(ymax, ydata.max())
            ymin = min(ymin, ydata.min())

            dataset_plotconfig = \
                getattr(self._plotconfig.datasets, dataset_id)
            p1, = self._axes.plot(xdata, ydata,
                                  marker=dataset_plotconfig.marker,
                                  color=dataset_plotconfig.markercolor,
                                  markersize=dataset_plotconfig.markersize,
                                  mec=dataset_plotconfig.markeredgecolor,
                                  mew=dataset_plotconfig.markeredgewidth,
                                  mfc=dataset_plotconfig.markerfacecolor,
                                  fillstyle=dataset_plotconfig.fillstyle,
                                  ls=dataset_plotconfig.linestyle,
                                  lw=dataset_plotconfig.linewidth,
                                  label=dataset_plotconfig.label,
                                  alpha=dataset_plotconfig.alpha,
                                  markevery=dataset_plotconfig.markevery,
                                  solid_joinstyle='round')

            plots.append(p1)
            offsets.append((self._figkwargs['dropshadow.offset.x'] / 2,
                            self._figkwargs['dropshadow.offset.y'] / 2))

        if self._plotconfig.add_image_overlay:
            XYPlot.add_overlay(figure=self._figure,
                               overlay_config=self._plotconfig.overlay_config)

        if self._plotconfig.xaxis.log_scale:
            #plt.xscale('log')
            self._axes.xscale('log')
        if self._plotconfig.yaxis.log_scale:
            #plt.yscale('log')
            self._axes.yscale('log')

        datalimits = {'xaxis': {'left': xmin, 'right': xmax},
                      'yaxis': {'bottom': ymin, 'top': ymax}}
        XYPlot.set_axes_limits(axes=self._axes,
                               plotconfig=self._plotconfig,
                               datalimits=datalimits)

        if not self._plotconfig.disable_legend:
            XYPlot.add_legend(axes=self._axes, plotconfig=self._plotconfig)

        if self._plotconfig.add_zoomed_inset:
            XYPlot.add_zoomed_inset(axes=self._axes,
                                    datasets=self._datasets,
                                    figkwargs=self._figkwargs,
                                    plotconfig=self._plotconfig,
                                    inset_config=self._plotconfig.inset_config)

        if self._plotconfig.enable_dropshadow:
            plot_dropshadow(self._axes, plots, offsets,
                            offset_units='points',
                            gaussian_blur_sigma=4, alpha=0.5)

    @classmethod
    def add_legend(cls, axes=None, plotconfig=None):
        axes.legend(bbox_to_anchor=plotconfig.legend_bbox_to_anchor,
                    loc=plotconfig.legend_loc,
                    fontsize=plotconfig.legend_fontsize,
                    frameon=plotconfig.frame_legend,
                    fancybox=plotconfig.fancy_legend_frame,
                    framealpha=plotconfig.legend_frame_alpha,
                    handlelength=plotconfig.legend_handlelength,
                    ncol=plotconfig.legend_ncol,
                    mode=plotconfig.legend_mode)

    @classmethod
    def add_overlay(cls, figure=None, overlay_config=None):
        for section in overlay_config.sections:
            imgax_pos = dict(left=None, bottom=None,
                             width=None, height=None)
            for pos in imgax_pos.iterkeys():
                imgax_pos[pos] = float(overlay_config[section][pos])

            imgax = figure.add_axes([imgax_pos['left'],
                                     imgax_pos['bottom'],
                                     imgax_pos['width'],
                                     imgax_pos['height']])
            overlay_img = \
                image.imread(overlay_config[section]['fpath'])
            imgax.imshow(overlay_img)
            imgax.axis('off')

    @classmethod
    def add_zoomed_inset(cls, axes=None, datasets=None, figkwargs=None,
                         inset_config=None, plotconfig=None):
        inset_axes = zoomed_inset_axes(axes, inset_config.zoom_factor,
                                       loc=inset_config.location)
        for dataset_id, dataset in datasets.iteritems():
            dataset_plotconfig = getattr(plotconfig.datasets, dataset_id)
            xdata = dataset.xdata
            ydata = dataset.ydata

            p, = inset_axes.plot(xdata, ydata,
                                 marker=dataset_plotconfig.marker,
                                 color=dataset_plotconfig.markercolor,
                                 mec=dataset_plotconfig.markeredgecolor,
                                 mfc=dataset_plotconfig.markerfacecolor,
                                 label=dataset_plotconfig.label,
                                 lw=dataset_plotconfig.linewidth,
                                 ls=dataset_plotconfig.linestyle,
                                 alpha=dataset_plotconfig.alpha)

        XYPlot.set_axes_limits(axes=inset_axes,
                               plotconfig=inset_config)

        inset_axes.tick_params(
            axis='both', which='major',
            length=figkwargs['tick.major.size'] / 2)
        plt.setp([axis.get_ticklabels()
                  for axis in (inset_axes.xaxis, inset_axes.yaxis)],
                 fontsize=figkwargs['inset.axes.labelsize'])
        plt.setp(inset_axes.get_yticklabels(), visible=False)
        mark_inset(axes, inset_axes,
                   loc1=2, loc2=4, fc="none", ec="0.5")

    @classmethod
    def savefig(cls, fname=None, plotconfig=None, figure=None,
                figkwargs=None, verbose=True):
        """Save figure.

        Parameters
        ----------
        fname : {None, str}, optional
        plotconfig : {None, `PlotConfig`}
        figure : `matplotlib.figure`
        figkwargs : {None, dict}, optional
        verbose : bool, optional

        """

        if fname is None:
            fname = plotconfig.output.fname

        fout = get_fpath(fname, ext=plotconfig.plotformat,
                         outpath=plotconfig.output.outpath,
                         overwrite=plotconfig.output.overwrite,
                         add_fnum=True, fnum=plotconfig.output.file_num,
                         verbose=verbose)
        figure.set_size_inches(figkwargs['xdim'], figkwargs['ydim'])
        figure.savefig(fout, transparent=plotconfig.save_transparent,
                       format=plotconfig.plotformat,
                       bbox_inches=plotconfig.bbox_inches,
                       pad_inches=plotconfig.pad_inches,
                       frameon=False)

    @classmethod
    def set_axes_labels(cls, axes=None, plotconfig=None, figkwargs=None,
                        label_dict=None):
        """Set axes labels.

        Parameters
        ----------
        axes : `matplotlib.axes`
        plotconfig : `PlotConfig`
        figkwargs : dict
        label_dict : dict

        """
        if label_dict is not None:
            xlabel = label_dict[plotconfig.strtype][plotconfig.xaxis.var]
            ylabel = label_dict[plotconfig.strtype][plotconfig.yaxis.var]
        else:
            xlabel = plotconfig.xaxis.label
            ylabel = plotconfig.yaxis.label

        axes.set_xlabel(xlabel, labelpad=figkwargs['labelpad'])
        axes.set_ylabel(ylabel, labelpad=figkwargs['labelpad'])

    @classmethod
    def set_axes_limits(cls, axes=None, plotconfig=None, datalimits=None):
        """Set axes limits.

        Parameters
        ----------
        axes : `matplotlib.axes`
        plotconfig : `PlotConfig`
        datalimits : dict

        """
        if axes is None or plotconfig is None:
            raise PlotConfigParserError('please provides axes and plotconfig')

        if plotconfig.xaxis.left_limit is not None:
            left_limit = plotconfig.xaxis.left_limit
        elif datalimits is not None and \
                datalimits['xaxis']['left'] is not None:
            left_limit = datalimits['xaxis']['left']
        else:
            left_limit = 0

        if plotconfig.xaxis.scale_left_limit:
            left_limit = plotconfig.xaxis.left_limit_scale_factor * left_limit
        elif plotconfig.xaxis.round_left_limit_down_to_nearest is not None:
            left_limit = \
                rounddown2nearestN(
                    left_limit,
                    N=plotconfig.xaxis.round_left_limit_down_to_nearest)
        elif plotconfig.xaxis.round_left_limit_up_to_nearest is not None:
            left_limit = \
                roundup2nearestN(
                    left_limit,
                    N=plotconfig.xaxis.round_left_limit_up_to_nearest)
        elif plotconfig.xaxis.round_left_limit_to_nearest is not None:
            left_limit = \
                round2nearestN(
                    left_limit,
                    N=plotconfig.xaxis.round_left_limit_to_nearest)

        if plotconfig.xaxis.right_limit is not None:
            right_limit = plotconfig.xaxis.right_limit
        elif datalimits is not None and \
                datalimits['xaxis']['right'] is not None:
            right_limit = datalimits['xaxis']['right']
        else:
            right_limit = axes.get_xlim()[-1]

        if plotconfig.xaxis.scale_right_limit:
            right_limit = \
                plotconfig.xaxis.right_limit_scale_factor * right_limit
        elif plotconfig.xaxis.round_right_limit_down_to_nearest is not None:
            right_limit = \
                rounddown2nearestN(
                    right_limit,
                    N=plotconfig.xaxis.round_right_limit_down_to_nearest)
        elif plotconfig.xaxis.round_right_limit_up_to_nearest is not None:
            right_limit = \
                roundup2nearestN(
                    right_limit,
                    N=plotconfig.xaxis.round_right_limit_up_to_nearest)
        elif plotconfig.xaxis.round_right_limit_to_nearest is not None:
            right_limit = \
                round2nearestN(
                    right_limit,
                    N=plotconfig.xaxis.round_right_limit_to_nearest)

        axes.set_xlim(left=left_limit, right=right_limit)

        if plotconfig.yaxis.bottom_limit is not None:
            bottom_limit = plotconfig.yaxis.bottom_limit
        elif datalimits is not None and \
                datalimits['yaxis']['bottom'] is not None:
            bottom_limit = datalimits['yaxis']['bottom']
        else:
            bottom_limit = 0

        if plotconfig.yaxis.scale_bottom_limit:
            bottom_limit = \
                plotconfig.yaxis.bottom_limit_scale_factor * bottom_limit
        elif plotconfig.yaxis.round_bottom_limit_down_to_nearest is not None:
            bottom_limit = \
                rounddown2nearestN(
                    bottom_limit,
                    N=plotconfig.yaxis.round_bottom_limit_down_to_nearest)
        elif plotconfig.yaxis.round_bottom_limit_up_to_nearest is not None:
            bottom_limit = \
                roundup2nearestN(
                    bottom_limit,
                    N=plotconfig.yaxis.round_bottom_limit_up_to_nearest)
        elif plotconfig.yaxis.round_bottom_limit_to_nearest is not None:
            bottom_limit = \
                round2nearestN(
                    bottom_limit,
                    N=plotconfig.yaxis.round_bottom_limit_to_nearest)

        if plotconfig.yaxis.top_limit is not None:
            top_limit = plotconfig.yaxis.top_limit
        elif datalimits is not None and \
                datalimits['yaxis']['top'] is not None:
            top_limit = datalimits['yaxis']['top']
        else:
            top_limit = axes.get_xlim()[-1]

        if plotconfig.yaxis.scale_top_limit:
            top_limit = \
                plotconfig.yaxis.top_limit_scale_factor * top_limit
        elif plotconfig.yaxis.round_top_limit_down_to_nearest is not None:
            top_limit = \
                rounddown2nearestN(
                    top_limit,
                    N=plotconfig.yaxis.round_top_limit_down_to_nearest)
        elif plotconfig.yaxis.round_top_limit_up_to_nearest is not None:
            top_limit = \
                roundup2nearestN(
                    top_limit,
                    N=plotconfig.yaxis.round_top_limit_up_to_nearest)
        elif plotconfig.yaxis.round_top_limit_to_nearest is not None:
            top_limit = \
                round2nearestN(
                    top_limit,
                    N=plotconfig.yaxis.round_top_limit_to_nearest)

        axes.set_ylim(bottom=bottom_limit, top=top_limit)

        if plotconfig.xaxis.auto_minor_locator is not None:
            axes.xaxis.set_minor_locator(
                AutoMinorLocator(n=plotconfig.xaxis.auto_minor_locator))
        else:
            axes.xaxis.set_minor_locator(AutoMinorLocator(n=5))

        if plotconfig.yaxis.auto_minor_locator is not None:
            axes.yaxis.set_minor_locator(
                AutoMinorLocator(n=plotconfig.yaxis.auto_minor_locator))
        else:
            axes.yaxis.set_minor_locator(AutoMinorLocator(n=5))

        if plotconfig.xaxis.major_format_str_formatter is not None:
            axes.xaxis.set_major_formatter(FormatStrFormatter(
                plotconfig.xaxis.major_format_str_formatter))
        if plotconfig.yaxis.major_format_str_formatter is not None:
            axes.yaxis.set_major_formatter(FormatStrFormatter(
                plotconfig.yaxis.major_format_str_formatter))


class XYGridPlot(MPLPlot):
    """Plot multi-row/column XY plots.

    Parameters
    ----------
    plotgrid : `numpy.array`
    datasets : dict
    plotconfig : `PlotConfig`
    figure : `matplotlib.figure`
    axes : `matplotlib.axes`
    aspectratio : float

    """
    def __init__(self, plotgrid=None, datasets=None, plotconfig=None,
                 figure=None, axes=None, aspectratio=1.0):

        self._rows = np.size(plotgrid, axis=0)
        self._cols = np.size(plotgrid, axis=1)

        super(XYGridPlot, self).__init__(
            datasets=datasets, plotconfig=plotconfig, figure=figure, axes=axes,
            rows=self._rows, cols=self._cols)

        x_ws = 0.125 + (self._cols - 1) / self._cols * 0.3 + 0.1
        y_ws = 0.1 + (self._rows - 1) / self._rows * 0.15 + 0.1
        aspectratio = aspectratio * x_ws / y_ws

        self._figkwargs['ydim'] = self._figkwargs['ydim'] * self._rows
        self._figkwargs['xdim'] = self._figkwargs['ydim'] * aspectratio * \
            self._cols / self._rows

    def plot(self):

        xmax = 0
        xmin = np.inf
        ymax = 0
        ymin = np.inf
        for c in range(self._cols):
            for r in range(self._rows):
                for dataset_id, dataset in self._datasets.iteritems():

                    if dataset.ydata is None:
                        dataset.ydata = \
                            dataset.data[:, dataset.headers.index(
                                self._plotconfig.input.headers.yvar)] * \
                            self._plotconfig.datasets.yscale_factor

                    if dataset.xdata is None:
                        if self._plotconfig.input.headers.xvar is not None:
                            dataset.xdata = \
                                dataset.data[:, dataset.headers.index(
                                    self._plotconfig.input.headers.xvar)] * \
                                self._plotconfig.datasets.yscale_factor
                        else:
                            dataset.xdata = \
                                np.arange(0, len(dataset.ydata)) * \
                                self._plotconfig.datasets.xscale_factor

                    xdata = dataset.xdata
                    ydata = dataset.ydata

                    xmax = max(xmax, xdata.max())
                    xmin = min(xmin, xdata.min())
                    ymax = max(ymax, ydata.max())
                    ymin = min(ymin, ydata.min())

                    dataset_plotconfig = \
                        getattr(self._plotconfig.datasets, dataset_id)
                    self._axes[r, c].plot(
                        xdata, ydata,
                        marker=dataset_plotconfig.marker,
                        color=dataset_plotconfig.markercolor,
                        ms=dataset_plotconfig.markersize,
                        mec=dataset_plotconfig.markeredgecolor,
                        mew=dataset_plotconfig.markeredgewidth,
                        mfc=dataset_plotconfig.markerfacecolor,
                        fillstyle=dataset_plotconfig.fillstyle,
                        ls=dataset_plotconfig.linestyle,
                        lw=dataset_plotconfig.linewidth,
                        label=dataset_plotconfig.label,
                        alpha=dataset_plotconfig.alpha,
                        markevery=dataset_plotconfig.markevery,
                        solid_joinstyle='round')
        plt.setp([[self._axes[r, c].get_xticklabels()
                 for r in range(self._rows - 1)]
                 for c in range(self._cols)], visible=False)

        [self._axes[-1,c].set_xlabel(self._plotconfig.xaxis.label,
                                     labelpad=self._figkwargs['labelpad'])
         for c in range(self._cols)]
