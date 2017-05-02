# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# no-self-use
'''knn classifier'''
#from sklearn.metrics import pairwise_distances
import numpy as np

from opencvlib.distance import L2dist


class KnnClassifier(object):
    '''knnclassifier'''

    def __init__(self, labels, samples):
        """ Initialize classifier with training data. """

        self.labels = labels
        self.samples = samples

    def classify(self, point, k=3, dist_func=L2dist):
        '''ndarray, int, func)->str
        Classify a point against k nearest
        in the training data, return label.
        ndarray: An ndarray representation of a point
        k: integer, representing number of groups
        dist_func: distance func taking 2 ndarray point representations, returning a float distance
        '''
        # compute distance to all training points
        dist = np.array([dist_func(point, s) for s in self.samples])

        # sort them
        ndx = dist.argsort()

        # use dictionary to store the k nearest
        votes = {}
        for i in range(k):
            label = self.labels[ndx[i]]
            votes.setdefault(label, 0)
            votes[label] += 1

        # return the dictionary label/key with the most votes
        return max(votes)
