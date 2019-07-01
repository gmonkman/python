# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''flag mackerel species in ugc_hint as is_bait'''
import ast
from sqlalchemy.orm import load_only
from sqlalchemy.sql import text as _text

import mmodb
from mmodb.model import Ugc, UgcHint
import nlp.relib as relib

from funclib.iolib import PrintProgress
import mmo.name_entities as NE
#from warnings import warn
import mmo.settings as settings




def main():
    '''main'''   
    row_cnt = mmodb.SESSION.query(UgcHint).filter_by(hint='mackerel').options(load_only('ugcid')).count()
    PP = PrintProgress(row_cnt, bar_length=20)

    #rows = mmodb.SESSION.query(Ugc).options(load_only('ugcid', 'title', 'txt', 'txt_cleaned', 'title_cleaned')).filter_by(txt_cleaned='').order_by(Ugc.ugcid).slice(start, stop).all()
    rows = mmodb.SESSION.query(UgcHint).filter_by(hint='mackerel').order_by(Ugc.ugcid).all()
    for row in rows:
        assert isinstance(row, UgcHint)
        try:
            if row.pos_list: continue
            inds = list(ast.literal_eval(row.pos_list))
            if not inds: continue
            is_bait = []
            for i in inds:
                sql = "select substring(txt, %s - 25, 25 + 30) from ugc where ugcid=%s" % (row.ugcid, i) #i.e. 25 chars to left of mackerel, and 30 chars to right m of mackerel
                ugc_row = mmodb.ENGINE.execute(_text(sql)).first()
                if not ugc_rw: continue
                txt = ugc_row[0][0]
                
                if relib.SentenceHasTextMulti(txt, NE.MackerelAsBait.allwords):
                    is_bait.append([True])
                elif relib.SentenceHasTextMulti(txt, NE.BaitSpecies.allwords):
                    is_bait.append([True])
                else:
                    is_bait.append([False])

            row.is_bait = all(is_bait)
        except:
            try:
                s = 'Rolling back because of error:\t%s' % e
                print(s)
                mmodb.SESSION.rollback()
            except:
                pass
        else:
            if PP.iteration % 1000 == 0 and PP.iteration > 0:
                mmodb.SESSION.commit()
        finally:
            PP.increment(show_time_left=True)


#endregion
    



if __name__ == "__main__":
    main()
            