# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument

'''clean the ugc text field and write to txt_cleaned'''
from sqlalchemy.sql import text as _text

import mmodb
import mmodb.model as mmomodel
from mmodb.model import Ugc

import gazetteerdb
import gazetteerdb.model as gazmodel

import nlp.stopwords as stopwords
import nlp.clean as clean
from funclib.iolib import PrintProgress
import mmo.name_entities as NE


#region start with ugc
sql = "SELECT ugcid, txt, txt_cleaned FROM ugc"
rows = mmodb.SESSION.query(Ugc).options(load_only('ugcid', 'title', 'txt', 'txt_cleaned')).filter_by(txt_processed='').all()
_PP = PrintProgress(len(rows), init_msg='Cleaning ugc text')

Stop = stopwords.StopWords(whitelist=NE.all_single)
Stop.purge_iter
for i, row in enumerate(rows):
    s = clean.clean(row('txt'), tolower=True)
    s = Stop.purge(s)
    row['txt_cleaned'] = s
    if i % 100 == 0 and i > 0:
        mmodb.SESSION.commit()
    _PP.increment(show_time_left=True) 
#endregion



#region GAZE
rows = mmodb.SESSION.query(Ugc).options(load_only('gazetteerid', 'name', 'name_cleaned')).filter_by(name_cleaned='').all()
_PP = PrintProgress(len(rows), init_msg='Cleaning gazetteer')

whitelist = NE.whitelist()
Stop = stopwords.StopWords(whitelist=whitelist)

for i, row in enumerate(rows):
    s = clean.clean(row('name_cleaned'), tolower=True)
    #s = Stop.purge(s)
    row['name_cleaned'] = s
    if i % 100 == 0 and i > 0:
        mmodb.SESSION.commit()
    _PP.increment(show_time_left=True) 
#endregion
