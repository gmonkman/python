import arcpy

sr = arcpy.SpatialReference(4326)

fname = "C:\\Users\\Team\\Documents\\Theo Laptop Folder\\Tasks\\Quick tasks\\WKTtest\\WKT_to_QGISmakealayerCSV2.csv"

field1 = "WKT"
# the field holding the unique ID...
field2 = "id"

# set up the empty list...
featureList = []


cursor = arcpy.SearchCursor(fname)
row = cursor.next()
while row:
    print (row.getValue(field2))
   
    WKT = row.getValue(field1)
    # this is the part that converts the WKT string to geometry using the defined spatial reference...
    temp = arcpy.FromWKT(WKT, sr)
    # append the current geometry to the list...
    featureList.append(temp)

    row = cursor.next()
   
# copy all geometries in the list to a feature class...
arcpy.CopyFeatures_management(featureList, "C:\\Users\\Team\\Documents\\Theo Laptop Folder\\Tasks\\Quick tasks\\WKTtest\\WKTShapes.shp")   

# clean up...
del row, temp, WKT, File, field1, featureList, cursor

