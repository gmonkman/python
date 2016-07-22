'''run tests'''
import numpy
import arcpy

_GDBPATH = 'C:\\Users\\Graham Monkman\\OneDrive\\Documents\\PHD\\My Papers\\WalesRSA-MSP\\GIS\\RSA-MSP-SCRATCH.gdb'
_OUTPUT_PATH = 'C:\\Users\\Graham Monkman\\OneDrive\\Documents\\PHD\\My Papers\\WalesRSA-MSP\\data\\focalcorr'

def dump_msp_paper_arrays():
    '''test the fmm focal data
    '''

    #FMM
    fmm_value = arcpy.Raster(_GDBPATH + '\\FMMValuetoRaster')
    np_fmm_value = arcpy.RasterToNumPyArray(fmm_value, nodata_to_value=numpy.nan)
    assert isinstance(np_fmm_value, numpy.ndarray)
    np_fmm_value.dump(_OUTPUT_PATH + '\\np_fmm_value.np')
    print 'Dumped FMMValuetoRaster'

    fmm_venue_focal = arcpy.Raster(_GDBPATH + '\\VenueCnt3x3FMMExtent')
    np_fmm_venue_focal = arcpy.RasterToNumPyArray(fmm_venue_focal, nodata_to_value=numpy.nan)

    assert isinstance(np_fmm_venue_focal, numpy.ndarray)
    np_fmm_venue_focal.dump(_OUTPUT_PATH + '\\np_fmm_venue_focal.np')
    print 'Dumped VenueCnt3x3FMMExtent'

    #PAM
    #118x77
    pam_dayspakm = arcpy.Raster(_GDBPATH + '\\PAM_dayspakmClip')
    np_pam_dayspakm = arcpy.RasterToNumPyArray(pam_dayspakm, nodata_to_value=numpy.nan)
    assert isinstance(np_pam_dayspakm, numpy.ndarray)
    np_pam_dayspakm.dump(_OUTPUT_PATH + '\\' + 'np_pam_dayspakm.np')
    print 'Dumped PAM_dayspakm'

    #118x77
    pam_venue_focal = arcpy.Raster(_GDBPATH + '\\VenueCnt3x3PAMExtentClip')
    np_pam_venue_focal = arcpy.RasterToNumPyArray(pam_venue_focal, nodata_to_value=numpy.nan)
    assert isinstance(np_pam_venue_focal, numpy.ndarray)
    np_pam_venue_focal.dump(_OUTPUT_PATH + '\\' + 'np_pam_venue_focal.np')
    print 'Dumped VenueCnt3x3PAMExtentClip'
    print 'Finished'

def dump_pam_fix():
    '''dump pam venue count data with pam venuecount contributions deleted
    in preparation for a manual review/fix
    '''
    pam_fix = arcpy.Raster(_GDBPATH + '\\PAMFix')
    pamarr = arcpy.RasterToNumPyArray(pam_fix, nodata_to_value=numpy.nan)
    assert isinstance(pamarr, numpy.ndarray)
    pamarr.dump(_OUTPUT_PATH + '\\' + 'PAMFix.np')
    print 'Dumped'

#dump_msp_paper_arrays()
print 'Dumping ................'
dump_pam_fix()