# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# no-self-use, unused-argument
'''Distance measures'''
import numpy as np

__all__ = ['L1dist', 'L2dist']


def L2dist(p1, p2):
    '''(ndarray,ndarray)->float
    Euclidean L2 distance between two points.
    eg.
    A=np.array([[0,0]])
    B=np.array([[1,1]])
    L2dist(A, B) = 1.4142...
    '''
    return np.sqrt(np.sum((p1 - p2)**2))


def L1dist(v1, v2):
    '''(ndarray,ndarray)->float
    l1dist, the minkowski or taxi cab distance
    A=np.array([[0,0]])
    B=np.array([[1,1]])
    L2dist(A, B) = 2
    '''
    return np.sum(abs(v1 - v2))
