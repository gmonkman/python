import arcpy
fc=r'C:\GISDATA\ztemp\4416.shp'
field = 'SHAPE@'


#rows = arcpy.SearchCursor("C:/GISDATA/ztemp/4416.shp")

cursor = arcpy.SearchCursor("C:/GISDATA/ztemp/4416.shp")
for row in cursor:
    print(row['SHAPE@'])



#for r in rows:
 #   array1=r[0].getPart()
  #  for vertice in range(r[1].pointCount):
   #     pnt=array1.getObject(0).getObject(vertice)
    #    print r[0],pnt.X,pnt.Y


