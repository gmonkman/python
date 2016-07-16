'''Main entry module to perform the permutation analysis'''

#base
import sys

#custom
import numpy
import xlwings

#mine
import funclib.iolib
import funclib.statslib
import funclib.arraylib
import funclib.stringslib

_NP_FMM_VALUE = numpy.array([])
assert isinstance(_NP_FMM_VALUE, numpy.ndarray)

_NP_FMM_VENUE_FOCAL = numpy.array([])
assert isinstance(_NP_FMM_VENUE_FOCAL, numpy.ndarray)

_NP_PAM_DAYSPAKM = numpy.array([])
assert isinstance(_NP_PAM_DAYSPAKM, numpy.ndarray)

_NP_PAM_VENUE_FOCAL = numpy.array([])
assert isinstance(_NP_PAM_VENUE_FOCAL, numpy.ndarray)

_ITERATIONS = 20
_PATH = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/WalesRSA-MSP/data/focalcorr'




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
    dic = funclib.arraylib.np_unmatched_nans_to_zero(_NP_FMM_VALUE, _NP_FMM_VENUE_FOCAL)
    _NP_FMM_VALUE = dic['a']
    _NP_FMM_VENUE_FOCAL = dic['b']

    dic = funclib.arraylib.np_unmatched_nans_to_zero(_NP_PAM_DAYSPAKM, _NP_PAM_VENUE_FOCAL)
    _NP_PAM_DAYSPAKM = dic['a']
    _NP_PAM_VENUE_FOCAL = dic['b']




def fmm_all():
    '''do the fmm work including zeros'''
    outcsv = ([['Tau', 'p WRONG!!!']])
    
    for cnt in range(_ITERATIONS-1):       
        pre = '/* iter:' + str(cnt) + ' */'

        cor = funclib.arraylib.np_permute_2d(_NP_FMM_VALUE)
        cor = funclib.arraylib.np_focal_mean(cor, False)

        #use scipy - p will be wrong, but the taus will be right
        res = funclib.statslib.correlation(cor, _NP_FMM_VENUE_FOCAL, engine=funclib.statslib.EnumStatsEngine.scipy)
        
        outcsv.append([res['teststat'], res['p']])

        funclib.iolib.print_progress(cnt+1, _ITERATIONS, prefix=pre, bar_length=30)

    filename = _PATH + '/fmm_0_' + funclib.stringslib.datetime_stamp() + '.csv'
    funclib.iolib.writecsv(filename, outcsv, inner_as_rows=False)
    
def fmm_no_zero():
    '''do the fmm work including zeros'''
    outcsv = ([['Tau', 'p WRONG!!!']])
    a = numpy.copy(_NP_FMM_VALUE)
    b = numpy.copy(_NP_FMM_VENUE_FOCAL)

    lst = funclib.arraylib.np_paired_zeros_to_nan(a, b)

    for cnt in range(_ITERATIONS-1):       
        pre = '/* iter:' + str(cnt) + ' */'

        cor = funclib.arraylib.np_permute_2d(lst['a'])
        cor = funclib.arraylib.np_focal_mean(cor, False)

        #use scipy - p will be wrong, but the taus will be right
        res = funclib.statslib.correlation(cor, lst['b'], engine=funclib.statslib.EnumStatsEngine.scipy)
        
        outcsv.append([res['teststat'], res['p']])

        funclib.iolib.print_progress(cnt+1, _ITERATIONS, prefix=pre, bar_length=30)

    filename = _PATH + '/fmm_No0_' + funclib.stringslib.datetime_stamp() + '.csv'
    funclib.iolib.writecsv(filename, outcsv, inner_as_rows=False)


def unpermuted_corr():
    '''calculate kendall tau for unpermuted values'''
    outcsv = [['Test', 'Tau', 'p']]
    results = dict()

    #we NaN pad all arrays to stop the problem of calculating edge effects
    #(although after mod this is now redundant)


    #FMM /w zeros
    nd_fmm_value_focal = numpy.copy(_NP_FMM_VALUE)
    #numpy.savetxt('C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/WalesRSA-MSP/data/focalcorr/nd_fmm_value.csv', nd_fmm_value_focal, delimiter=',')
    nd_fmm_value_focal = funclib.arraylib.np_focal_mean(nd_fmm_value_focal, True)
    #numpy.savetxt('C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/WalesRSA-MSP/data/focalcorr/nd_fmm_value_focal.csv', nd_fmm_value_focal, delimiter=',')

    nd_venuefmm = numpy.copy(_NP_FMM_VENUE_FOCAL).astype(float)
    nd_venuefmm = funclib.arraylib.np_pad_nan(nd_venuefmm)
    #numpy.savetxt('C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/WalesRSA-MSP/data/focalcorr/nd_venuefmm.csv', nd_venuefmm, delimiter=',')

    if nd_fmm_value_focal.shape != nd_venuefmm.shape:
        raise ValueError('FMM arrays with zeros not of the same shape')

    results = funclib.statslib.correlation(nd_fmm_value_focal, nd_venuefmm, engine=funclib.statslib.EnumStatsEngine.r)
    outcsv.append(['FMM Focal with Zeros', results['teststat'], results['p']])


    #FMM /wo zeros
    dic = funclib.arraylib.np_delete_paired_nans_flattened(nd_fmm_value_focal, nd_venuefmm)
    dic = funclib.arraylib.np_delete_paired_zeros_flattened(dic['a'], dic['b'])
    numpy.savetxt('C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/WalesRSA-MSP/data/focalcorr/nd_fmm_value_focal.csv', dic['a'], delimiter=',')
    numpy.savetxt('C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/WalesRSA-MSP/data/focalcorr/nd_venuefmm.csv', dic['b'], delimiter=',')

    if dic['a'].shape != dic['b'].shape:
        raise ValueError('FMM arrays witout zeros not of the same shape')

    results = funclib.statslib.correlation(dic['a'], dic['b'], engine=funclib.statslib.EnumStatsEngine.r)
    outcsv.append(['FMM Focal without Zeros', results['teststat'], results['p']])

    
    #PAM /w zeros
    nd_pam_dayspa_focal = numpy.copy(_NP_PAM_DAYSPAKM).astype(float)
    nd_pam_dayspa_focal = funclib.arraylib.np_focal_mean(nd_pam_dayspa_focal, True)

    nd_venuepam = numpy.copy(_NP_PAM_VENUE_FOCAL).astype(float)
    #pad to make same dimensions as dayspa, padding is not included in corr anal
    nd_venuepam = funclib.arraylib.np_pad_nan(nd_venuepam)

    if nd_pam_dayspa_focal.shape != nd_venuepam.shape:
        raise ValueError('PAM arrays not of the same shape')

    results = funclib.statslib.correlation(nd_pam_dayspa_focal, nd_venuepam, engine=funclib.statslib.EnumStatsEngine.r)
    outcsv.append(['PAM Focal with Zeros', results['teststat'], results['p']])

    #PAM /wo zeros
    dic = funclib.arraylib.np_delete_paired_nans_flattened(nd_pam_dayspa_focal, nd_venuepam)
    dic = funclib.arraylib.np_delete_paired_zeros_flattened(dic['a'], dic['b'])
    if dic['a'].shape != dic['b'].shape:
        raise ValueError('PAM arrays witout zeros not of the same shape')
    
    results = funclib.statslib.correlation(dic['a'], dic['b'], engine=funclib.statslib.EnumStatsEngine.r)
    outcsv.append(['PAM Focal without Zeros', results['teststat'], results['p']])


    filename = _PATH + '/unpermuted_' + funclib.stringslib.datetime_stamp() + '.csv'
    funclib.iolib.writecsv(filename, outcsv, inner_as_rows=False)





load_arrays()
#unpermuted_corr()
#fmm_all()
fmm_no_zero()

funclib.iolib.folder_open(_PATH)
sys.exit()
