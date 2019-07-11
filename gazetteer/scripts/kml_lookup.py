# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, too-many-nested-blocks
'''Import a KML file into the gazetteer.

DOESNT CURRENTLY IMPORT, OPENS AN EXCEL SPREADSHEET WITH A LOOKUP ON THE DATA

Example:
kml_lookup.py "C:/temp.kml"
'''
import argparse
import os.path as path


from fastkml import kml
import xlwings

import gazetteerdb
from gazetteerdb.model import Gazetteer
from gazetteer import gazlib

import nlp.clean as clean
import funclib.iolib as iolib
from funclib.iolib import PrintProgressFlash



from funclib.numericslib import round_normal

ALLOWED_FOLDERS = ['charter_mmo']

EXCLUDE = ['The Point', 'Main Road', 'Embankement', 'Pier', 'Quay']
EXCLUDE = [s.lower() for s in EXCLUDE]

def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__) #use the module __doc__
    cmdline.add_argument('kml', help='Path to the kml file')
    cmdline.add_argument('-a', '--add', action='store_true', help="Add points if they don't exist by name")    
    args = cmdline.parse_args()

    with open(path.normpath(args.kml), 'rt', encoding='utf-8') as kml_file:
        doc = kml_file.read()
    k = kml.KML()
    k.from_string(bytes(doc, 'utf-8'))
    out = [['fld', 'name', 'x', 'y', 'desc', 'lookup']]

    doc = list(k.features())[0]
    Flash = PrintProgressFlash(msg='working on it...')
    added = 0
    for doc in k.features():
        for fld in doc.features():
            if not fld.name in ALLOWED_FOLDERS:
                continue
            for i, geom in enumerate(fld.features()):
                i += 1
                Flash.update()
                if geom.geometry.geom_type != 'Point' or geom.name in EXCLUDE:
                    continue
                if args.add:
                    r = gazetteerdb.SESSION.query(Gazetteer).filter_by(name=geom.name).first()
                    if not r:
                        G = Gazetteer()
                        G.x = geom.geometry.x
                        G.y = geom.geometry.y
                        G.name = geom.name
                        G.name_cleaned = clean.clean(geom.name)
                        G.source = iolib.get_file_parts2(args.kml)[1]
                        G.x_rnd = round_normal(geom.geometry.x, 1)
                        G.y_rnd = round_normal(geom.geometry.y, 1)
                        G.shape = 'Point'
                        G.feature_class = ''
                        G.feature_class1 = ''
                        G.id = i
                        try:
                            gazetteerdb.SESSION.add(G)
                            gazetteerdb.SESSION.commit()
                            added += 1
                        except Exception as e:
                            try:
                                print(e)
                                gazetteerdb.SESSION.rollback()
                            except:
                                pass

                s = '"' +  gazlib.lookup(geom.name, include_any_ifca=True, as_str=True) + '"'
                out.append([fld.name, geom.name, geom.geometry.x, geom.geometry.y, geom.description, s])
    if out:
        xlwings.view(out)

    if args.add:
        print('Finished. Added %s locations' % added)
    else:
        print('Finished')



if __name__ == "__main__":
    main()
            