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

NP_FMM_VALUE = numpy.array([])
assert isinstance(NP_FMM_VALUE, numpy.ndarray)

NP_FMM_VENUE_FOCAL = numpy.array([])
assert isinstance(NP_FMM_VENUE_FOCAL, numpy.ndarray)

NP_PAM_DAYSPAKM = numpy.array([])
assert isinstance(NP_PAM_DAYSPAKM, numpy.ndarray)

NP_PAM_VENUE_FOCAL = numpy.array([])
assert isinstance(NP_PAM_VENUE_FOCAL, numpy.ndarray)

ITERATIONS = 100000
PATH = 'C:\\Users\\Graham Monkman\\OneDrive\\Documents\\PHD\\My Papers\\WalesRSA-MSP\\data\\focalcorr'

def load_arrays():
    '''() -> void
    Load data previously exported as numpy arrays
    from arcgis for both FMM and PAM data.

    We will permute the study data then calculate 3x3 sliding windowed means
    then run a correlation against the already permuted data
    '''

    #FMM
    global NP_FMM_VALUE
    NP_FMM_VALUE = numpy.load(PATH + '\\NP_FMM_VALUE.np')
    global NP_FMM_VENUE_FOCAL
    NP_FMM_VENUE_FOCAL = numpy.load(PATH + '\\NP_FMM_VENUE_FOCAL.np')
    #NP_FMM_VENUE_FOCAL has an extra column which should be deleted
    NP_FMM_VENUE_FOCAL = numpy.delete(NP_FMM_VENUE_FOCAL, 69, 1)
    if NP_FMM_VALUE.shape != NP_FMM_VENUE_FOCAL.shape:
        raise ValueError('FMM arrays not of the same shape')

    #PAM
    global NP_PAM_DAYSPAKM
    NP_PAM_DAYSPAKM = numpy.load(PATH + '\\' + 'NP_PAM_DAYSPAKM.np')
    global NP_PAM_VENUE_FOCAL 
    NP_PAM_VENUE_FOCAL = numpy.load(PATH + '\\' + 'NP_PAM_VENUE_FOCAL.np')
    if NP_PAM_DAYSPAKM.shape != NP_PAM_VENUE_FOCAL.shape:
        raise ValueError('PAM arrays not of the same shape')


def fmm_all():
    '''do the fmm work including zeros'''
    results = (['Tau', 'p'])

    for cnt in range(ITERATIONS-1):       
        pre = '/* iter:' + str(cnt) + ' */'

        cor = funclib.arraylib.np_permute_2d(NP_FMM_VALUE)
        dic = funclib.statslib.correlation(cor, NP_FMM_VENUE_FOCAL, engine=funclib.statslib.EnumStatsEngine.r)
        results.append([dic['teststat'], dic['p']])

        funclib.iolib.print_progress(cnt, ITERATIONS, prefix=pre, bar_length=30)
    
        filename = PATH + '\\' + fmm_all_funclib.stringslib.datetime_stamp + '.csv'
    
    funclib.iolib.writecsv(filename, results, ['Tau','p'], False)

load_arrays()
fmm_all()
sys.exit()