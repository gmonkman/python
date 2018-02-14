# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''quick plots to view data while debugging'''
#import matplotlib as _mpl
import matplotlib.pyplot as Plot
import matplotlib.mlab as _mlab
import numpy as _np

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



def scatter(x_data, y_data, group_labels=(), show=True):
    '''(listlike|ndarray, listlike|ndarray, bool) - void

    Simple x-y scatter plot, supports groups by passing
    multiple iterables to x_data and y_data.

    x_data:
        an iterable of iterable data, or an iterable
    y_data:
        an iterable of iterable data, or an iterable
    group_labels:
        tuple of group labels to use to create a legend

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

    for ind, x in enumerate(x_data):
        if len(group_labels) >= ind:
            grp = '{0!s}'.format(group_labels[ind])
        else:
            grp = 'grp {0!s}'.format(ind)


        if isinstance(x, _np.ndarray):
            ndX = x.flatten()
        else:
            ndX = _np.ndarray(x).flatten()

        if isinstance(y_data[ind], _np.ndarray):
            ndY = y_data[ind].flatten()
        else:
            ndY = _np.ndarray(y_data[ind]).flatten()

        groups.append(grp)
        Plot.scatter(ndX, ndY)

    Plot.legend(groups, loc='upper right')

    if show:
        Plot.show()
