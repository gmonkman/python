'''run tests'''
import numpy
import arcpy


def dump_msp_paper_arrays():
    '''test the fmm focal data
    '''
    gdbpath = 'C:\\Users\\Graham Monkman\\OneDrive\\Documents\\PHD\\My Papers\\WalesRSA-MSP\\GIS\\RSA-MSP-SCRATCH.gdb'
    output_path = 'C:\\Users\\Graham Monkman\\OneDrive\\Documents\\PHD\\My Papers\\WalesRSA-MSP\\data\\focalcorr'

    #FMM
    fmm_value = arcpy.Raster(gdbpath + '\\FMMValuetoRaster')
    np_fmm_value = arcpy.RasterToNumPyArray(fmm_value, nodata_to_value=numpy.nan)
    assert isinstance(np_fmm_value, numpy.ndarray)
    np_fmm_value.dump(output_path + '\\np_fmm_value.np')
    print 'Dumped FMMValuetoRaster'

    fmm_venue_focal = arcpy.Raster(gdbpath + '\\VenueCnt3x3FMMExtent')
    np_fmm_venue_focal = arcpy.RasterToNumPyArray(fmm_venue_focal, nodata_to_value=numpy.nan)

    assert isinstance(np_fmm_venue_focal, numpy.ndarray)
    np_fmm_venue_focal.dump(output_path + '\\np_fmm_venue_focal.np')
    print 'Dumped VenueCnt3x3FMMExtent'

    #PAM
    #118x77
    pam_dayspakm = arcpy.Raster(gdbpath + '\\PAM_dayspakmClip')
    np_pam_dayspakm = arcpy.RasterToNumPyArray(pam_dayspakm, nodata_to_value=numpy.nan)
    assert isinstance(np_pam_dayspakm, numpy.ndarray)
    np_pam_dayspakm.dump(output_path + '\\' + 'np_pam_dayspakm.np')
    print 'Dumped PAM_dayspakm'

    #118x77
    pam_venue_focal = arcpy.Raster(gdbpath + '\\VenueCnt3x3PAMExtentClip')
    np_pam_venue_focal = arcpy.RasterToNumPyArray(pam_venue_focal, nodata_to_value=numpy.nan)
    assert isinstance(np_pam_venue_focal, numpy.ndarray)
    np_pam_venue_focal.dump(output_path + '\\' + 'np_pam_venue_focal.np')
    print 'Dumped VenueCnt3x3PAMExtentClip'
    print 'Finished'

dump_msp_paper_arrays()
