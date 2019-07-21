# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''clean the ugc text field and write to txt_cleaned'''
from sqlalchemy.orm import load_only
from sqlalchemy.sql import text
from mmodb.model import Cb
from gazetteer import name_entities as gaz_ne
import nlp.clean as clean
from funclib.iolib import PrintProgress

import pandas as pd
import mmodb
import mmo.settings as settings


#see cb_imputation.ipynb for the imputation ratios



def main():
    '''main'''    
    
    last = ''
    alloc20 = 1
    alloc60 = 3

    sql = "update cb set passengers_imputed=passengers, distance_imputed=distance"
    mmodb.SESSION.execute(sql)
    mmodb.SESSION.commit()

    row_cnt = mmodb.SESSION.query(Cb).filter(Cb.distance_imputed == None).count()
    PP = PrintProgress(row_cnt, bar_length=20)


    rows = mmodb.SESSION.query(Cb).filter(Cb.distance_imputed == None).order_by(Cb.harbour).all()
    for row in rows:
        #do work
        assert isinstance(row, Cb)
        try:
            if last != '' and row.harbour != last or (alloc20 == 0 and alloc60 == 0):
                alloc20 = 1
                alloc60 = 3

            if alloc60 > 0:
                row.distance_imputed = 60
                alloc60 -= 1
            elif alloc20 > 0:
                row.distance_imputed = 20
                alloc20 -= 1
            mmodb.SESSION.flush()
            mmodb.SESSION.commit()
        except Exception as e:
            try:
                print(e)
                mmodb.SESSION.rollback()
            except:
                pass
        finally:
            last = row.harbour
            PP.increment(show_time_left=True)
          
              
    alloc12 = 3
    alloc10 = 1
    alloc6 = 1

    row_cnt = mmodb.SESSION.query(Cb).filter(Cb.passengers_imputed == None).count()
    PP = PrintProgress(row_cnt, bar_length=20)


    rows = mmodb.SESSION.query(Cb).filter(Cb.passengers_imputed == None).order_by(Cb.harbour).all()
    for row in rows:
        #do work
        assert isinstance(row, Cb)
        try:
            if last != '' and row.harbour != last or (alloc12 == 0 and alloc10 == 0 and alloc6 == 0):
                alloc12 = 3
                alloc10 = 1
                alloc6 = 1

            if alloc12 > 0:
                row.passengers_imputed = 12
                alloc12 -= 1
            elif alloc10 > 0:
                row.passengers_imputed = 10
                alloc10 -= 1
            elif alloc6 > 0:
                row.passengers_imputed = 6
                alloc6 -= 1
            mmodb.SESSION.flush()
            mmodb.SESSION.commit()
        except Exception as e:
            try:
                print(e)
                mmodb.SESSION.rollback()
            except:
                pass
        finally:
            last = row.harbour
            PP.increment(show_time_left=True)




if __name__ == "__main__":
    main()
            