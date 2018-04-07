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



def scatter(x_data, y_data, group_labels=(), ptsizes=4, show=True):
    '''(list|tuple|ndarray, list|tuple|ndarray, list|tuple|ndarray, bool) - void

    Simple x-y scatter plot, supports groups by passing
    multiple iterables to x_data and y_data.

    x_data:
        an iterable of iterable data, or an iterable
    y_data:
        an iterable of iterable data, or an iterable
    group_labels:
        tuple of group labels to use to create a legend
    ptsizes:
        single value or list-like of point sizes. If
        list like, ptsizes matches group_labels by
        index
    show:
        show the plot

    Example:
    >>>x_data=[[-1,-2,-3],[3,4,5]]
    >>>y_data=[[-5,-6,-7],[5,5,12]]
    >>>group_labels=('negatives','positives')
    >>>scatter(x_data, y_data, group_labels)
    '''

    if not _baselib.isIterable(x_data):
        x_data = [_np.array(x_data)]

    if not _baselib.isIterable(y_data):
        y_data = [_np.array(y_data)]

    for ind, x in enumerate(x_data):
        if len(x) != len(y_data[ind]):
            raise ValueError('x_data and y_data lengths must match')

    groups = []
    if not group_labels or len(group_labels) != len(x_data):
        print('\nGroup labels empty, or len(group_labels) != len(data). Creating custom labels.')
        group_labels = []
        _ = [group_labels.append(str(x)) for x in range(len(x_data))]

    for ind, x in enumerate(x_data):
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

        groups.append(grp)
        Plot.scatter(ndX, ndY, s=ptsizes)
        lst_mean = lambda lst: sum(lst)/len(lst) if lst else 0

        label_pts = [(lst_mean(x), lst_mean(y)) for x, y in zip(x_data, y_data)]
        for i in range(len(label_pts)):
            Plot.annotate(group_labels[i], xy=label_pts[i], xytext=label_pts[i], horizontalalignment='center', verticalalignment='center', size=8)

        #Plot.legend(groups, loc='upper right')

    if show:
        Plot.show()
