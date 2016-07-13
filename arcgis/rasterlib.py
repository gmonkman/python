#misc arcgis work
import arcpy
import numpy as np

def raster_to_array(gdb_path, raster_name):
    ''' (string, string) -> nparray
    Takes arcmap fully qualified workspace name (gdb) and the name of a raster layer
    Path should not be qualified with \\
    and loads the raster to a numpy array (nparray) object
    NoData is returned as NaN's in the numpy array
    '''
    assert isinstance(gdb_path, str)
    assert isinstance(raster_name, str)

    raster = arcpy.Raster(gdb_path + '\\' + raster_name)
    
    nparr = arcpy.RasterToNumPyArray(raster, nodata_to_value=np.nan)
    assert isinstance(nparr, np.ndarray)