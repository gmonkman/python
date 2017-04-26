import pickle

from numpy import hstack, vstack, array, ones
from numpy.random import randn
from numpy import sin, cos
from numpy import pi
"""
This generates the 2D point data sets used in chapter 8.

(both training and test)
"""

###
# Training data
###

# create sample data of 2D points
n = 10

# two normal distributions
class_1 = 0.6 * randn(n, 2)
class_2 = 1.2 * randn(n, 2) + array([5, 1]) #numpy array filled with 100 random points, ie 100,2
labels = hstack((ones(n), -ones(n))) #greats numpy array 1 x 200  filled with 100 ones (0:100) and 100 -1s (100:200)

# save with Pickle
with open('./data/points_normal_10.pkl', 'wb') as f:
    pickle.dump(class_1, f)
    pickle.dump(class_2, f)
    pickle.dump(labels, f)

# normal distribution and ring around it
class_1 = 0.6 * randn(n, 2)
r = 0.8 * randn(n, 1) + 5 #start making class 2
angle = 2 * pi * randn(n, 1)
class_2 = hstack((r * cos(angle), r * sin(angle)))
labels = hstack((ones(n), -ones(n)))

# save with Pickle
with open('./data/points_ring_10.pkl', 'wb') as f:
    pickle.dump(class_1, f)
    pickle.dump(class_2, f) #plt.scatter(class_2[0:100,0:1],class_2[0:100,1:2])
    pickle.dump(labels, f)


###
# Test data
###

# create sample data of 2D points
n = 10

# two normal distributions
class_1 = 0.6 * randn(n, 2)
class_2 = 1.2 * randn(n, 2) + array([5, 1])
labels = hstack((ones(n), -ones(n)))

# save with Pickle
with open('./data/points_normal_test_10.pkl', 'wb') as f:
    pickle.dump(class_1, f)
    pickle.dump(class_2, f)
    pickle.dump(labels, f)

# normal distribution and ring around it
class_1 = 0.6 * randn(n, 2)
r = 0.8 * randn(n, 1) + 5
angle = 2 * pi * randn(n, 1)
class_2 = hstack((r * cos(angle), r * sin(angle)))
labels = hstack((ones(n), -ones(n)))

# save with Pickle
with open('./data/points_ring_test_10.pkl', 'wb') as f:
    pickle.dump(class_1, f)
    pickle.dump(class_2, f)
    pickle.dump(labels, f)

print('Finished')