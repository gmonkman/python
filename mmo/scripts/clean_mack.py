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


mackerel = ['mackeerel', 'makey', 'mackkrel', 'mackkeral', 'macrel', 'makeral', 'maackie',
                'maccarel', 'macarrel', 'mackrell', 'makey', 'mackrrell', 'makerell', 'mackerall', 'maceral', 'maacky',
                'makerrel', 'maackerel', 'maackrel', 'mackie', 'mackks', 'mackiee', 'macarell', 'macckerel', 'mackerell',
                'mackkerel', 'mackky', 'mackerral', 'makrell', 'maackrell',
                'mackerrel', 'maackey', 'mack', 'makerel', 'mackeraal', 'maakerel', 'makrel', 'maccky',
                'macckrel', 'mackey', 'macki', 'macckey', 'macck', 'makeal', 'mackkie',
                'makie', 'mackrrel', 'makereel', 'mackrl', 'mackyy', 'mackrel', 'mackeral',
                'maackeral', 'mackkey', 'macareel', 'maerel', 'macerel', 'makeels', 'mackreel',
                'mackral', 'mackreell', 'maack', 'mackerel', 'macky', 'mackrll', 'mackereel',
                'mackkrell', 'makeraal', 'mackeeral', 'makkerel', 'makerral']

herring = ['herring', 'herringg', 'herring', 'herringss', 'herriings', 'herringgs', 'herrring',
           'herings', 'herrng', 'herrigs', 'heerring', 'herrig', 'heerrings', 'herriing',
           'hering', 'herrrings', 'herrinng', 'herrings', 'herrin', 'herrngs', 'herrins', 'herrinngs']


haddock = ['haddock', 'pingers', 'haddes', 'hadocks', 'haddies', 'hadock', 'haddcks',
           'haddoks', 'haddoock', 'haddiess', 'haddocs', 'haddoccks', 'haddocks', 'hadddock',
           'haddie', 'haddocck', 'haaddies', 'haddiees', 'haddiies', 'haddockss', 'haddck',
           'haddoocks', 'hadies', 'pinger', 'hadddocks', 'haddyy', 'haddock', 'haaddy', 'haaddocks',
           'hadddy', 'haddockk', 'haaddock', 'haddok', 'hadddies', 'haddy', 'haddockks', 'haddis', 'haddoc']


def main():
    '''main'''   
    row_cnt = mmodb.SESSION.query(UgcHint).filter_by(hint='mackerel').options(load_only('ugcid')).count()
    PP = PrintProgress(row_cnt, bar_length=20, init_msg='Mackerel')

    #rows = mmodb.SESSION.query(Ugc).options(load_only('ugcid', 'title', 'txt', 'txt_cleaned', 'title_cleaned')).filter_by(txt_cleaned='').order_by(Ugc.ugcid).slice(start, stop).all()
    rows = mmodb.SESSION.query(UgcHint).filter_by(hint='mackerel').order_by(UgcHint.ugcid).all()
    for row in rows:
        assert isinstance(row, UgcHint)
        try:
            if not row.pos_list: continue
            inds = list(ast.literal_eval(row.pos_list))
            if not inds: continue
            is_bait = []
            for i in inds:
                sql = "select substring(txt_cleaned, %s - 15, 25 + 35) from ugc where ugcid=%s" % (i, row.ugcid) #i.e. 25 chars to left of mackerel, and 30 chars to right m of mackerel
                ugc_row = mmodb.ENGINE.execute(_text(sql)).first()
                if not ugc_row: continue
                txt = ugc_row[0]
                
                if relib.SentenceHasTextMulti(txt, NE.MackerelAsBait.allwords):
                    is_bait.append([True])
                elif relib.SentenceHasTextMulti(txt, NE.BaitSpecies.allwords):
                    is_bait += [True]
                else:
                    is_bait += [False]

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


    row_cnt = mmodb.SESSION.query(UgcHint).filter_by(hint='herring').options(load_only('ugcid')).count()
    PP = PrintProgress(row_cnt, bar_length=20, init_msg='Herring')
    rows = mmodb.SESSION.query(UgcHint).filter_by(hint='herring').order_by(UgcHint.ugcid).all()
    for row in rows:
        assert isinstance(row, UgcHint)
        try:
            if not row.pos_list: continue
            inds = list(ast.literal_eval(row.pos_list))
            if not inds: continue
            is_bait = []
            for i in inds:
                sql = "select substring(txt_cleaned, %s - 15, 25 + 35) from ugc where ugcid=%s" % (i, row.ugcid) #i.e. 25 chars to left of mackerel, and 30 chars to right m of mackerel
                ugc_row = mmodb.ENGINE.execute(_text(sql)).first()
                if not ugc_row: continue
                txt = ugc_row[0]
                
                if relib.SentenceHasTextMulti(txt, NE.HerringAsBait.allwords):
                    is_bait.append([True])
                elif relib.SentenceHasTextMulti(txt, NE.BaitSpecies.allwords):
                    is_bait += [True]
                else:
                    is_bait += [False]

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


    row_cnt = mmodb.SESSION.query(UgcHint).filter_by(hint='haddock').options(load_only('ugcid')).count()
    PP = PrintProgress(row_cnt, bar_length=20, init_msg='Haddock')
    rows = mmodb.SESSION.query(UgcHint).filter_by(hint='haddock').order_by(UgcHint.ugcid).all()
    for row in rows:
        assert isinstance(row, UgcHint)
        try:
            if not row.pos_list: continue
            inds = list(ast.literal_eval(row.pos_list))
            if not inds: continue
            is_bait = []
            for i in inds:
                sql = "select substring(txt_cleaned, %s - 15, 25 + 35) from ugc where ugcid=%s" % (i, row.ugcid) #i.e. 25 chars to left of mackerel, and 30 chars to right m of mackerel
                ugc_row = mmodb.ENGINE.execute(_text(sql)).first()
                if not ugc_row: continue
                txt = ugc_row[0]
                
                if relib.SentenceHasTextMulti(txt, NE.HaddockAsException.allwords):
                    is_bait.append([True])
                else:
                    is_bait += [False]

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
            