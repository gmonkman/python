# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''Import a KML file into the gazetteer.

DOESNT CURRENTLY IMPORT, OPENS AN EXCEL SPREADSHEET WITH A LOOKUP ON THE DATA

Example:
kml_lookup.py "C:/temp.kml"
'''
import argparse
import os.path as path
from sqlalchemy.orm import load_only

from fastkml import kml
import xlwings

import gazetteerdb
from gazetteerdb.model import Gazetteer
from gazetteer import gazlib

import nlp.clean as clean
import funclib.iolib as iolib
from funclib.iolib import PrintProgressFlash
#from warnings import warn
import mmo.settings as settings

ALLOWED_FOLDERS = ['Angling Marks']

EXCLUDE = ['The Point', 'Main Road', 'Embankement', 'Pier', 'Quay']
EXCLUDE = [s.lower() for s in EXCLUDE]

def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__) #use the module __doc__
    cmdline.add_argument('kml', help='Path to the kml file')
    #cmdline.add_argument('-s', '--source', help='Source name', required=True)
    
    args = cmdline.parse_args()

    with open(path.normpath(args.kml), 'rt', encoding='utf-8') as kml_file:
        doc = kml_file.read()
    k = kml.KML()
    k.from_string(bytes(doc, 'utf-8'))
    out = [['fld', 'name', 'x', 'y', 'desc', 'lookup']]

    doc = list(k.features())[0]
    Flash = PrintProgressFlash(msg='working on it...')

    for doc in k.features():
        for fld in doc.features():
            if not fld.name in ALLOWED_FOLDERS:
                continue
            for geom in fld.features():
                Flash.update()
                if geom.geometry.geom_type != 'Point' or geom.name in EXCLUDE:
                    continue
                s = '"' +  gazlib.lookup(geom.name, include_any_ifca=True, as_str=True) + '"'
                out.append([fld.name, geom.name, geom.geometry.x, geom.geometry.y, geom.description, s])
    if out:
        xlwings.view(out)





if __name__ == "__main__":
    main()
            