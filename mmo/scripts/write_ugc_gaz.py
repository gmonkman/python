# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''
make dictionary arrays of place names
with wordcounts
'''
import argparse

from sqlalchemy.orm import load_only
import mmodb
from mmodb.model import UgcGaz, Ugc

import funclib.iolib as iolib
from funclib.iolib import PrintProgress

import nlp.baselib as nlpbase
import mmo.name_entities as NE

import mmo.settings as settings

#region setup log
from pysimplelog import Logger
from funclib.iolib import files_delete2

files_delete2(settings.PATHS.LOG_WRITE_UGC_GAZ)
Log = Logger(name='train', logToStdout=False, logToFile=True, logFileMaxSize=1)
Log.set_log_file(settings.PATHS.LOG_WRITE_UGC_GAZ)
print('\nLogging to %s\n' % settings.PATHS.LOG_WRITE_UGC_GAZ)

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
GAZ = iolib.unpickle(settings.PATHS.GAZ_WORDS_BY_WORD_COUNT)
assert isinstance(GAZ, dict), 'Expected dict for GAZ. Use make_gaz_wordcounts.py if %s does not exists.' % settings.PATHS.GAZ_WORDS_BY_WORD_COUNT




def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__) #use the module __doc__
    f = lambda s: [str(item) for item in s.split(',')]
    cmdline.add_argument('-s', '--slice', help='Record slice, eg -s 0,1000', type=f)
    args = cmdline.parse_args()

    OFFSET = int(args.slice[0])
    max_row = args.slice[1]
    if max_row in ('max', 'end', 'last'):
        max_row = mmodb.SESSION.query(Ugc).count()
    else:
        max_row = int(max_row)

    
    row_cnt = mmodb.SESSION.query(Ugc).order_by(Ugc.ugcid).slice(OFFSET, max_row).count()
    PP = PrintProgress(row_cnt, bar_length=20)

    WINDOW_SIZE = 10; WINDOW_IDX = 0

    while True:
        start, stop = WINDOW_SIZE * WINDOW_IDX + OFFSET, WINDOW_SIZE * (WINDOW_IDX + 1) + OFFSET
        
        #remember, filters don't work with slice if we are updating the records we filter on
        rows = mmodb.SESSION.query(Ugc).options(load_only('ugcid', 'board', 'txt_cleaned', 'processed_gaz', 'title_cleaned')).order_by(Ugc.ugcid).slice(start, stop).all()
        for row in rows:
            try:
                if row.processed_gaz:
                    PP.increment(show_time_left=True)
                    return
                txt = ' '.join([row.title_cleaned, row.txt_cleaned])
                SW = nlpbase.SlidingWindow(txt, tuple(i for i in range(1, MAX_WORDS+1)))
                win = SW.get()


#GAZ will look like:
#   {'cornwall':                A DICT
#       {1:                     A DICT
#           {'a', 'b' ..}       A SET
#   }, ...
                for num_key, ugc_words in win.items():
                    assert isinstance(ugc_words, set)
                    for ifcaid in NE.FORUM_IFCA[row.board]:
                        wds = GAZ.get(ifcaid, {}).get(num_key)
                        if not wds:
                            log('Failed to get places for ifca "%s", num_key "%s"', (ifcaid, num_key), 'both')
                            PP.increment()
                            continue

                        words = ugc_words.intersection(wds)
                        if words:
                            gazs = []
                            for word in words:
                                gazs.append(UgcGaz(ugcid=row.ugcid, name=word, ifcaid=ifcaid))
                row.processed_gaz = True
                mmodb.SESSION.commit()       
            except Exception as e:
                try:
                    log('Error in loop:\t%s' % e, 'both')
                    mmodb.SESSION.rollback()
                except Exception as _:
                    pass
            finally:
                PP.increment(show_time_left=True)


        if len(rows) < WINDOW_SIZE:
            break
        WINDOW_IDX += 1







if __name__ == "__main__":
    main()

              