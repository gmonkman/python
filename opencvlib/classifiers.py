# pylint: disable=C0103, too-few-public-methods, locally-disabled
'''Classifiers'''

#from sklearn.metrics import pairwise_distances
import numpy as np

from opencvlib.distance import L2dist


class KnnClassifier(object):
    '''K-nearest neighour classifier

    Given a distance metric (such as euclidean distance),
    finds the K nearest neighbours to our feature vector
    returning the classification label of the feature
    with the highest number of 'votes' to our feature
    '''

    def __init__(self, labels, samples):
        """ Initialize classifier with training data.
        Labels is a list of labels
        Samples is a list of samples
        ***Sample and Label indexes MUST match***

        e.g.
        labels=['yes','no','yes','yes']
        samples=[12.3, 2.3, 14.4, 12.1]
        """

        self.labels = labels
        self.samples = samples

    def classify(self, point, k=3, dist_func=L2dist):
        '''ndarray, int, func)->str

        Classify a point against k nearest
        in the training data, returning label.

        labels and samples should be set on initialisation
        class initialisation

        point:
            An ndarray vector representing a point. e.g. [[3,3,4,3]]
            for a 4-D point
        k:
            representing number of groups. e.g. if we had wanted to classify an
            image according to whether it is predominantly red, green or blue,
            k would be 3.
        dist_func:
            distance func taking 2 ndarray multidimensional point representations
            and returning a float distance measure (e.g. euclidean distance)


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
