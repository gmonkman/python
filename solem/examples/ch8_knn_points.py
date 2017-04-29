from __future__ import print_function
from pylab import *
from numpy import *
import pickle

from solem.PCV.classifiers import knn
from solem.PCV.tools import imtools

"""
This is the simple 2D classification example in Section 8.1.

If you have created the data files, it will reproduce the plot
in Figure 8-1.
"""


# load 2D points using Pickle
with open('./data/points_normal.pkl', 'rb') as f:
    class_1 = pickle.load(f)
    class_2 = pickle.load(f)
    labels = pickle.load(f)

# load the model training data with corresponding labesl
model = knn.KnnClassifier(labels, vstack((class_1, class_2)))

# load test data using Pickle
with open('./data/points_normal_test.pkl', 'rb') as f:
    class_1 = pickle.load(f)
    class_2 = pickle.load(f)
    labels = pickle.load(f)

# test on the first point
res = model.classify(class_1[0])
print(res, class_1[0])

res = model.classify(class_1[1])
print(res, class_1[1])

res = model.classify(class_2[0])
print(res, class_2[0])

res = model.classify(class_2[1])
print(res, class_2[1])


# define function for plotting


def _classify(x, y, model=model):
    arr = []
    for (xx, yy) in zip(x, y):  # [1,2,3],[3,4,5] -> [1,3],[2,4],[3,5]
        arr.append(model.classify([xx, yy]))
    return array(arr)
    # return array([model.classify([xx, yy]) for (xx, yy) in zip(x, y)])


# plot the classification boundary

def plot():
    imtools.plot_2D_boundary(
        [-6, 6, -6, 6], [class_1, class_2], _classify, [1, -1])
    show()


def main():
    load_data()
    # plot()


if __name__ == "__main__":
    main()
    sys.exit(int(main() or 0))
