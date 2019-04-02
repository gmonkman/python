# pylint: skip-file
"""
Wrapper for matplotlib.
Takes care of common-case, pretty graphs.
"""
from __future__ import print_function

import config
import constants
import itertools as _it

import matplotlib
matplotlib.use('Agg')  # Disable the display, does not affect graph generation
import matplotlib.cm as _cm
import matplotlib.pyplot as _plt
from matplotlib.patches import Polygon

import networkx as _nx
import numpy as _np
import util
from mpl_toolkits.axes_grid1 import make_axes_locatable

from funclib.baselib import lists_remove_empty_pairs as _remove_empty


# Set font, globally
default_font = {
    #'family': 'normal',
    'weight': 'semibold',
    'size': 24,
    #'linespacing' : 0.4,
}
title_font = {
    #'family': 'normal',
    'weight': 'semibold',
    'size': 40,
    #'linespacing' : 0.4,
}
matplotlib.rc('font', **default_font)

markers = ["o", "^", "s", "*", "h", "D"]
COLORS = ["b", "darkgreen", "darkmagenta", "cyan",
          "darkorange", "magenta", "lime", "darkviolet", "chartreuse"]
LINE_STYLES = ["-", "-.", ":", "--"]

##########################################################################


def bar(xvalues, yvalues, title, xlabel, ylabel, alpha=1, color='royalblue', xlabels=None, width=0.8, output=None, xmax=None, ymax=None, vlines=None):
    """
        Create and save a bar plot.
        Args:
        - xvalues = x-axis positions for bars
        - yvalues = y-axis magnitudes of each bar
        - title   = title of plot. Also used for filename
        - xlabel  = x-axis label
        - ylabel  = y-axis label
        Options:
        - alpha   = opacity of bars
        - color   = color of bars
        - xlabels = x-axis labels for each bar
        - xmax    = max x-value
        - ymax    = max y-value
        - width   = width of bars
    """
    fig, ax1 = _plt.subplots()
    # Size
    if xmax:
        xmin, _ = ax1.get_xlim()
        ax1.set_xlim(xmin, xmax)
    if ymax:
        ymin, _ = ax1.get_ylim()
        ax1.set_ylim(ymin, ymax)
    # Add data
    bar = _plt.bar(xvalues, yvalues, width=width, color=color, alpha=alpha)
    # Add extra lines
    for line in (vlines or []):
        _plt.axvline(line["xpos"], color=line["color"],
                    linestyle=line["style"], linewidth=line["width"])
    # Labels
    if xlabels:
        _plt.xticks([x + width / 2 for x in xvalues], xlabels)
    ax1.set_title(title)
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    # Save
    output = output or "%s/%s-bar.png" % (constants.OUTPUT_DIR, title)
    _plt.savefig(output)
    _plt.clf()
    _plt.close()
    print("Saved bar chart to '%s'" % output)
    return output


def dots(xs, yss, title, xlabel, ylabel, labels=None, skip=None, output=None, vlines=None):
    fig, ax1 = _plt.subplots()
    # Add data
    for (ys, c, m) in zip(yss, _cm.rainbow(_np.linspace(0, 1, len(yss))), _it.cycle(markers)):
        _plt.plot(xs, ys, color=c, linestyle="dashed", marker=m)
    # Legend
    _plt.legend(['%s' % (labels[i] if labels else (skip * i)) for i in range(len(yss))],
               loc=2, bbox_to_anchor=(1, 1), borderaxespad=0., fontsize=11)
    # Add extra lines
    for line in (vlines or []):
        _plt.axvline(line["xpos"], color=line["color"],
                    linestyle=line["style"], linewidth=line["width"])
    ax1.set_title(title)
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    # Save
    output = output
    _plt.savefig(output)
    _plt.clf()
    _plt.close()
    print("Saved dots chart to '%s'" % output)
    return output


def line(xbounds, y_funs, title=None, xlabel=None, ylabel=None, linelabels=None, samples=constants.GRAPH_SAMPLES, alpha=1, output=None, vlines=None, hlines=None, ymax=None, yticks=None, xticks=None):
    fig, ax1 = _plt.subplots()
    # data
    X = _np.linspace(xbounds[0], xbounds[1], num=samples)
    for (y_fun, c, i) in zip(y_funs, _it.cycle(COLORS), range(0, 10, 2)):
        Y = [y_fun(val) for val in X]
        style = 'solid'
        wd = 6 if i == 0 else 4
        _plt.plot(X, Y, color=c, alpha=alpha - (0.1 * i),
                 linestyle=style, linewidth=wd)
    if linelabels:
        _plt.legend(['%s' % lbl for lbl in linelabels], loc=2,
                   bbox_to_anchor=(1, 1), borderaxespad=0., fontsize=11)
    # Add extra lines
    for line in (hlines or []):
        _plt.axhline(line["ypos"], alpha=line.get(
            "alpha", 1), color=line["color"], linestyle=line["style"], linewidth=line["width"])
    for line in (vlines or []):
        _plt.axvline(line["xpos"], alpha=line.get(
            "alpha", 1), color=line["color"], linestyle=line["style"], linewidth=line["width"])
    if ymax:
        ymin, _ = ax1.get_ylim()
        ax1.set_ylim(ymin, ymax + 2)
    ax1.set_xlim(xbounds[0] - 0.5, xbounds[1])
    if title:
        _plt.suptitle(title, fontdict=title_font, y=1.0)
    _plt.gcf().subplots_adjust(bottom=0.15)
    _plt.xlabel(xlabel, fontdict=default_font)
    # y-label & yticks
    _plt.title(ylabel, fontdict=default_font, x=0.001, y=1.05)
    if yticks:
        _plt.yticks(*yticks)
    if xticks:
        xposns, xlbls = xticks
        _plt.xticks(*xticks)
    # ax1.set_xticks([1] + ax1.get_xticks()[1:])
    # Save
    _plt.savefig(output)
    _plt.clf()
    _plt.close()
    print("Saved line to '%s'" % output)
    return output


def histogram(values, title, xlabel, ylabel, num_bins, xmax, ymax, output, alpha=0.8, color='royalblue'):
    '''stuff'''
    minval = min(values)
    maxval = max(values)
    bkt_width = (maxval - minval) / num_bins
    xvals = [(bkt_width * i) + minval for i in range(num_bins)]
    yvals = [sum((1 for val in values if lo <= val <= (lo + bkt_width)))
             for lo in xvals]
    # print("Plotting with vals %s" % yvals)
    return bar(xvals, yvals, title, xlabel, ylabel, xmax=xmax, ymax=ymax, alpha=alpha, color=color, width=bkt_width, output=output)


def module_graph(graph, project_name, cfg, title=None, alpha=1, edgecolor="k", untypedcolor='royalblue', typedcolor='darkorange', output=None):
    """
        Show module-dependence graph.
        Args:
        - graph        = The modulegraph object to plot
        - fname        = Filename the graph was parsed from. Used to save output.
        - title        = Title of plot
        Options:
        - alpha        = opacity of nodes
        - boundaries   = Edges to color Red and THICK
        - edgecolor    = Normal edge color
        - untypedcolor = Node color for untyped modules
        - typedcolor   = Node color for typed modules
    """
    # Make networkx graph
    g = _nx.DiGraph()
    for mn in graph.get_module_names():
        g.add_node(mn)
    for (src, dst) in graph.edges_iter():
        g.add_edge(src, dst)
    # Make pyplot
    pos = _nx.circular_layout(g, scale=1)
    fig, ax1 = _plt.subplots()
    # Untyped nodes, or the default
    _nx.draw_networkx_nodes(g, pos, node_size=1000, alpha=alpha, nodelist=[mn for mn in graph.get_module_names(
    ) if config.untyped_at(cfg, graph.index_of_module(mn))], node_color=untypedcolor)
    # Typed nodes
    _nx.draw_networkx_nodes(g, pos, node_size=1000, alpha=alpha, nodelist=[mn for mn in graph.get_module_names(
    ) if config.typed_at(cfg, graph.index_of_module(mn))], node_color=typedcolor)
    _nx.draw_networkx_labels(g, pos, dict(
        [(k, k) for k in graph.get_module_names()]))
    _nx.draw_networkx_edges(g, pos, edge_color=edgecolor, alpha=alpha)
    # Draw boundaries
    boundaries = [(src, dst) for (src, dst) in graph.edges_iter()
                  if config.is_boundary(cfg, graph.index_of_module(src), graph.index_of_module(dst))]
    _nx.draw_networkx_edges(g, pos, edgelist=boundaries,
                           edge_color="r", width=4)
    output = output or "%s/%s-module-graph-%s.png" % (
        constants.OUTPUT_DIR, project_name, cfg)
    title = title or "%s-modulegraph-%s.png" % (project_name, cfg)
    ax1.set_title(title)
    _plt.axis("off")
    _plt.savefig(output)
    _plt.clf()
    _plt.close()
    print("Saved module graph to '%s'" % output)
    return output


def box(dataset, title, xlabel, ylabel, alpha=1, color='royalblue', sym="+", xlabels=None, output=None):
    """
        Create and save a boxplot from the list `dataset`.
        Args:
        - dataset = y-axis points to plot
        - title   = Title of plot
        - xlabel  = x-axis label
        - ylabel  = y-axis label
        Options:
        - alpha : Opacity of box
        - color : Box color
        - sym   : Symbol for outliers
    """
    fig, ax1 = _plt.subplots()
    bp = _plt.boxplot(dataset, notch=0, sym=sym, vert=True, whis=1)
    _plt.setp(bp['boxes'], color='black')
    _plt.setp(bp['whiskers'], color='black')
    _plt.setp(bp['fliers'], color='red', marker=sym)
    ax1.yaxis.grid(True, linestyle='-', which='major',
                   color='lightgrey', alpha=0.5)
    # Fancier boxes
    for i in range(len(dataset)):
        box = bp['boxes'][i]
        coords = []
        # Color the boxes
        for j in range(0, 5):
            coords.append((box.get_xdata()[j], box.get_ydata()[j]))
        boxPolygon = Polygon(coords, facecolor=color, alpha=alpha)
        ax1.add_patch(boxPolygon)
        # Re-draw median lines
        med = bp['medians'][i]
        mx, my = [], []
        for j in range(2):
            mx.append(med.get_xdata()[j])
            my.append(med.get_ydata()[j])
            _plt.plot(mx, my, 'k')
        # Draw avg. dot
        _plt.plot([_np.average(med.get_xdata())], [_np.average(
            dataset[i])], color='w', marker='*', markeredgecolor='k')
    # plot axis: runtime + num types
    posns = range(len(dataset))
    if xlabels:
        _plt.xticks(posns, xlabels)
    else:
        _plt.xticks(posns)
    ax1.set_axisbelow(True)
    ax1.set_title(title)
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    # Legend
    # Reset y limit
    ymin, ymax = ax1.get_ylim()
    ax1.set_ylim(ymin - 5, ymax)
    _plt.figtext(0.80, 0.01, '*', color='white',
                backgroundcolor=color, weight='roman', size='medium')
    _plt.figtext(0.82, 0.01, ' Average Value', color='black',
                weight='roman', size='x-small')
    ## Save & clear
    output = output or "%s/%s-boxplot.png" % (constants.OUTPUT_DIR, title)
    _plt.savefig(output)
    _plt.clf()
    _plt.close()
    print("Saved figure to %s" % output)
    return output


def draw_violin(dataset, posns, alpha=1, color='royalblue', meanmarker="*"):
    """
        Draw a violin to the current plot.
        Color the mean point.
        (Shared helper for `violin_plot` and `double_violin`)
    """
    # Add data
    vp = _plt.violinplot(dataset, positions=posns,
                        showmeans=True, showextrema=True, showmedians=True)
    # Re-color bodies
    for v in vp['bodies']:
        v.set_edgecolors('k')
        v.set_facecolors(color)
        v.set_alpha(alpha)
    # Draw mean markers
    # Make original mean line invisible
    vp['cmeans'].set_alpha(0)
    # Draw data points
    for i in range(len(dataset)):
        _plt.plot([posns[i]] * len(dataset[i]), dataset[i], "r+")
    # Re-color median, min, max lines to be black
    for field in ['cmaxes', 'cmins', 'cbars', 'cmedians']:
        vp[field].set_color('k')
    # Draw the mean marker
    for i in range(len(dataset)):
        _plt.plot(posns[i], [_np.average(dataset[i])], color='w',
                 marker=meanmarker, markeredgecolor='k')
    # Draw confidence interval (should be optional)
    for i in range(len(dataset)):
        stat = utils.stats_of_row(dataset[i])
        _plt.errorbar(posns[i], stat["mean"], yerr=stat["ci"]
                     [1] - stat["mean"], ecolor="magenta", capthick=4)
    return


# region Violin
def violin(dataset, title, xlabel, ylabel, alpha=1, color='royalblue', meanmarker='*', positions=None, xlabels=None, output=None):
    """
        Create and save a violin plot representing the list `dataset`.
        Args:
        - dataset = List of lists to plot. Member lists cannot be empty.
        - title   = Title of plot
        - xlabel  = x-axis label
        - ylabel  = y-axis label
        Options:
        - `alpha` = Float [0,1], the opacity of colors in the output graph
        - `color` = Color to use for violins in the output graph
        - `meanmarker` = Symbol to use to mark the violin's mean
        - `positions` = x-axis positions for each violin
    """
    # Set default values
    posns = positions or list(range(1, 1 + len(dataset)))
    fig, ax1 = _plt.subplots()  # add figsize?
    draw_violin(dataset, posns, alpha=alpha,
                color=color, meanmarker=meanmarker)
    # Light gridlines
    ax1.yaxis.grid(True, linestyle='-', which='major',
                   color='lightgrey', alpha=0.5)
    # Titles + legend
    ax1.set_axisbelow(True)
    ax1.set_title(title)
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    if xlabels:
        _plt.xticks(posns, xlabels)
    else:
        _plt.xticks(posns)
    # Legend
    # Reset y limit
    ymin, ymax = ax1.get_ylim()
    ax1.set_ylim(ymin - 5, ymax)
    _plt.figtext(0.70, 0.043, "x", color="magenta", weight='roman',
                backgroundcolor="magenta", size='medium')
    _plt.figtext(0.72, 0.043, " 95% CI", color='black',
                weight='roman', size='x-small')
    _plt.figtext(0.80, 0.043, "+", color='red', weight='roman', size='medium')
    _plt.figtext(0.82, 0.043, " Sampled Point", color='black',
                weight='roman', size='x-small')
    _plt.figtext(0.80, 0.01, meanmarker, color='white',
                backgroundcolor=color, weight='roman', size='medium')
    _plt.figtext(0.82, 0.01, ' Average Value', color='black',
                weight='roman', size='x-small')
    output = output or "%s/%s-violin.png" % (constants.OUTPUT_DIR, title)
    _plt.savefig(output)
    _plt.clf()
    _plt.close()
    print("Saved violin plot to '%s'" % output)
    return output


def double_violin(series, title, xlabel, ylabel, alpha=0.8, colors=['royalblue', 'darkorange'], markers=['*', 'o'], legend=False):
    """
        Plot 2 violins to the same plot.
        Used to compare two distributions.

        TODO think of more ways to compare 2 datasets
        TODO get working for more than 2 datasets, if necessary
    """
    # Set default values
    series1, series2, posns = _remove_empty(series[0], series[1])
    fig, ax1 = _plt.subplots()  # add figsize?
    draw_violin(series1, posns, alpha=alpha,
                color=colors[0], meanmarker=markers[0])
    draw_violin(series2, posns, alpha=alpha,
                color=colors[1], meanmarker=markers[1])
    # Light gridlines
    ax1.yaxis.grid(True, linestyle='-', which='major',
                   color='lightgrey', alpha=0.5)
    # Legend
    if legend and len(legend) == len(series):
        ymin, ymax = ax1.get_ylim()
        ax1.set_ylim(ymin - 5, ymax)
        _plt.figtext(
            0.70, 0.04, "-", color=colors[0], backgroundcolor=colors[0], weight='roman', size='x-small')
        _plt.figtext(0.72, 0.04, legend[0], color='k',
                    weight='roman', size='x-small')
        _plt.figtext(
            0.70, 0.01, '-', color=colors[1], backgroundcolor=colors[1], weight='roman', size='x-small')
        _plt.figtext(
            0.72, 0.01, legend[1], color='black', weight='roman', size='x-small')
    # Titles + legend
    ax1.set_axisbelow(True)
    ax1.set_title(title)
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    output = "%s/%s-dv.png" % (constants.OUTPUT_DIR, title)
    _plt.savefig(output)
    _plt.clf()
    _plt.close()
    print("Saved double violin plot to '%s'" % output)
    return output
# endregion


def bivariate_historgram(x, y):
    '''(ndarray, ndarray) -> void
    Draw a bivariate heatmap abounded by the 2d historgrams
    of each variable
    '''
    # the random data
    x = _np.random.randn(1000)
    y = _np.random.randn(1000)

    fig, axScatter = _plt.subplots(figsize=(5.5, 5.5))

    # the scatter plot:
    axScatter.scatter(x, y)
    axScatter.set_aspect(1.)

    # create new axes on the right and on the top of the current axes
    # The first argument of the new_vertical(new_horizontal) method is
    # the height (width) of the axes to be created in inches.
    divider = make_axes_locatable(axScatter)
    axHistx = divider.append_axes("top", 1.2, pad=0.1, sharex=axScatter)
    axHisty = divider.append_axes("right", 1.2, pad=0.1, sharey=axScatter)

    # make some labels invisible
    _plt.setp(axHistx.get_xticklabels() + axHisty.get_yticklabels(),
             visible=False)

    # now determine nice limits by hand:
    binwidth = 0.25
    xymax = _np.max([_np.max(_np.fabs(x)), _np.max(_np.fabs(y))])
    lim = (int(xymax / binwidth) + 1) * binwidth

    bins = _np.arange(-lim, lim + binwidth, binwidth)
    axHistx.hist(x, bins=bins)
    axHisty.hist(y, bins=bins, orientation='horizontal')

    # the xaxis of axHistx and yaxis of axHisty are shared with axScatter,
    # thus there is no need to manually adjust the xlim and ylim of these
    # axis.

    # axHistx.axis["bottom"].major_ticklabels.set_visible(False)
    for tl in axHistx.get_xticklabels():
        tl.set_visible(False)
    axHistx.set_yticks([0, 50, 100])

    # axHisty.axis["left"].major_ticklabels.set_visible(False)
    for tl in axHisty.get_yticklabels():
        tl.set_visible(False)
    axHisty.set_xticks([0, 50, 100])

    _plt.draw()
    _plt.show()



def cm2inch(*tupl):
    '''(tuple) -> tuple
    matplotlib uses inches for figsize,
    this wll convert inches to cm

    Example:
    >>>plt.figure(figsize=cm2inch(12.8, 9.6))
    '''
    inch = 2.54
    if isinstance(tupl[0], tuple):
        return tuple(i/inch for i in tupl[0])
    else:
        return tuple(i/inch for i in tupl)