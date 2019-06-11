# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''clean the ugc text field and write to txt_cleaned'''
import argparse
from sqlalchemy.orm import load_only

import gazetteerdb
from gazetteerdb.model import Gazetteer

import nlp.stopwords as stopwords
import nlp.clean as clean
from funclib.iolib import PrintProgress
import mmo.name_entities as NE
from warnings import warn
import mmo.settings as settings

#region setup log
from pysimplelog import Logger
from funclib.iolib import files_delete2

files_delete2(settings.PATHS.LOG_CLEAN_GAZ)
Log = Logger(name='train', logToStdout=False, logToFile=True, logFileMaxSize=1)
Log.set_log_file(settings.PATHS.LOG_CLEAN_GAZ)
print('\nLogging to %s\n' % settings.PATHS.LOG_CLEAN_GAZ)


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




def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__) #use the module __doc__
    f = lambda s: [str(item) for item in s.split(',')]
    cmdline.add_argument('-s', '--slice', help='Record slice, eg -s 0,1000', type=f)
    args = cmdline.parse_args()

    OFFSET = int(args.slice[0])
    max_row = args.slice[1]
    if max_row in ('max', 'end', 'last'):
        max_row = gazetteerdb.SESSION.query(Gazetteer.gazetteerid).count()
    else:
        max_row = int(max_row)

    row_cnt = gazetteerdb.SESSION.query(Gazetteer.gazetteerid).slice(OFFSET, max_row).count()
    PP = PrintProgress(row_cnt, bar_length=20)
 
    Stop = stopwords.StopWords(whitelist=NE.all_single)


    WINDOW_SIZE = 10; WINDOW_IDX = 0


    while True:
        start, stop = WINDOW_SIZE * WINDOW_IDX + OFFSET, WINDOW_SIZE * (WINDOW_IDX + 1) + OFFSET
        rows = gazetteerdb.SESSION.query(Gazetteer).options(load_only('gazetteerid', 'name', 'name_cleaned')).filter_by(name_cleaned='').order_by(Gazetteer.gazetteerid).slice(start, stop).all()
        
        if rows is None: break

        try:
            for row in rows:
                #do work
                s = clean.clean(row.name, tolower=True)
                s = Stop.purge(s)
                row.name_cleaned = s
                row.processed = True
                PP.increment(show_time_left=True)
            gazetteerdb.SESSION.commit()
        except Exception as e:
            s = 'Rolling back because of error:\t%s' % e
            log(s, 'both')
            gazetteerdb.SESSION.rollback()


        if len(rows) < WINDOW_SIZE:
            break
        WINDOW_IDX += 1




if __name__ == "__main__":
    main()
            