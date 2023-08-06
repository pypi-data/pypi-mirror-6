# -*- coding: utf-8 -*-
"""
==========================================================================
Module for plot filter effects (:mod:`pksci.tools.mpltools._plotfuncs`)
==========================================================================

.. currentmodule:: pksci.tools.mpltools._plotfuncs

"""

from __future__ import division, print_function, absolute_import

import os
import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt

from matplotlib.patheffects import Normal
from matplotlib.ticker import FormatStrFormatter
from matplotlib.transforms import offset_copy

from .._fiofuncs import get_fpath

from ._cmaps import CustomColormap
from ._filters import DropShadowFilter, GrowFilter, FilteredArtistList, \
    LightFilter
from ._profiles import get_mpl_rcParams

__all__ = ['plot_colorbar', 'generate_colorbar', 'plot_dropshadow',
           'filtered_text', 'light_filter_pie', 'drop_shadow_patches',
           'plot_arrow_line']


def plot_colorbar(fname, cmap_name='BlGnOr', cbar_min=None, cbar_max=None,
                  cbar_extend='both', cbar_orientation='horizontal',
                  cbar_ticks_position=None, cbar_label_fontsize=None,
                  cbar_label_position=None, cbar_label_pad=None,
                  cbar_Nticks=10, cbar_tick_width=None, cbar_tick_length=None,
                  cbar_format_str=None, cbar_units=None, N_rgb_qlevels=256,
                  dpi=1200, cbar_width=None, cbar_height=None,
                  plotformat='png', bbox_inches='tight', pad_inches=0.1,
                  profile='kgraph', usetex=False):

    get_mpl_rcParams(mpl, profile='kgraph', usetex=usetex)
    fig, ax = plt.subplots(1, 1)
    try:
        cbar_cmap = \
            CustomColormap(cmap_name).get_mpl_colormap(N=N_rgb_qlevels)
    except KeyError:
        cbar_cmap = mpl.cm.get_cmap(cmap_name)

    cbar_norm = mpl.colors.Normalize(vmin=cbar_min, vmax=cbar_max)
    cbar_ticks = np.linspace(cbar_min, cbar_max, cbar_Nticks).tolist()
    if cbar_format_str is None:
        cbar_format_str = '%.1f'

    if cbar_units is not None:
        cbar_format_str = ' '.join((cbar_format_str, cbar_units))

    cbar_formatter = FormatStrFormatter(cbar_format_str)
    cbar = mpl.colorbar.ColorbarBase(ax, cmap=cbar_cmap, norm=cbar_norm,
                                     extend=cbar_extend, ticks=cbar_ticks,
                                     format=cbar_formatter,
                                     orientation=cbar_orientation)

    if cbar_ticks_position is not None:
        if cbar_orientation == 'horizontal':
            cbar.ax.xaxis.set_ticks_position(cbar_ticks_position)
        else:
            cbar.ax.yaxis.set_ticks_position(cbar_ticks_position)

    if cbar_label_position is not None:
        if cbar_orientation == 'horizontal':
            cbar.ax.xaxis.set_label_position(cbar_label_position)
        else:
            cbar.ax.yaxis.set_label_position(cbar_label_position)

    if cbar_label_fontsize is not None:
        cbar.ax.tick_params(labelsize=cbar_label_fontsize)

    if cbar_tick_width is not None:
        cbar.ax.tick_params(width=cbar_tick_width)

    if cbar_tick_length is not None:
        cbar.ax.tick_params(length=cbar_tick_length)

    if cbar_label_pad is not None:
        cbar.ax.tick_params(pad=cbar_label_pad)

    if cbar_width is not None and cbar_height is not None:
        fig.set_size_inches(cbar_width, cbar_height)
    fig.savefig(get_fpath(fname, ext=plotformat), bbox_inches=bbox_inches,
                pad_inches=pad_inches, dpi=dpi)


def generate_colorbar(fname, outpath=os.getcwd(), ext='png',
                      overwrite=False, add_fnum=True, fnum=None,
                      bbox_inches='tight', pad_inches=0.1,
                      figwidth=None, figheight=None,
                      cmap_name='jet', cbar_vmin=None, cbar_vmax=None,
                      cbar_cmap=None, cbar_norm=None, cbar_boundaries=None,
                      cbar_extend=None, cbar_extendfrac=None, cbar_ticks=None,
                      cbar_spacing=None, cbar_format=None,
                      cbar_orientation=None, Ncolors=None):

    fig = plt.figure(figsize=(figwidth, figheight))
    ax = fig.add_axes([0, 1, 1, 1])

    fout = get_fpath(fname=fname, outpath=outpath, ext=ext,
                     overwrite=overwrite, add_fnum=add_fnum, fnum=fnum)
    if cbar_cmap is None:
        cbar_cmap = mpl.cm.get_cmap(cmap_name)

    if cbar_norm is None:
        cbar_norm = mpl.colors.Normalize(vmin=cbar_vmin, vmax=cbar_vmax)

    if cbar_ticks is None:
        pass

    cbar = mpl.colorbar.ColorbarBase(ax, cmap=cbar_cmap, norm=cbar_norm,
                                     extend=cbar_extend, ticks=cbar_ticks,
                                     format=cbar_format,
                                     orientation=cbar_orientation)

    fig.savefig(fout, bbox_inches=bbox_inches, pad_inches=pad_inches)

    return cbar


def plot_arrow_line(axes, xdata, ydata, direction=1, ec='k', fc='k',
                    markersize=5.0, alpha=0.9):
    """Plot arrow markers at data points oriented tangent to the slope of line.

    Parameters
    ----------
    axes : `matplotlib Axes instance <matplotlib:Axes>`.
    xdata, ydata : array_like
    direction : {0, 1}, optional
    ec, fc : str, optional
    markersize : float, optional
    alpha : float, optional

    """
    dx = np.diff(xdata)
    dy = np.diff(ydata)
    m = dy / dx
    mean_m = []
    for i in xrange(len(m[:-1])):
        mean_m.append(np.mean(m[i:i+2]))
    mean_m.insert(0, m[0])
    mean_m.append(m[-1])

    #dr = np.hypot(dx, dy).tolist()
    #dr.insert(0, 0)
    #dr = np.asarray(dr, dtype=float)
    #r = np.cumsum(dr)

    da = 2 * markersize * direction
    for i, (xi, yi) in enumerate(zip(xdata, ydata)):
        x0 = xi - da / 2
        y0 = yi - mean_m[i] * da / 2

        xi += da
        yi += mean_m[i] * da

        axes.annotate('', xy=(xi, yi), xycoords='data',
                      xytext=(x0, y0), textcoords='data',
                      arrowprops=dict(arrowstyle='-|>',
                                      alpha=alpha,
                                      ec=ec, fc=fc))


def plot_dropshadow(ax, plots, offsets, offset_units='points',
                    gaussian_blur_sigma=4, alpha=0.7, scale_factor=1):
    """Add :py:class:`DropShadowFilter` to plots.

    Parameters
    ----------
    ax : :py:class:`~matplotlib.axes.Axes` instance
    plots : sequence
        list of plot objects
    offsets : sequence
        tuple of (x, y) offset for drop shadow
    offset_units : str, optional
    gaussian_blur_sigma : float, optional
    alpha : float, optional
    scale_factor : float, optional

    """
    dropshadow = DropShadowFilter(gaussian_blur_sigma, alpha=alpha)
    for p, offset in zip(plots, offsets):
        xoffset, yoffset = offset[0] * scale_factor, offset[1] * scale_factor
        shadow, = ax.plot(p.get_xdata(), p.get_ydata())
        shadow.update_from(p)
        shadow_offset = offset_copy(p.get_transform(), ax.figure,
                                    x=xoffset, y=yoffset,
                                    units=offset_units)
        shadow.set_transform(shadow_offset)
        shadow.set_zorder(p.get_zorder() - 0.5)
        shadow.set_agg_filter(dropshadow)
        shadow.set_rasterized(True)


def filtered_text(ax):
    """Add filtered text to axes.

    mostly copied from contour_demo.py

    Parameters
    ----------
    ax : :py:class:`~matplotlib.axes.Axes` instance

    """

    # prepare image
    delta = 0.025
    x = np.arange(-3.0, 3.0, delta)
    y = np.arange(-2.0, 2.0, delta)
    X, Y = np.meshgrid(x, y)
    Z1 = mpl.mlab.bivariate_normal(X, Y, 1.0, 1.0, 0.0, 0.0)
    Z2 = mpl.mlab.bivariate_normal(X, Y, 1.5, 0.5, 1, 1)
    # difference of Gaussians
    Z = 10.0 * (Z2 - Z1)

    # draw
    ax.imshow(Z, interpolation='bilinear', origin='lower',
              cmap=mpl.cm.gray, extent=(-3, 3, -2, 2))
    levels = np.arange(-1.2, 1.6, 0.2)
    CS = ax.contour(Z, levels,
                    origin='lower',
                    linewidths=2,
                    extent=(-3, 3, -2, 2))

    ax.set_aspect("auto")

    # contour label
    cl = ax.clabel(CS, levels[1::2],  # label every second level
                   inline=1,
                   fmt='%1.1f',
                   fontsize=11)

    # change clable color to black
    for t in cl:
        t.set_color("k")
        # to force TextPath (i.e., same font in all backends)
        t.set_path_effects([Normal()])

    # Add white glows to improve visibility of labels.
    white_glows = FilteredArtistList(cl, GrowFilter(3))
    ax.add_artist(white_glows)
    white_glows.set_zorder(cl[0].get_zorder() - 0.1)

    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)


def drop_shadow_patches(ax):
    """Add drop shadow patches to axes.

    copied from barchart_demo.py

    Parameters
    ----------
    ax : :py:class:`~matplotlib.axes.Axes` instance

    """

    N = 5
    menMeans = (20, 35, 30, 35, 27)

    ind = np.arange(N)  # the x locations for the groups
    width = 0.35       # the width of the bars

    rects1 = ax.bar(ind, menMeans, width, color='r', ec="w", lw=2)

    womenMeans = (25, 32, 34, 20, 25)
    rects2 = ax.bar(ind + width + 0.1, womenMeans, width,
                    color='y', ec="w", lw=2)

    #gauss = GaussianFilter(1.5, offsets=(1,1), )
    gauss = DropShadowFilter(5, offsets=(1, 1), )
    shadow = FilteredArtistList(rects1 + rects2, gauss)
    ax.add_artist(shadow)
    shadow.set_zorder(rects1[0].get_zorder() - 0.1)

    ax.set_xlim(ind[0] - 0.5, ind[-1] + 1.5)
    ax.set_ylim(0, 40)

    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)


def light_filter_pie(ax):
    """Add :py:class:`LightFilter` to plot axes.

    Parameters
    ----------
    ax : :py:class:`~matplotlib.axes.Axes` instance

    """
    fracs = [15, 30, 45, 10]
    explode = (0, 0.05, 0, 0)
    pies = ax.pie(fracs, explode=explode)
    ax.patch.set_visible(True)

    light_filter = LightFilter(9)
    for p in pies[0]:
        p.set_agg_filter(light_filter)
        p.set_rasterized(True)  # to support mixed-mode renderers
        p.set(ec="none", lw=2)

    gauss = DropShadowFilter(9, offsets=(3, 4), alpha=0.7)
    shadow = FilteredArtistList(pies[0], gauss)
    ax.add_artist(shadow)
    shadow.set_zorder(pies[0][0].get_zorder() - 0.1)
