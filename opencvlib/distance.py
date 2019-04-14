# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# no-self-use, unused-argument
'''Distance measures'''
from warnings import warn as _warn

import numpy as _np
import scipy.spatial.distance as _scipy_dist

from funclib.arraylib import iter_dist_matrix #helper

__all__ = ['L1dist', 'L2dist']


def L2dist(p1, p2):
    '''(ndarray|list,ndarray|list)->float
    Euclidean L2 distance between two points.
    eg.
    A=np.array([[0,0]])
    B=np.array([[1,1]])
    L2dist(A, B) = 1.4142...
    '''
    if isinstance(p1, (list, tuple)):
        return _np.sqrt(_np.sum((_np.array(p1) - _np.array(p2))**2))
    return _np.sqrt(_np.sum((p1 - p2)**2))


def L1dist(v1, v2):
    '''(ndarray,ndarray)->float
    L1dist (minkowski/taxi cab) distance between 2 points
    A=np.array([[0,0]])
    B=np.array([[1,1]])
    L2dist(A, B) = 2
    '''
    if isinstance(v1, (list, tuple)):
        return _np.sum(abs(_np.array(v1) - _np.array(v2)))
    return _np.sum(abs(v1 - v2))



def nearN_euclidean(point, points, nr=1):
    '''(ndarray|list|tuple|ndarray|list|tuple,int)->list [[ind1,dist1]int (index of tuple), point of same type as points
    Given a point and an array of points
    return a list of lists containing the index and distances of the nr closest points to point.
    eg:
    pt = [0,0]: pts=[[0,0], [1,1], [3,3]]
    nearN_euclidean(point, points, nr=2)
    # ([0,0], [1,1.414

    0 and 1 are the indices and 1, 1.414 are the distances
    '''
    ndpt = _np.array(point)
    ndpts = _np.array(points)
    diff = ndpts - ndpt
    dist = diff*diff
    dist = _np.sqrt(dist[0:, 0] + dist[0:, 1])

    nr = len(dist) if nr > len(dist) else nr #argpartition generates an error if nr greater than nr of elements in dist
    ret = _np.argpartition(dist, -nr)
    ret = ret[:nr]
    l_ind = ret.tolist()
    l_dist = dist[l_ind].tolist()
    out = [x for x in zip(l_ind, l_dist)]
    return out


def furthestN_euclidean(point, points, nr=1):
    '''(ndarray|list|tuple|ndarray|list|tuple,int)->list [[int,float], ... ]
    Given a point and an array of points
    return a list of lists of the index and distance of the nr most distant points from point.
    eg:
    >>> pt = [0,0]; pts=[[0,0], [1,1], [3,3]]
    >>> furthestN_euclidean(pt, pts, nr=2)
    [[2,9], [1,1.414]]

    2 and 1 are the indices and 9 and 1.414 are the distances

    This list is NOT ordered, i.e. the first in the list may not be the furthest,
    unless ofcouse nr=1
    '''
    assert len(points) >= nr, 'Points should be greater than or equal to nr'
    ndpt = _np.array(point).astype('float')
    ndpts = _np.array(points).astype('float')

    diff = ndpt - ndpts
    dist = diff*diff
    dist = _np.sqrt(dist[0:, 0] + dist[0:, 1])
    if len(points) == 1:
        out = [[0, dist[0]]]
    else:
        ret = _np.argpartition(dist, -nr)[-nr:]
        l_ind = ret.tolist()
        l_dist = dist[l_ind].tolist()
        out = [x for x in zip(l_ind, l_dist)]
    return out


def nearestN_euclidean(point, points, nr=1):
    '''(ndarray|list|tuple|ndarray|list|tuple,int)->list [[int,float], ... ]
    Given a point and an array of points
    return a list of lists of the index and distance of the nr most distant points from point.
    eg:
    >>> pt = [0,0]; pts=[[0,0], [1,1], [3,3]]
    >>> furthestN_euclidean(pt, pts, nr=2)
    [[2,9], [1,1.414]]

    2 and 1 are the indices and 9 and 1.414 are the distances

    This list is NOT ordered, i.e. the first in the list may not be the nearest,
    unless ofcouse nr=1
    '''
    assert len(points) >= nr, 'Points should be greater than or equal to nr'
    ndpt = _np.array(point).astype('float')
    ndpts = _np.array(points).astype('float')
    diff = ndpts - ndpt
    dist = diff*diff
    dist = _np.sqrt(dist[0:, 0] + dist[0:, 1])
    if len(points) == 1:
        out = [[0, dist[0]]]
    else:
        ret = _np.argpartition(dist, nr)[:nr]
        l_ind = ret.tolist()
        l_dist = dist[l_ind].tolist()
        out = [x for x in zip(l_ind, l_dist)]
    return out


def linear_distance_matrix(r, c):
    '''(int, int) -> ndarray
    Returns a distance matrix based on linear distance.

    args
        r: row count
        c: column count

    Example:
    linear_distance_matrix(3,3)

      0 1 2
    -------
    0|0 1 2
    1|1 0 1
    2|2 1 0
    '''
    return _np.fromfunction(lambda i, j: abs(i - j), (r, c), dtype=int)



def feature_dist(labelled_array):
    #see https://stackoverflow.com/questions/37228589/minimal-edge-to-edge-euclidean-distance-between-labeled-components-in-numpy-arra
    """(tuple|ndarray) -> n,n-ndarray
    Takes a labeled array as returned by scipy.ndimage.label and
    returns an intra-feature distance matrix which should be the
    edge to edge distance between features.

    Use scipy.ndimage.label to label images to be passed into
    feature_dist. All non-zero values are considered features.

    Params:
    labelled_array: An ndarray of labelled features

    Returns:
    A square form n x n distance matrix ndarray

    Example:
    >>>A=_np.zeros(100).reshape(10,10)
    >>>A[0:2,0:2] = 1; A[3,3]=1; A[8:10,8:10]=1
    >>>ALbl= _ndimage.label(A)
    >>>feature_dist(ALbl[0])
    array(  [[0.        , 2.82842712, 9.89949494],
            [2.82842712, 0.        , 7.07106781],
            [9.89949494, 7.07106781, 0.        ]])
    """
    if isinstance(labelled_array, tuple):
        _warn('Tuple was passed to feature_dist, assuming the ndarray is in the tuple. This happens of the output from ndimage.label is used directly and is not a problem.')
        labelled_array = labelled_array[0]

    I, J = _np.nonzero(labelled_array)
    labels = labelled_array[I,J]
    coords = _np.column_stack((I,J))

    sorter = _np.argsort(labels)
    labels = labels[sorter]
    coords = coords[sorter]

    sq_dists = _scipy_dist.cdist(coords, coords, 'sqeuclidean')

    start_idx = _np.flatnonzero(_np.r_[1, _np.diff(labels)])
    nonzero_vs_feat = _np.minimum.reduceat(sq_dists, start_idx, axis=1)
    feat_vs_feat = _np.minimum.reduceat(nonzero_vs_feat, start_idx, axis=0)

    return _np.sqrt(feat_vs_feat)