# pylint: disable=too-few-public-methods,too-many-statements,bad-whitespace

'''test code'''
import numpy

import funclib.stringslib as stringslib
import funclib.arraylib as arraylib
import funclib.statslib as statslib





def test_stringslib():
    '''test stuff () <- void
    '''
    #print funclib.stringslib.datetime_stamp
    #print funclib.stringslib.read_number('12')


def test_arraylib():
    '''test shit
    '''
    #CREATE SOME ARRAYS
    #a = numpy.arange(9).reshape(3,3).astype(float)
    a = numpy.array([[numpy.nan, 0, 3], [0, numpy.nan, 99]])
    b = numpy.array([[numpy.nan, 0, 3], [0, 99, numpy.nan]])
    assert isinstance(a, numpy.ndarray)
    assert isinstance(b, numpy.ndarray)
    #dic  = arraylib.np_unmatched_nans_to_zero(a, b)
    dic  = arraylib.np_paired_zeros_to_nan(a, b)
    print dic['a']
    print dic['b']
    
    


def test_statslib():
    '''test stats
    '''
    res = statslib.permuted_teststat_check(r"C:\Users\Graham Monkman\OneDrive\Documents\PHD\My Papers\WalesRSA-MSP\data\focalcorr\fmm_0_20160716180726.csv", 0, 0)





#test_arraylib()
test_statslib()
#sys.exit()
