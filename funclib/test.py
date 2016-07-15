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
    a = numpy.array([[1, 2, 3], [numpy.nan, numpy.nan, 99]])
    b = numpy.array([[1, 2, 3], [numpy.nan, 99, numpy.nan]])
    assert isinstance(a, numpy.ndarray)
    assert isinstance(b, numpy.ndarray)
    dic  = arraylib.np_unmatched_nans_to_zero(a, b)
    print dic['a']
    print dic['b']
    
    


def test_statslib():
    '''test stats
    '''
    a = numpy.array([numpy.NaN,1,2,3])
    b = numpy.array([numpy.NaN,1,2,3])
    results = statslib.correlation(a, b, engine=statslib.EnumStatsEngine.r)
    print results
    results = statslib.correlation(a, b, engine=statslib.EnumStatsEngine.scipy)
    print results




test_arraylib()
#test_statslib()
#sys.exit()
