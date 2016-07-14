'''Main entry module to perform the permutation analysis'''

#base
import sys

#custom
import numpy

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

_ITERATIONS = 100000
_PATH = 'C:\\Users\\Graham Monkman\\OneDrive\\Documents\\PHD\\My Papers\\WalesRSA-MSP\\data\\focalcorr'




def load_arrays():
    '''() -> void
    Load data previously exported as numpy arrays
    from arcgis for both FMM and PAM data.

    We will permute the study data then calculate 3x3 sliding windowed means
    then run a correlation against the already permuted data
    '''

    #FMM
    global _NP_FMM_VALUE
    _NP_FMM_VALUE = numpy.load(_PATH + '\\NP_FMM_VALUE.np')
    global _NP_FMM_VENUE_FOCAL
    _NP_FMM_VENUE_FOCAL = numpy.load(_PATH + '\\NP_FMM_VENUE_FOCAL.np')

    #_NP_FMM_VENUE_FOCAL has an extra column which needs to be deleted so arrays
    #are of same dims
    _NP_FMM_VENUE_FOCAL = numpy.delete(_NP_FMM_VENUE_FOCAL, 69, 1)

    if _NP_FMM_VALUE.shape != _NP_FMM_VENUE_FOCAL.shape:
        raise ValueError('FMM arrays not of the same shape')

    #PAM
    global _NP_PAM_DAYSPAKM
    _NP_PAM_DAYSPAKM = numpy.load(_PATH + '\\' + 'NP_PAM_DAYSPAKM.np')
    global _NP_PAM_VENUE_FOCAL 
    _NP_PAM_VENUE_FOCAL = numpy.load(_PATH + '\\' + 'NP_PAM_VENUE_FOCAL.np')
    if _NP_PAM_DAYSPAKM.shape != _NP_PAM_VENUE_FOCAL.shape:
        raise ValueError('PAM arrays not of the same shape')


def fmm_all():
    '''do the fmm work including zeros'''
    outcsv = (['Tau', 'p'])

    for cnt in range(_ITERATIONS-1):       
        pre = '/* iter:' + str(cnt) + ' */'

        cor = funclib.arraylib.np_permute_2d(_NP_FMM_VALUE)
        dic = funclib.statslib.correlation(cor, _NP_FMM_VENUE_FOCAL, engine=funclib.statslib.EnumStatsEngine.r)
        outcsv.append([dic['teststat'], dic['p']])

        funclib.iolib.print_progress(cnt, _ITERATIONS, prefix=pre, bar_length=30)

    filename = _PATH + '\\fmm_0_' + funclib.stringslib.datetime_stamp + '.csv'
    funclib.iolib.writecsv(filename, outcsv, ['Tau', 'p'], False)




def unpermuted_corr():
    '''calculate kendall tau for unpermuted values'''
    outcsv = ['Test', 'Tau', 'p']
    results = dict()

    #we NaN pad all arrays to stop the problem of calculating edge effects


    #FMM /w zeros
    nd_fmm_value_focal = numpy.copy(_NP_FMM_VALUE)
    nd_fmm_value_focal = funclib.arraylib.np_pad_nan(nd_fmm_value_focal)
    nd_fmm_value_focal = funclib.arraylib.np_focal_mean(nd_fmm_value_focal, False)
    numpy.savetxt('C:\\Users\\Graham Monkman\\OneDrive\\Documents\\PHD\\My Papers\\WalesRSA-MSP\\data\\focalcorr\\nd_fmm_value_focal.csv', nd_fmm_value_focal, delimiter=',')

    nd_venuefmm = numpy.copy(_NP_FMM_VENUE_FOCAL)
    nd_venuefmm = funclib.arraylib.np_pad_nan(nd_venuefmm)
    numpy.savetxt('C:\\Users\\Graham Monkman\\OneDrive\\Documents\\PHD\\My Papers\\WalesRSA-MSP\\data\\focalcorr\\nd_venuefmm.csv', nd_venuefmm, delimiter=',')

    if nd_fmm_value_focal.shape != nd_venuefmm.shape:
        raise ValueError('FMM arrays not of the same shape')

    results = funclib.statslib.correlation(nd_fmm_value_focal, nd_venuefmm, engine=funclib.statslib.EnumStatsEngine.r)
    outcsv.append(['FMM Focal with Zeros', results['teststat'], results['p']])

    #PAM /w zeros
    nd_pam_dayspa_focal = numpy.copy(_NP_PAM_DAYSPAKM)
    nd_pam_dayspa_focal = funclib.arraylib.np_pad_nan(nd_pam_dayspa_focal)
    nd_pam_dayspa_focal = funclib.arraylib.np_focal_mean(nd_pam_dayspa_focal, False)

    nd_venuepam = numpy.copy(_NP_FMM_VENUE_FOCAL)
    nd_venuepam = funclib.arraylib.np_pad_nan(nd_venuepam)

    if nd_pam_dayspa_focal.shape != nd_venuepam.shape:
        raise ValueError('PAM arrays not of the same shape')

    results = funclib.statslib.correlation(nd_pam_dayspa_focal, nd_venuepam, engine=funclib.statslib.EnumStatsEngine.r)
    outcsv.append(['PAM Focal with Zeros', results['teststat'], results['p']])

    filename = _PATH + '\\unpermuted_' + funclib.stringslib.datetime_stamp + '.csv'
    funclib.iolib.writecsv(filename, outcsv, inner_as_rows=False)



load_arrays()
unpermuted_corr()
#fmm_all()
sys.exit()
