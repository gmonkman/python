# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''create additional gazetteer records base on common substitutions
Substitutions are read from mmo.named_entities.py
'''
from sqlalchemy import text

import gazetteerdb
import gazetteer.gazlib as _gazlib

from funclib.iolib import PrintProgress

from mmo.name_entities import Substitutions




def main():
    '''main'''
    l = list([getattr(Substitutions, attr) for attr in dir(Substitutions) if not callable(getattr(Substitutions, attr)) and not attr.startswith("__")])
    PP = PrintProgress(len(l))
    for words in list([getattr(Substitutions, attr) for attr in dir(Substitutions) if not callable(getattr(Substitutions, attr)) and not attr.startswith("__")]):
        run_job(words)
        PP.increment()
    print('done')







def run_job(words):
    '''run job'''
    for match, replace in [(x, y) for x in words for y in words]:
        if match == replace: continue
        sql = "select name, x, y from gazetteer where name_cleaned like '% " +  match + "'"
        rows = gazetteerdb.SESSION.execute(text(sql)).fetchall()
        PP1 = PrintProgress(len(rows), bar_length=15)
        for row in rows:
            s = row[0][:-len(match)] + replace
            _gazlib.add('substitutions', s, row[1], row[2], unique_only=True)
            PP1.increment()



if __name__ == "__main__":
    main()
            