#pylint: skip-file

'''test code'''
import numpy
import os
import sys
import itertools

import funclib.stringslib as stringslib
import funclib.arraylib as arraylib
import funclib.statslib as statslib
import funclib.plotlib.seabornlib as seabornlib
import funclib.inifilelib as inifilelib


#region stringslib
def test_stringslib():
    '''test stuff () <- void
    '''
    #print funclib.stringslib.datetime_stamp
    #print funclib.stringslib.read_number('12')
#endregion


#region arraylib
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
#endregion


#region statslib
def test_statslib():
    '''test stats
    '''
    res = statslib.permuted_teststat_check(r"C:\Users\Graham Monkman\OneDrive\Documents\PHD\My Papers\WalesRSA-MSP\data\focalcorr\fmm_0_20160716180726.csv", 0, 0)

def testbinning():
    a = numpy.random.rand(100)
    a[0] = numpy.nan
    a[99] = numpy.nan
    aout = statslib.quantile_bin(a, percentiles=[25,50,75], zero_as_zero=True)
#endregion


#region plots
def test_plots():
    '''test plots
    '''
   # seabornlib.bivariate_histogram()
#endregion


#region arraylib
#test_arraylib()
test_statslib()
#sys.exit()
#endregion

#region inifile
ini_name = os.path.abspath(__file__) + '.ini'
ini = inifilelib.configfile(ini_name)
s = ini.tryread('test', 'timeout', True, 60)
ini.trywrite('test','NEWTEST','666')
ini.trywrite('TRYWRITE','magic','8ball')
pass

#endregion


#region Top Level
#test_plots()
#testbinning()
#endregion


def file_list_generator(paths, wildcards):
    '''(iterable, iterable) -> tuple
    Takes a list of paths and wildcards and creates a
    generator which can be used to iterate through
    the generated file list
    '''
    yield [zip(x,paths) for x in itertools.permutations(paths,len(wildcards))]

paths = ('c:/','d:/','C:/development/python/')
wildcards=('*.ini','*.txt','*.bat','*.zip','*.pdf')

gen = file_list_generator(paths,wildcards)

for v in gen:
    print v