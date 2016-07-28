import numpy
import xlwings

def export(a):
    '''currentl unused'''
    assert isinstance(a, numpy.ndarray)
    xlwings.view(a)


def numpy_pickle_view(picklepath):
    '''(str) -> void
    Loads and shows a pickled numpy array on the file system
    in excel
    '''
    arr = numpy.load(picklepath)
    xlwings.view(arr)