# -*- coding: utf-8 -*-
"""
   This script will convert a raster with floating point values to a polygon
"""
import arcgisscripting
import arcpy
from arcpy.sa import Int
from arcpy.sa import Times
from arcpy import RasterToPolygon_conversion as cvt


gp = arcgisscripting.create(10.0)

    
if __name__ == "__main__":
    input_layer = gp.GetParameterAsText(0)
    output_file = gp.GetParameterAsText(1)
    factor = int(1000 if(gp.GetParameterAsText(2)=='' or gp.GetParameterAsText(2)==0) else gp.GetParameterAsText(2))
    col_name = gp.GetParameterAsText(3)
 
    deleteme = "C:\\Users\\Graham Monkman\\OneDrive\\Documents\\PHD\\My Papers\\WalesRSA-MSP\\GIS\\RSA-MSP-SCRATCH.gdb\\deleteme"

    try:
        tmp = Times(input_layer, factor)
        tmpi = Int(tmp)
        poly = cvt(tmpi, output_file, 'NO_SIMPLIFY', 'VALUE')
        arcpy.AddField_management(poly[0], col_name, "double")

        d = arcpy.Describe(poly[0])
        flds = d.fields
        flds_lcase = [x.name.lower() for x in flds]
        if 'grid_code' in flds_lcase:
            val_col = 'grid_code'
        elif 'gridcode' in flds_lcase:
            val_col = 'gridcode'
        else:
            raise(BaseException('Could not find field grid_code or gridcode in shapefile'))

        sql =  '!%s!/(%s+0.000000001)' % (val_col, factor)
        arcpy.CalculateField_management(poly[0], col_name, sql, 'PYTHON_9.3')
      #  dropfields = ['grid_code']
      #  arcpy.Delete_management(poly[0], dropfields)
    except:
        import traceback
        gp.AddError(traceback.format_exc())

print "FINISHED"