'''test code'''
import sys

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
    a = numpy.arange(9).reshape(3,3).astype(float)
    assert isinstance(a, numpy.ndarray)

    a = arraylib.np_pad_nan(a)
    b = numpy.copy(a)

    dic = arraylib.np_delete_paired_nans_flattened(a,b)
    print dic['a']
    print dic['b']

    #a = arraylib.np_focal_mean(a, False)
    #print a


def test_statslib():
    a = numpy.array([numpy.NaN,1,2,3])
    b = numpy.array([numpy.NaN,1,2,3])
    results = statslib.correlation(a, b, engine=statslib.EnumStatsEngine.r)
    print results
    results = statslib.correlation(a, b, engine=statslib.EnumStatsEngine.scipy)
    print results




test_arraylib()
#test_statslib()
#sys.exit()