import numpy
import xlwings

def export(a):
    '''currentl unused'''
    assert isinstance(a, numpy.ndarray)
    xlwings.view(a)
