# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''clean the ugc text field and write to txt_cleaned'''
import argparse
from sqlalchemy.orm import load_only

import gazetteerdb
from gazetteerdb.model import GazetteerAfloat
import nlp.clean as clean
from funclib.iolib import PrintProgress
#from warnings import warn
import mmo.settings as settings

#region setup log
from pysimplelog import Logger
from funclib.iolib import files_delete2

files_delete2(settings.PathsUGCGazAfloat.LOG_CLEAN_GAZ)
Log = Logger(name='train', logToStdout=False, logToFile=True, logFileMaxSize=1)
Log.set_log_file(settings.PathsUGCGazAfloat.LOG_CLEAN_GAZ)
print('\nLogging to %s\n' % settings.PathsUGCGazAfloat.LOG_CLEAN_GAZ)


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
        max_row = gazetteerdb.SESSION.query(GazetteerAfloat.gazetteer_afloatid).count()
    else:
        max_row = int(max_row)
    
    row_cnt = gazetteerdb.SESSION.query(GazetteerAfloat.gazetteer_afloatid).order_by(GazetteerAfloat.gazetteer_afloatid).slice(OFFSET, max_row).count()

    PP = PrintProgress(row_cnt, bar_length=20)

    WINDOW_SIZE = 100; WINDOW_IDX = 0
    if WINDOW_SIZE > row_cnt: WINDOW_SIZE = row_cnt
    while True:
        start, stop = WINDOW_SIZE * WINDOW_IDX + OFFSET, WINDOW_SIZE * (WINDOW_IDX + 1) + OFFSET
        #rows = gazetteerdb.SESSION.query(Gazetteer).options(load_only('gazetteer_afloatid', 'name', 'name_cleaned')).filter_by(name_cleaned='').order_by(Gazetteer.gazetteer_afloatid).slice(start, stop).all()
        rows = gazetteerdb.SESSION.query(GazetteerAfloat).options(load_only('gazetteer_afloatid', 'name', 'name_cleaned')).order_by(GazetteerAfloat.gazetteer_afloatid).slice(start, stop).all()
        for row in rows:
            #do work
            try:
                if row.name_cleaned: continue
                s = clean.clean(row.name, tolower=True, skip_txt2nr=True)
                row.name_cleaned = s
                row.processed = True
            except Exception as e:
                try:
                    log(e, 'both')
                    if not s:
                        row.name_cleaned = row.name
                    else:
                        row.name_cleaned = s
                except:
                    pass
            finally:
                PP.increment(show_time_left=True)
            

            
        try:
            gazetteerdb.SESSION.commit() #commit every time
        except:
            try:
                gazetteerdb.SESSION.rollback()
            except:
                pass

        if len(rows) < WINDOW_SIZE or PP.iteration >= row_cnt:
            break

        WINDOW_IDX += 1



if __name__ == "__main__":
    main()
            