# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''
make dictionary arrays of place names
with wordcounts
'''
import argparse

#from sqlalchemy.sql import text as _text


import gazetteerdb
from gazetteerdb.model import t_v_gazetteer_word_count as T

import funclib.iolib as iolib
from funclib.iolib import PrintProgress

import mmo.settings as settings

#region setup log
from pysimplelog import Logger
from funclib.iolib import files_delete2



files_delete2(settings.PATHS.LOG_MAKE_GAZ_WORDCOUNTS)
Log = Logger(name='train', logToStdout=False, logToFile=True, logFileMaxSize=1)
Log.set_log_file(settings.PATHS.LOG_MAKE_GAZ_WORDCOUNTS)
print('\nLogging to %s\n' % settings.PATHS.LOG_MAKE_GAZ_WORDCOUNTS)

class LogTo():
    '''log options'''
    console = 'console'
    file_ = 'file'
    both = 'both'


def log(msg, output_to='both'):
    '''(argparse.parse, str) -> void
    '''
    try:
        if output_to in ['file', 'both']:
            Log.info(msg)

        if output_to in ['console', 'both']:
            print(msg)
    except Exception as _:
        try:
            print('Log file failed to print.')
        except Exception as _:
            pass
#endregion


MAX_WORDS = 4 #only consider places with 4 or fewer words


VALID_IFCAS = ['cornwall', 'devon and severn', 'eastern', 'isles of scilly', 'kent and essex', 'north east', 'north west', 'northumberland', 'southern', 'sussex']


#D will look like:
#   {'cornwall':                A DICT
#       {1:                     A DICT
#           {'a', 'b' ..}       A SET
#   }, ...
    
     
D = {}
for s in VALID_IFCAS:
    D[s] = {}


def _addit(ifca, k, v):
    '''(dict, int|str|iter, any) -> None

    Byref: add value v to dictionary d with key k
    '''
    if not k or k == 0: return
    global D
    assert ifca in VALID_IFCAS, 'IFCA "%s" not found' % ifca
    if not D[ifca].get(k): D[ifca][k] = set()    
    D[ifca][k] |= set([v])








def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__) #use the module __doc__
    f = lambda s: [str(item) for item in s.split(',')]
    cmdline.add_argument('-s', '--slice', help='Record slice, eg -s 0,1000', type=f)
    args = cmdline.parse_args()

    OFFSET = int(args.slice[0])
    max_row = args.slice[1]
    if max_row in ('max', 'end', 'last'):
        max_row = gazetteerdb.SESSION.query(T).count()
    else:
        max_row = int(max_row)

    
    row_cnt = gazetteerdb.SESSION.query(T).order_by(T.columns.gazetteerid).slice(OFFSET, max_row).count()
    PP = PrintProgress(row_cnt, bar_length=20)

    WINDOW_SIZE = 1000; WINDOW_IDX = 0

    while True:
        start, stop = WINDOW_SIZE * WINDOW_IDX + OFFSET, WINDOW_SIZE * (WINDOW_IDX + 1) + OFFSET
        rows = gazetteerdb.SESSION.query(T).order_by(T.columns.gazetteerid).slice(start, stop).all()
        
        if rows is None: break

        try:
            for row in rows:
                if row.n > MAX_WORDS:
                    print('skipped %s' % row.name_cleaned)
                    continue
                assert row.ifca in VALID_IFCAS, 'IFCA %s not found' % row.ifca
                #do work
                _addit(row.ifca, row.n, row.name_cleaned) 
                PP.increment(show_time_left=True)
        except Exception as e:
            log('Error in loop:\t%s' % e, 'both')

        if len(rows) < WINDOW_SIZE:
            break
        WINDOW_IDX += 1







if __name__ == "__main__":
    main()
    iolib.pickle(D, settings.GAZ_WORDS_BY_WORD_COUNT)
    print('\nDone. Saved to %s' % settings.GAZ_WORDS_BY_WORD_COUNT) 
               