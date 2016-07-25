'''Main entry module to perform the permutation analysis'''

#custom
import numpy
import scipy.stats

#mine
import funclib.iolib as iolib
import funclib.statslib as statslib
import funclib.arraylib as arraylib
import funclib.stringslib as stringslib

_NP_FMM_VALUE = numpy.array([])
assert isinstance(_NP_FMM_VALUE, numpy.ndarray)

_NP_FMM_VENUE_FOCAL = numpy.array([])
assert isinstance(_NP_FMM_VENUE_FOCAL, numpy.ndarray)

_NP_PAM_DAYSPAKM = numpy.array([])
assert isinstance(_NP_PAM_DAYSPAKM, numpy.ndarray)

_NP_PAM_VENUE_FOCAL = numpy.array([])
assert isinstance(_NP_PAM_VENUE_FOCAL, numpy.ndarray)

_ITERATIONS = 100000
_PATH = './data'

_RESULT_PATH = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/WalesRSA-MSP/data/focalcorr'


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

    #_NP_FMM_VENUE_FOCAL has an extra column which needs to be deleted so arrays
    #are of same dims
    _NP_FMM_VENUE_FOCAL = numpy.delete(_NP_FMM_VENUE_FOCAL, 69, 1)

    if _NP_FMM_VALUE.shape != _NP_FMM_VENUE_FOCAL.shape:
        raise ValueError('FMM arrays not of the same shape')

    #PAM
    global _NP_PAM_DAYSPAKM
    _NP_PAM_DAYSPAKM = numpy.load(_PATH + '/' + 'NP_PAM_DAYSPAKM.np').astype(float)
    global _NP_PAM_VENUE_FOCAL
    _NP_PAM_VENUE_FOCAL = numpy.load(_PATH + '/' + 'NP_PAM_VENUE_FOCAL.np').astype(float)
    if _NP_PAM_DAYSPAKM.shape != _NP_PAM_VENUE_FOCAL.shape:
        raise ValueError('PAM arrays not of the same shape')

    #there were a small number of cells which existed in one but not the other
    #decided to resolve globally than on a 'per use' basis
    dic = arraylib.np_unmatched_nans_to_zero(_NP_FMM_VALUE, _NP_FMM_VENUE_FOCAL)
    _NP_FMM_VALUE = dic['a']
    _NP_FMM_VENUE_FOCAL = dic['b']

    dic = arraylib.np_unmatched_nans_to_zero(_NP_PAM_DAYSPAKM, _NP_PAM_VENUE_FOCAL)
    _NP_PAM_DAYSPAKM = dic['a']
    _NP_PAM_VENUE_FOCAL = dic['b']


def test_all(permute, focal, file_prefix=''):
    '''test with zeros
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

    
def test_no_zero(permute, focal, file_prefix=''):
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


def unpermuted_corr():
    '''calculate kendall tau for unpermuted values'''
    outcsv = [['Test', 'Tau', 'p']]
    results = dict()

    #we NaN pad all arrays to stop the problem of calculating edge effects
    #(although after mod this is now redundant)


    #FMM /w zeros
    nd_fmm_value_focal = numpy.copy(_NP_FMM_VALUE)
    #numpy.savetxt('C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/WalesRSA-MSP/data/focalcorr/nd_fmm_value.csv', nd_fmm_value_focal, delimiter=',')
    nd_fmm_value_focal = arraylib.np_focal_mean(nd_fmm_value_focal, True)
    #numpy.savetxt('C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/WalesRSA-MSP/data/focalcorr/nd_fmm_value_focal.csv', nd_fmm_value_focal, delimiter=',')

    nd_venuefmm = numpy.copy(_NP_FMM_VENUE_FOCAL).astype(float)
    nd_venuefmm = arraylib.np_pad_nan(nd_venuefmm)
    #numpy.savetxt('C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/WalesRSA-MSP/data/focalcorr/nd_venuefmm.csv', nd_venuefmm, delimiter=',')

    if nd_fmm_value_focal.shape != nd_venuefmm.shape:
        raise ValueError('FMM arrays with zeros not of the same shape')

    results = statslib.correlation(nd_fmm_value_focal, nd_venuefmm, engine=statslib.EnumStatsEngine.r)
    outcsv.append(['FMM Focal with Zeros', results['teststat'], results['p']])


    #FMM /wo zeros
    dic = arraylib.np_delete_paired_nans_flattened(nd_fmm_value_focal, nd_venuefmm)
    dic = arraylib.np_delete_paired_zeros_flattened(dic['a'], dic['b'])
    #numpy.savetxt('C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/WalesRSA-MSP/data/focalcorr/nd_fmm_value_focal.csv', dic['a'], delimiter=',')
    #numpy.savetxt('C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/WalesRSA-MSP/data/focalcorr/nd_venuefmm.csv', dic['b'], delimiter=',')

    if dic['a'].shape != dic['b'].shape:
        raise ValueError('FMM arrays witout zeros not of the same shape')

    results = statslib.correlation(dic['a'], dic['b'], engine=statslib.EnumStatsEngine.r)
    outcsv.append(['FMM Focal without Zeros', results['teststat'], results['p']])

    
    #PAM /w zeros
    nd_pam_dayspa_focal = numpy.copy(_NP_PAM_DAYSPAKM).astype(float)
    nd_pam_dayspa_focal = arraylib.np_focal_mean(nd_pam_dayspa_focal, True)

    nd_venuepam = numpy.copy(_NP_PAM_VENUE_FOCAL).astype(float)
    #pad to make same dimensions as dayspa, padding is not included in corr anal
    nd_venuepam = arraylib.np_pad_nan(nd_venuepam)

    if nd_pam_dayspa_focal.shape != nd_venuepam.shape:
        raise ValueError('PAM arrays not of the same shape')

    results = statslib.correlation(nd_pam_dayspa_focal, nd_venuepam, engine=statslib.EnumStatsEngine.r)
    outcsv.append(['PAM Focal with Zeros', results['teststat'], results['p']])

    #PAM /wo zeros
    dic = arraylib.np_delete_paired_nans_flattened(nd_pam_dayspa_focal, nd_venuepam)
    dic = arraylib.np_delete_paired_zeros_flattened(dic['a'], dic['b'])
    if dic['a'].shape != dic['b'].shape:
        raise ValueError('PAM arrays witout zeros not of the same shape')
    
    results = statslib.correlation(dic['a'], dic['b'], engine=statslib.EnumStatsEngine.r)
    outcsv.append(['PAM Focal without Zeros', results['teststat'], results['p']])


    filename = _PATH + '/unpermuted_' + stringslib.datetime_stamp() + '.csv'
    iolib.writecsv(filename, outcsv, inner_as_rows=False)




def calculate_p():
    '''calculate permuted p values
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




def permute_test_with_random(iter=10):
    '''test how tau is affected by focal with normal random data
    '''
    #first copy our original matrices and fill them with data where not NaN
    #fname = 'random' + stringslib.datetime_stamp() + '.csv'
    #out = open(stringslib.add_right(_RESULT_PATH, '/') + fname, 'w+')
    #out.write('unpermuted,%f,%f\n' % (tau))
    #print 'unpermuted,%f,%f\n' % (tau, p)
    lst = []
    cnt = 0
    for i in range(iter):
        y = numpy.random.normal(size=[50,50])
        x = numpy.random.normal(size=[50,50])
    
        #calculate original correlation
        tau = scipy.stats.pearsonr(x.flatten(), y.flatten())[0]
        
        y = arraylib.np_focal_mean(y, False).flatten()
        x = arraylib.np_focal_mean(x, False).flatten()
        tau_focal = scipy.stats.pearsonr(x.flatten(), y.flatten())[0]
        lst.append([tau,tau_focal])
        iolib.print_progress(cnt+1, iter, 'iter:%d' % (cnt), bar_length=30)
        cnt += 1

    np = numpy.array(lst)
    p = (np[:,0]>np[:,1]).sum()/float(len(np))
    print '\n'
    print 'p[tau_focal > tau] = %f' % (p)

#load_arrays()
#unpermuted_corr()

#Change the file names of the permuted results and run this to calculate p values
#calculate_p()



#CALL FOR FMM STUFF
#test_all(_NP_FMM_VALUE, _NP_FMM_VENUE_FOCAL, 'fmm_0_')
#test_no_zero(_NP_FMM_VALUE, _NP_FMM_VENUE_FOCAL, 'fmm_no0_')

#CALL FOR PAM STUFF
#test_all(_NP_PAM_DAYSPAKM, _NP_PAM_VENUE_FOCAL, 'pam_0_')
#test_no_zero(_NP_PAM_DAYSPAKM, _NP_PAM_VENUE_FOCAL, 'pam_No0_')

#iolib.folder_open(_PATH)
permute_test_with_random()
print 'Done'
