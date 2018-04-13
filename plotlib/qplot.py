# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''quick plots to view data while debugging'''
#import matplotlib as _mpl
import matplotlib.pyplot as Plot
import matplotlib.mlab as _mlab
import numpy as _np
import funclib.baselib as _baselib
#import scipy.stats as _stats
#import math as _math

import funclib.baselib as _baselib

def histo(data, bins='auto', normed=True, show=True):
    '''(list|ndarray, str|int, bool
    Plot a histogram
    '''

    D = _np.array(data).flatten()
    dummy, bins, dummy1 = Plot.hist(D, bins=bins, normed=normed)

    if normed:
        mu = D.mean()
        sigma = D.std()
        y = _mlab.normpdf(bins, mu, sigma)
        dummy = Plot.plot(bins, y, 'r--', linewidth=1)

    if show:
        Plot.show()



def scatter(x_data, y_data, data_labels=(), group_labels=(), ptsizes=4, data_label_font_sz=8, xlim=None, ylim=None, show=True):
    '''(list|tuple|ndarray, list|tuple|ndarray|None,
            list|tuple|ndarray, list|tuple|ndarray,
            2-tuple|None, 2-tuple|None, bool) - void

    Simple x-y scatter plot, supports groups by passing
    multiple iterables to x_data and y_data.

    x_data:
        an iterable of iterable data, or an iterable
        eg. [[1,2,4], [10,11,12]]
    y_data:
        an iterable of iterable data, or an iterable
        eg. [[1,2,4], [10,11,12]]

    data_labels:
        label for each data point
        eg. [['a','b','c'], ['x','y','z']]
    group_labels:
        tuple of group labels to use to create a legend,
        midpoint of series labelled.
        eg. ['group1', 'group2']
    ptsizes:
        single value or list-like of point sizes. If
        list like, ptsizes matches group_labels by
        index. Sensible values are between 1 and 20.
    data_label_font_sz:
        size of data labels, ie the labels of each point.
        8 is usually about right.
    xlim:
        2-Tuple, lower and upper limits of x, or None
    ylim:
        2-Tuple, lower and upper limits of y, or None
    show:
        show the plot

    Example:
    >>>x_data=[[-1,-2,-3],[3,4,5]]
    >>>y_data=[[-5,-6,-7],[5,5,12]]
    >>>group_labels=('negatives','positives')
    >>>scatter(x_data, y_data, group_labels)
    '''

    if isinstance(x_data, (list, tuple)):
        if _baselib.depth(x_data) == 1:
            x_data = [x_data]

    if isinstance(y_data, (list, tuple)):
        if _baselib.depth(y_data) == 1:
            y_data = [y_data]

    if isinstance(data_labels, (list, tuple)):
        if _baselib.depth(data_labels) == 1:
            data_labels = [data_labels]

    if not _baselib.isIterable(x_data):
        x_data = [_np.array(x_data)]

    if not _baselib.isIterable(y_data):
        y_data = [_np.array(y_data)]

    if not _baselib.isIterable(data_labels):
        data_labels = [_np.array(data_labels)]

    for ind, x in enumerate(x_data):
        if data_labels:
            if len(x) != len(data_labels[ind]):
                raise ValueError('x_data and data_label lengths must match')
        if len(x) != len(y_data[ind]):
            raise ValueError('x_data and y_data lengths must match')

    if group_labels and len(group_labels) != len(x_data):
        print('\nGroup labels: len(group_labels) != len(data). Creating custom labels.')
        group_labels = []
        _ = [group_labels.append(str(x)) for x in range(len(x_data))]

    for ind, x in enumerate(x_data):
        if group_labels:
            if len(group_labels) >= ind:
                grp = '{0!s}'.format(group_labels[ind])
            else:
                grp = 'grp {0!s}'.format(ind)


        if isinstance(x, _np.ndarray):
            ndX = x.flatten()
        else:
            ndX = _np.asarray(x).flatten()

        if isinstance(y_data[ind], _np.ndarray):
            ndY = y_data[ind].flatten()
        else:
            ndY = _np.asarray(y_data[ind]).flatten()

        Plot.figure()
        Plot.scatter(ndX, ndY, s=ptsizes)

        axes = Plot.gca()
        if isinstance(xlim, (tuple, list)):
            if len(xlim) == 2:
                axes.set_xlim(xlim)
        if isinstance(ylim, (tuple, list)):
            if len(ylim) == 2:
                axes.set_ylim(ylim)


        lst_mean = lambda lst: sum(lst)/len(lst) if lst else 0

        #this labels the mid point
        if group_labels:
            label_pts = [(lst_mean(x), lst_mean(y)) for x, y in zip(x_data, y_data)]
            for i in range(len(label_pts)):
                Plot.annotate(group_labels[i], xy=label_pts[i], xytext=label_pts[i], horizontalalignment='center', verticalalignment='center', size=data_label_font_sz)

        if data_labels:
            for n, labels in enumerate(data_labels):
                for i, label in enumerate(labels):
                    lbl_pt = (x_data[n][i], y_data[n][i])
                    Plot.annotate(label, xy=lbl_pt, xytext=lbl_pt, horizontalalignment='center', verticalalignment='center', size=data_label_font_sz)

        #Plot.legend(groups, loc='upper right')

    if show:
        Plot.show()
