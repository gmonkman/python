#pylint: disable=unused-import
'''Main entry module to perform the permutation analysis'''
from __future__ import print_function
import os
import sys

#custom
import numpy
import scipy.stats
import xlwings #dont delete this - call it from immediate sometimes

#mine
import funclib.iolib as iolib
import funclib.statslib as statslib
import funclib.arraylib as arraylib
import funclib.stringslib as stringslib

_INI_NAME = os.path.abspath(__file__) + '\\' + os.path.basename(sys.argv[0])

_NP_FMM_VALUE = numpy.array([])
assert isinstance(_NP_FMM_VALUE, numpy.ndarray)

_NP_FMM_VENUE_FOCAL = numpy.array([])
assert isinstance(_NP_FMM_VENUE_FOCAL, numpy.ndarray)

_NP_FMM_VENUE = numpy.array([])
assert isinstance(_NP_FMM_VENUE, numpy.ndarray)

_NP_PAM_DAYSPAKM = numpy.array([])
assert isinstance(_NP_PAM_DAYSPAKM, numpy.ndarray)

_NP_PAM_VENUE_FOCAL = numpy.array([])
assert isinstance(_NP_PAM_VENUE_FOCAL, numpy.ndarray)

_NP_PAM_VENUE = numpy.array([])
assert isinstance(_NP_PAM_VENUE, numpy.ndarray)

_ITERATIONS = 100000
_PATH = 'C:/development/python/focalpermute/data'
_RESULT_PATH = 'C:/development/python/focalpermute/data' # '.C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/WalesRSA-MSP/data/focalcorr'




def load_arrays():
    '''() -> void
    Load data previously exported as numpy arrays
    from arcgis for both FMM and PAM data.

    We will permute the study data then calculate 3x3 sliding windowed means
    then run a correlation against the already permuted data
    '''

    #FMM
    global _NP_FMM_VALUE
    _NP_FMM_VALUE = numpy.load(_PATH + '/NP_FMM_VALUE.np').astype(float)
    global _NP_FMM_VENUE_FOCAL
    _NP_FMM_VENUE_FOCAL = numpy.load(_PATH + '/NP_FMM_VENUE_FOCAL.np').astype(float)
    global _NP_FMM_VENUE
    _NP_FMM_VENUE = numpy.load(_PATH + '/NP_FMM_VENUE.np').astype(float)

    #_NP_FMM_VENUE_FOCAL has an extra column which needs to be deleted so arrays
    #are of same dims
    _NP_FMM_VENUE_FOCAL = numpy.delete(_NP_FMM_VENUE_FOCAL, 69, 1)
    if _NP_FMM_VALUE.shape != _NP_FMM_VENUE_FOCAL.shape:
        raise ValueError('FMM arrays not of the same shape')
    # same for _NP_FMM_VENUE but with an example of slicing
    _NP_FMM_VENUE = _NP_FMM_VENUE[0:56, 0:69]

    if not _NP_FMM_VENUE.shape == _NP_FMM_VALUE.shape == _NP_FMM_VENUE_FOCAL.shape:
        raise ValueError('FMM arrays not of the same shape')

    #PAM
    global _NP_PAM_DAYSPAKM
    _NP_PAM_DAYSPAKM = numpy.load(_PATH + '/' + 'NP_PAM_DAYSPAKM.np').astype(float)
    global _NP_PAM_VENUE_FOCAL
    _NP_PAM_VENUE_FOCAL = numpy.load(_PATH + '/' + 'NP_PAM_VENUE_FOCAL.np').astype(float)
    global _NP_PAM_VENUE
    _NP_PAM_VENUE = numpy.load(_PATH + '/' + 'PAMSansPAMVCntRaster.np').astype(float)
    if not _NP_PAM_DAYSPAKM.shape == _NP_PAM_VENUE_FOCAL.shape == _NP_PAM_VENUE.shape:
        raise ValueError('PAM arrays not of the same shape')

    #there were a small number of cells which existed in one but not the other
    #decided to resolve globally than on a 'per use' basis
    dic = arraylib.np_unmatched_nans_to_zero(_NP_FMM_VALUE, _NP_FMM_VENUE_FOCAL)
    _NP_FMM_VALUE = dic['a']
    _NP_FMM_VENUE_FOCAL = dic['b']

    dic = arraylib.np_unmatched_nans_to_zero(_NP_FMM_VALUE, _NP_FMM_VENUE)
    _NP_FMM_VALUE = dic['a']
    _NP_FMM_VENUE = dic['b']

    dic = arraylib.np_unmatched_nans_to_zero(_NP_FMM_VENUE_FOCAL, _NP_FMM_VENUE)
    _NP_FMM_VENUE_FOCAL = dic['a']
    _NP_FMM_VENUE = dic['b']

    dic = arraylib.np_unmatched_nans_to_zero(_NP_PAM_DAYSPAKM, _NP_PAM_VENUE_FOCAL)
    _NP_PAM_DAYSPAKM = dic['a']
    _NP_PAM_VENUE_FOCAL = dic['b']

def permutation_focal_all(permute, focal, file_prefix=''):
    '''(ndarray,ndarray,str) -> void
    test with zeros
    writes results to csv file
    '''
    outcsv = ([['Tau', 'p WRONG!!!']])
    
    for cnt in range(_ITERATIONS):       
        pre = '/* iter:' + str(cnt+1) + ' */'

        cor = arraylib.np_permute_2d(permute)
        cor = arraylib.np_focal_mean(cor, False)

        #use scipy - p will be wrong, but the taus will be right
        res = statslib.correlation(cor, focal, engine=statslib.EnumStatsEngine.scipy)
        
        outcsv.append([res['teststat'], res['p']])

        iolib.print_progress(cnt+1, _ITERATIONS, prefix=pre, bar_length=30)

    filename = _PATH + '/' + file_prefix + stringslib.datetime_stamp() + '.csv'
    iolib.writecsv(filename, outcsv, inner_as_rows=False)

  
def permutation_focal_no_zero(permute, focal, file_prefix=''):
    '''test without zeros'''
    outcsv = ([['Tau', 'p WRONG!!!']])
    a = numpy.copy(permute)
    b = numpy.copy(focal)

    lst = arraylib.np_paired_zeros_to_nan(a, b)

    for cnt in range(_ITERATIONS):       
        pre = '/* iter:' + str(cnt+1) + ' */'

        cor = arraylib.np_permute_2d(lst['a'])
        cor = arraylib.np_focal_mean(cor, False)

        #use scipy - p will be wrong, but the taus will be right
        res = statslib.correlation(cor, lst['b'], engine=statslib.EnumStatsEngine.scipy)
        
        outcsv.append([res['teststat'], res['p']])

        iolib.print_progress(cnt+1, _ITERATIONS, prefix=pre, bar_length=30)

    filename = _PATH + '/' + file_prefix + stringslib.datetime_stamp() + '.csv'
    iolib.writecsv(filename, outcsv, inner_as_rows=False)


def permutation(a, b, omit_paired_zeros=False):
    '''(ndarray,ndarray)  -> void
    takes two arrays and calculates tau then performs permutation
    test to see how many values are more extreme than the give one
    
    Results are printed to console
    '''
    if omit_paired_zeros:
        dic = arraylib.np_paired_zeros_to_nan(a, b)
    else:
        dic = {'a':a, 'b':b}
    
    dic = arraylib.np_unmatched_nans_to_zero(dic['a'], dic['b'])
    dic = arraylib.np_delete_paired_nans_flattened(dic['a'], dic['b'])
    if arraylib.np_contains_nan(dic['a']):
        raise ValueError('array "a" contains nans')

    if arraylib.np_contains_nan(dic['b']):
        raise ValueError('array "b" contains nans')

    tau = scipy.stats.kendalltau(dic['a'], dic['b'], nan_policy='propagate')[0]

    taus = []
    for cnt in range(_ITERATIONS):       
        pre = '/* iter:' + str(cnt+1) + ' */'

        #use general permute as we have flattened the array and should have no nans in it now
        dic['a'] = numpy.random.permutation(dic['a'])

        #use scipy - p will be wrong, but the taus will be right
        res = scipy.stats.kendalltau(dic['a'], dic['b'], nan_policy='propagate')[0]
        taus.append(res)

        iolib.print_progress(cnt+1, _ITERATIONS, prefix=pre, bar_length=30)

    out = statslib.permuted_teststat_check1(taus, tau)
    if omit_paired_zeros:
        s = '**ZEROS WERE OMITTED**'
    else:
        s = '**ZEROS WERE INCLUDED**'
    
    results = s + ' : p = %f, n = %d, more_extreme = %d, unpermuted_tau = %f' % (out['p'], out['n'], out['more_extreme_n'], tau)
    iolib.write_to_file(results)


#this also dumps out the data
def unpermuted_corr():
    '''calculate kendall tau for unpermuted values'''
    outcsv = [['Test', 'Tau', 'p']]
    results = dict()
    path = r'C:\development\python\focalpermute\data\cleaned'

    #we NaN pad all arrays to stop the problem of calculating edge effects
    #(although after mod this is now redundant)

    #region FOCAL

    #region FMM /w zeros
    nd_fmm_value_focal = numpy.copy(_NP_FMM_VALUE)
    nd_fmm_value_focal = arraylib.np_focal_mean(nd_fmm_value_focal, True)

    nd_venuefmm_focal = numpy.copy(_NP_FMM_VENUE_FOCAL).astype(float)
    nd_venuefmm_focal = arraylib.np_pad_nan(nd_venuefmm_focal)

    if nd_fmm_value_focal.shape != nd_venuefmm_focal.shape:
        raise ValueError('FMM arrays with zeros not of the same shape')


    dic = arraylib.np_delete_paired_nans_flattened(nd_fmm_value_focal, nd_venuefmm_focal)
    dic['a'].dump(path + r'\nd_fmm_value_focal_0_cleaned.np')
    dic['b'].dump(path + r'\nd_fmm_venue_focal_0_cleaned.np')

    results = statslib.correlation(dic['a'], dic['b'], engine=statslib.EnumStatsEngine.r)
    outcsv.append(['FMM Focal with Zeros', results['teststat'], results['p']])
    #endregion

    #region FMM /wo zeros
    dic = arraylib.np_delete_paired_zeros_flattened(dic['a'], dic['b'])

    if dic['a'].shape != dic['b'].shape:
        raise ValueError('FMM arrays witout zeros not of the same shape')

    dic['a'].dump(path + r'\nd_fmm_value_focal_No0_cleaned.np')
    dic['b'].dump(path + r'\nd_fmm_venue_focal_No0_cleaned.np')

    results = statslib.correlation(dic['a'], dic['b'], engine=statslib.EnumStatsEngine.r)
    outcsv.append(['FMM Focal without Zeros', results['teststat'], results['p']])
    #endregion
    
    #region PAM /w zeros

    #calculate this oneon the fly, others focals are loaded from already exported data
    nd_pam_dayspa_focal = numpy.copy(_NP_PAM_DAYSPAKM).astype(float)
    nd_pam_dayspa_focal = arraylib.np_focal_mean(nd_pam_dayspa_focal, True)
    
    nd_venuepam_focal = numpy.copy(_NP_PAM_VENUE_FOCAL).astype(float)
    #pad to make same dimensions as dayspa, padding is not included in corr anal
    nd_venuepam_focal = arraylib.np_pad_nan(nd_venuepam_focal)

    if nd_pam_dayspa_focal.shape != nd_venuepam_focal.shape:
        raise ValueError('PAM arrays not of the same shape')

    dic = arraylib.np_delete_paired_nans_flattened(nd_pam_dayspa_focal, nd_venuepam_focal)
    dic['a'].dump(path + r'\nd_pam_dayspa_focal_0_cleaned.np')
    dic['b'].dump(path + r'\nd_pam_venue_focal_0_cleaned.np')

    results = statslib.correlation(dic['a'], dic['b'], engine=statslib.EnumStatsEngine.r)
    outcsv.append(['PAM Focal with Zeros', results['teststat'], results['p']])
    #endregion

    #region PAM /wo zeros
    dic = arraylib.np_delete_paired_zeros_flattened(dic['a'], dic['b'])
    if dic['a'].shape != dic['b'].shape:
        raise ValueError('PAM arrays witout zeros not of the same shape')
    
    dic['a'].dump(path + r'\nd_pam_dayspa_focal_No0_cleaned.np')
    dic['b'].dump(path + r'\nd_pam_venue_focal_No0_cleaned.np')

    results = statslib.correlation(dic['a'], dic['b'], engine=statslib.EnumStatsEngine.r)
    outcsv.append(['PAM Focal without Zeros', results['teststat'], results['p']])
    #endregion
    #endregion


    #region CRISP STUFF

    #region FMM /w zeros
    nd_fmm_value = numpy.copy(_NP_FMM_VALUE).astype(float)
    nd_fmm_venue = numpy.copy(_NP_FMM_VENUE).astype(float)

    dic = arraylib.np_delete_paired_nans_flattened(nd_fmm_value, nd_fmm_venue)

    if dic['a'].shape != dic['b'].shape:
        raise ValueError('FMM non focal arrays with zeros not of the same shape')

    if arraylib.np_contains_nan(dic['a']):
        raise ValueError('nd_fmm_value has nans')

    if arraylib.np_contains_nan(dic['b']):
        raise ValueError('nd_fmm_venue has nans')

    dic['a'].dump(path + r'\nd_fmm_value_0_cleaned.np')
    dic['b'].dump(path + r'\nd_fmm_venue_0_cleaned.np')

    results = statslib.correlation(dic['a'], dic['b'], engine=statslib.EnumStatsEngine.r)
    outcsv.append(['FMM NON FOCAL with Zeros', results['teststat'], results['p']])
    #endregion
    

    #region FMM /wo zeros
    dic = arraylib.np_delete_paired_zeros_flattened(dic['a'], dic['b'])
    if dic['a'].shape != dic['b'].shape:
        raise ValueError('FMM non focal arrays without zeros not of the same shape')

    dic['a'].dump(path + r'\nd_fmm_value_No0_cleaned.np')
    dic['b'].dump(path + r'\nd_fmm_venue_No0_cleaned.np')    
      
    results = statslib.correlation(dic['a'], dic['b'], engine=statslib.EnumStatsEngine.r)
    outcsv.append(['FMM NON FOCAL without Zeros', results['teststat'], results['p']])
    #endregion

    #region PAM /w zeros
    nd_pam_dayspa = numpy.copy(_NP_PAM_DAYSPAKM).astype(float)
    nd_venuepam = numpy.copy(_NP_PAM_VENUE).astype(float)
    dic = arraylib.np_delete_paired_nans_flattened(nd_pam_dayspa, nd_venuepam)

    if dic['a'].shape != dic['b'].shape:
        raise ValueError('PAM arrays not of the same shape')

    if arraylib.np_contains_nan(dic['a']):
        raise ValueError('nd_pam_dayspa has nans')

    if arraylib.np_contains_nan(dic['b']):
        raise ValueError('nd_venuepam has nans')

    dic['a'].dump(path + r'\nd_pam_dayspa_0_cleaned.np')
    dic['b'].dump(path + r'\nd_pam_venue_0_cleaned.np')

    results = statslib.correlation(dic['a'], dic['b'], engine=statslib.EnumStatsEngine.r)
    outcsv.append(['PAM NON FOCAL with Zeros', results['teststat'], results['p']])
    #endregion

    #region PAM /wo zeros
    dic = arraylib.np_delete_paired_zeros_flattened(dic['a'], dic['b'])
    if dic['a'].shape != dic['b'].shape:
        raise ValueError('PAM non focal arrays without zeros not of the same shape')

    dic['a'].dump(path + r'\nd_pam_dayspa_No0_cleaned.np')
    dic['b'].dump(path + r'\nd_pam_venue_No0_cleaned.np')    
      
    results = statslib.correlation(dic['a'], dic['b'], engine=statslib.EnumStatsEngine.r)
    outcsv.append(['PAM NON FOCAL without Zeros', results['teststat'], results['p']])
    #endregion
    #endregion
    
        
    filename = _PATH + '/unpermuted_' + stringslib.datetime_stamp() + '.csv'
    iolib.writecsv(filename, outcsv, inner_as_rows=False)


def calculate_p():
    '''calculate p values from permuted taus
    '''
        
    #header row
    res = [['test', 'n', 'more_extreme_n', 'p', 'teststat']]

    #FMM Focal with zeros
    tau = 0.38099216491130256
    test = 'FMM Focal with zeros'
    dic = statslib.permuted_teststat_check(_RESULT_PATH + '/fmm_0_20160716180726.csv', 0, tau)
    res.append([test, dic['n'], dic['more_extreme_n'], dic['p'], tau])

    #FMM Focal without zeros
    tau = 0.3288618472771732
    test = 'FMM Focal without zeros'
    dic = statslib.permuted_teststat_check(_RESULT_PATH + '/fmm_no0_20160716200708.csv', 0, tau)
    res.append([test, dic['n'], dic['more_extreme_n'], dic['p'], tau])

    #PAM Focal with Zeros
    tau = 0.2504477456968775
    test = 'PAM Focal with zeros'
    dic = statslib.permuted_teststat_check(_RESULT_PATH + '/pam_No0_20160723200744.csv', 0, tau)
    res.append([test, dic['n'], dic['more_extreme_n'], dic['p'], tau])

    #PAM Focal Without Zeros
    tau = 0.14656599127578984
    test = 'PAM Focal without zeros'
    dic = statslib.permuted_teststat_check(_RESULT_PATH + '/pam_No0_20160723200744.csv', 0, tau)
    res.append([test, dic['n'], dic['more_extreme_n'], dic['p'], tau])

    iolib.writecsv(_RESULT_PATH + '/permStats_' + stringslib.datetime_stamp() + '.csv', res, inner_as_rows=False)


def permute_test_with_random(iterations=10):
    '''test how tau is affected by focal with normal random data
    '''
    #first copy our original matrices and fill them with data where not NaN
    #fname = 'random' + stringslib.datetime_stamp() + '.csv'
    #out = open(stringslib.add_right(_RESULT_PATH, '/') + fname, 'w+')
    #out.write('unpermuted,%f,%f\n' % (tau))
    #print 'unpermuted,%f,%f\n' % (tau, p)
    lst = []

    for i in range(iterations):
        y = numpy.random.normal(size=[50, 50])
        x = numpy.random.normal(size=[50, 50])
    
        #calculate original correlation
        tau = scipy.stats.pearsonr(x.flatten(), y.flatten())[0]
        
        y = arraylib.np_focal_mean(y, False).flatten()
        x = arraylib.np_focal_mean(x, False).flatten()
        tau_focal = scipy.stats.pearsonr(x.flatten(), y.flatten())[0]
        lst.append([tau, tau_focal])
        iolib.print_progress(i, iterations, 'iter:%d' % (i), bar_length=30)

    np = numpy.array(lst)
    p = (np[:, 0] > np[:, 1]).sum()/float(len(np))
    print('\n')
    print('p[tau_focal > tau] = %f' % (p))


def set_iter():
    '''get user to input number of iterations'''
    global _ITERATIONS
    _ITERATIONS = iolib.input_int(prompt='Input number of interations :')




#region Top Level Calls
def run_fmm_focal():
    '''run fmm focal'''
    permutation_focal_all(_NP_FMM_VALUE, _NP_FMM_VENUE_FOCAL, 'fmm_0_')
    permutation_focal_no_zero(_NP_FMM_VALUE, _NP_FMM_VENUE_FOCAL, 'fmm_no0_')

def run_pam_focal():
    '''run pam focal'''
    permutation_focal_all(_NP_PAM_DAYSPAKM, _NP_PAM_VENUE_FOCAL, 'pam_0_')
    permutation_focal_no_zero(_NP_PAM_DAYSPAKM, _NP_PAM_VENUE_FOCAL, 'pam_No0_')

def run_pam_permutation():
    '''run the pam permutation correlation analysis on non-focal data
    results outputted to txt file and console
    This is a recalculation because old figures included PAM data itself
    '''
    permutation(_NP_PAM_VENUE, _NP_PAM_DAYSPAKM, False)
    permutation(_NP_PAM_VENUE, _NP_PAM_DAYSPAKM, True)


#region Time tests
def omit():
    '''omit time test'''
    tau = scipy.stats.kendalltau(_NP_PAM_VENUE, _NP_PAM_DAYSPAKM, nan_policy='omit')[0]
    print(tau)

def propogate():
    '''prop test'''
    x = numpy.arange(118*77).reshape(118, 77)
    y = numpy.arange(118*77).reshape(118, 77)
    tau = scipy.stats.kendalltau(x, y, nan_policy='propagate')[0]
    print(tau)

def test_speed():
    '''test performance'''
    omit()
    propogate()
#end region
    
    
#endregion


#region Init
#set_iter()
#load_arrays()

#unpermuted_corr()
#test_speed()
#run_pam_permutation()
#endregion
#run_pam_focal()

#reg1ion End of program housekeeping
#iolib.folder_open(_RESULT_PATH)
#print 'Done'
#endregion
