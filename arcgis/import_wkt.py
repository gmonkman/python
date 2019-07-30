import arcpy

sr = arcpy.SpatialReference(4326)

fname = "C:/temp/facilities.txt"

fields = ("facilitiesid","name","wkt",
        "boatnr","capacity","facility_type",
        "ifca","mpa","x",
        "y","sail","commercial",
        "other","fish","prop",
        "mean_prop","mean_est")


featureList = []


cursor = arcpy.SearchCursor(fname)
row = cursor.next()
while row:
    print (row.getValue(fields[1]))

    WKT = row.getValue(fields[2])
    # this is the part that converts the WKT string to geometry using the defined spatial reference...
    geog = arcpy.FromWKT(WKT, sr)
    # append the current geometry to the list...
    featureList.append(geog)

    row = cursor.next()
   
# copy all geometries in the list to a feature class...
arcpy.CopyFeatures_management(featureList,
    "C:/temp/facilities.shp")   


# clean up...
#del row, geog, WKT, File, field1, featureList, cursor

