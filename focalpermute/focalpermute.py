'''Main entry module to perform the permutation analysis
'''

#base

#custom
import numpy

#mine
import funclib
import arcgis.rasterlib

np_fmm_value = numpy.array([])
assert isinstance(np_fmm_venue_focal, numpy.ndarray)

np_fmm_venue_focal = numpy.array([])
assert isinstance(np_fmm_value, numpy.ndarray)

np_pam_dayspakm = numpy.array([])
assert isinstance(np_pam_dayspakm, numpy.ndarray)

np_pam_venue_focal = numpy.array([])
assert isinstance(np_pam_venue_focal, numpy.ndarray)

path = 'C:\\Users\\Graham Monkman\\OneDrive\\Documents\\PHD\\My Papers\\WalesRSA-MSP\\data\\focalcorr'
def load_arrays():
    '''() -> void
    test the fmm focal data
    '''

    #FMM
    global np_fmm_value
    np_fmm_value = numpy.load(path + '\\np_fmm_value.np')
    global np_fmm_venue_focal
    np_fmm_venue_focal = numpy.load(path + '\\np_fmm_venue_focal.np')

    #PAM
    global np_pam_dayspakm 
    np_pam_dayspakm = numpy.load(path + '\\' + 'np_pam_dayspakm.np')
    global np_pam_venue_focal 
    np_pam_venue_focal = numpy.load(path + '\\' + 'np_pam_venue_focal.np')


load_arrays()
