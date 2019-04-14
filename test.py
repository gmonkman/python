# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''Produce rext region proposals using tensorflow, saving the
detection to a pickled numpy array per image and optionally
showing the detections on a new image, saved in folder output_dir.

Non-maximum suppression can be optionaly applied.
'''
import numpy

A = numpy.array([[1,2,3],[2,3,4]])
B = numpy.array([[1,2,3],[2,3,4]])
C = numpy.vstack((A,B)).T