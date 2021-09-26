# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, too-many-nested-blocks
'''Write facilities to SQL
'''
import argparse
import os.path as path

from fastkml import kml
import xlwings

import gazetteerdb
from gazetteerdb.model import Facilities
from gazetteer import gazlib

import funclib.pandaslib as pandaslib
from funclib import xmllib
import funclib.baselib as baselib

import funclib.iolib as iolib
from funclib.iolib import PrintProgress

BAD_FACILITES = {'names':[], 'inds':[]}

from funclib.numericslib import round_normal

#ALLOWED_FOLDERS = ['charter_mmo']
ALLOWED_FOLDERS = []



#EXCLUDE = ['The Point', 'Main Road', 'Embankement', 'Pier', 'Quay']
EXCLUDE = []
EXCLUDE = [s.lower() for s in EXCLUDE]


class Facility():
    facility_type = None
    capacity = None
    boatnr = None



# Example polygon from kml
#<Polygon>
#	<tessellate>1</tessellate>
#	<outerBoundaryIs>
#		<LinearRing>
#			<coordinates>
#				-1.960322205790629,50.70999739568558,0 -1.959442739470479,50.71045367942265,0 -1.958604303567524,50.71090712711025,0 -1.959358345017074,50.71143932632991,0 -1.960042374005195,50.71151182011462,0 -1.961073754786425,50.71144818270756,0 -1.961737120208189,50.71133222049772,0 -1.96217566374988,50.71110286909818,0 -1.960322205790629,50.70999739568558,0 
#			</coordinates>
#		</LinearRing>
#	</outerBoundaryIs>
#</Polygon>

#SET @g = geography::STGeomFromText('LINESTRING(-122.360 47.656, -122.343 47.656)', 4326);
#geography::STGeomFromText('POLYGON((-122.358 47.653 , -122.348 47.649, -122.348 47.658, -122.358 47.658, -122.358 47.653))', 4326))
#https://docs.microsoft.com/en-us/sql/t-sql/spatial-geography/spatial-types-geography?view=sql-server-2017

def main():
    '''main'''
    global BAD_FACILITES
    cmdline = argparse.ArgumentParser(description=__doc__) #use the module __doc__
    cmdline.add_argument('kml', help='Path to the kml file')
    cmdline.add_argument('-d', '--duponly', action='store_true', help="Duplicate check only")    
    args = cmdline.parse_args()

    with open(path.normpath(args.kml), 'rt', encoding='utf-8') as kml_file:
        doc = kml_file.read()
    k = kml.KML()
    k.from_string(bytes(doc, 'utf-8'))

    doc = list(k.features())[0]

    skipped_not_poly = 0
    added = 0
    
    gazetteerdb.SESSION.execute('delete from facilities')
    gazetteerdb.SESSION.commit()

    cnt = 0
    names = []
    for doc in k.features():
        for fld in doc.features():
            if not fld.name in ALLOWED_FOLDERS and ALLOWED_FOLDERS:
                continue
            for i, geom in enumerate(fld.features()):
                names.append(geom.name)
                cnt += 1

    if args.duponly:
        bad = pandaslib.df_from_dict(baselib.list_get_dups(names))
        xlwings.view(bad) 


    PP = PrintProgress(cnt)    

    for doc in k.features():
        for fld in doc.features():
            if not fld.name in ALLOWED_FOLDERS and ALLOWED_FOLDERS:
                continue
            for i, geom in enumerate(fld.features()):
                if geom.geometry.geom_type != 'Polygon' or geom.name in EXCLUDE:
                    skipped_not_poly += 1
                    PP.increment()
                    continue

                Fac = Facilities()
                waserr = False
                try:
                    F = parse_desc(geom.description, geom.name)
                    if F.boatnr in (0, None):
                        raise ValueError('F.boatnr was 0 or None')
                except:
                    waserr = True
                    BAD_FACILITES['names'].append(geom.name)
                    BAD_FACILITES['inds'].append(i)
                finally:
                    PP.increment

                if waserr: continue

                assert isinstance(F, Facility)

                try:
                    if_ = lambda x: int(float(x))
                    Fac.x = geom.geometry.centroid.x
                    Fac.y = geom.geometry.centroid.y
                    Fac.name = geom.name
                    Fac.boatnr = if_(F.boatnr) if F.boatnr else if_(F.capacity)
                    
                    try:
                        Fac.capacity = if_(F.capacity)
                    except:
                        Fac.capacity = None

                    Fac.facility_type = F.facility_type
                    Fac.geogtxt = geom.geometry.to_wkt()
                
                    gazetteerdb.SESSION.add(Fac)
                    gazetteerdb.SESSION.commit()
                    added += 1
                except Exception as e:
                    try:
                        print(e)
                        gazetteerdb.SESSION.rollback()
                        try:
                            BAD_FACILITES['names'].append(geom.name)
                            BAD_FACILITES['inds'].append(i)
                        except:
                            pass
                    except Exception as e:
                        print(e)
                        pass
                finally:
                    PP.increment()



    gazetteerdb.SESSION.execute('update facilities_geog set geog=geog.MakeValid().ReorientObject() WHERE geog.MakeValid().EnvelopeAngle() > 90;')
    gazetteerdb.SESSION.commit()
    print('Added: %s\tSkipped: %s' % (added, PP.max - added))
    bad = pandaslib.df_from_dict(BAD_FACILITES)
    xlwings.view(bad)




def parse_desc(desc, name):
    '''(str) -> list
    parse description
    '''
    
    F = Facility()    

    if '<' in desc:
        asxml = '<root>' + desc + '</root>'
        D = xmllib.XML(asxml).asdict()
        F.facility_type = D['root'].get('type', '')
        if not F.facility_type:
            if 'moor' in name:
                F.facility_type = 'mooring'
            else:
                F.facility_type = 'marina'

        F.boatnr = D['root'].get('boats', 0)
        if F.boatnr == 0: D['root'].get('boat', 0)

        F.capacity = D['root'].get('cap', 0)
        if F.capacity == 0:
            D['root'].get('caps', 0)

    else:
        A = desc.split()
        F.facility_type = A[0].lower()
        F.boatnr = A[1]
        if len(A) == 3: F.capacity = A[2]

    if 'marin' in F.facility_type: F.facility_type = 'marina'
    if 'harb' in F.facility_type: F.facility_type = 'marina'
    if 'moor' in F.facility_type: F.facility_type = 'mooring'
    if 'quay' in F.facility_type: F.facility_type = 'marina'
    if not F.facility_type in ('marina', 'mooring'): F.facility_type = 'marina'
    return F
 



if __name__ == "__main__":
    main()
           