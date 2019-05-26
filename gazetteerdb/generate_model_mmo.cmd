C:\Python354x64\Scripts\sqlacodegen --outfile c:/development/python/gazetteerdb/model_gazetteer_sqlacodegen.py mssql+pyodbc://sa:GGM290471@toshiba/gazetteer_no_geom?driver=SQL+Server+Native+Client+11.0
pause

REM For this to work, we have to exclude tables with spatial data types
REM After importing using ogr2ogr command line, we can handball seperate
REM geom data types from the main data in the table using the SQL Template in Spatial\SQLAlchemyWGS84PolygonFix
REM ****But**** the spatial index must first be scripted, and then applied to new table
REM After that do:
REM 1) Script entire DB
REM 2) Create new db
REM 3) Execute script against new db
REM 4) Manually delete geom containing table
REM 5) Run this script aganst the new db





