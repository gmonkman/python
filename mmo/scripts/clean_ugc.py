# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''clean the ugc text field and write to txt_cleaned'''
import argparse
import ast
from sqlalchemy.orm import load_only
from sqlalchemy.sql import text as _text

import mmodb
from mmodb.model import Ugc

import nlp.stopwords as stopwords
import nlp.clean as clean
from funclib.iolib import PrintProgress
import mmo.name_entities as NE
#from warnings import warn
import mmo.settings as settings

#region setup log
from pysimplelog import Logger
from funclib.iolib import files_delete2

files_delete2(settings.PATHS.LOG_CLEAN_UGC)
Log = Logger(name='train', logToStdout=False, logToFile=True, logFileMaxSize=1)
Log.set_log_file(settings.PATHS.LOG_CLEAN_UGC)
print('\nLogging to %s\n' % settings.PATHS.LOG_CLEAN_UGC)


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


class Platforms():
    charter = 'charter'
    private = 'private'
    shore = 'shore'
    kayak = 'kayak'




def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__) #use the module __doc__
    f = lambda s: [str(item) for item in s.split(',')]
    cmdline.add_argument('-s', '--slice', help='Record slice, eg -s 0,1000', type=f)
    cmdline.add_argument('-p', '--platforms', help='Platforms to consider, this is a comma seperated list in [all,charter,private,kayak,shore]. It looks up on ugc.source_platform', type=f)
    args = cmdline.parse_args()

    OFFSET = int(args.slice[0])
    max_row = args.slice[1]


    if max_row in ('max', 'end', 'last'):
        max_row = mmodb.SESSION.query(Ugc.ugcid).count()
    else:
        max_row = int(max_row)
   
    row_cnt = mmodb.SESSION.query(Ugc).options(load_only('ugcid')).order_by(Ugc.ugcid).slice(OFFSET, max_row).count()
    PP = PrintProgress(row_cnt, bar_length=20)

    Stop = stopwords.StopWords(whitelist=NE.all_single)

    WINDOW_SIZE = 5; WINDOW_IDX = 0
    if WINDOW_SIZE > row_cnt: WINDOW_SIZE = row_cnt
    #region Ug
    while True:
        start, stop = WINDOW_SIZE * WINDOW_IDX + OFFSET, WINDOW_SIZE * (WINDOW_IDX + 1) + OFFSET
        #rows = mmodb.SESSION.query(Ugc).options(load_only('ugcid', 'title', 'txt', 'txt_cleaned', 'title_cleaned')).filter_by(txt_cleaned='').order_by(Ugc.ugcid).slice(start, stop).all()
        row_cnt = mmodb.SESSION.query(Ugc).options(load_only('ugcid', 'title', 'txt', 'txt_cleaned', 'title_cleaned', 'source_platform')).order_by(Ugc.ugcid).slice(start, stop).all()
        for row in row_cnt:
            try:
                s = '%s\n%s' % (row.title, row.txt)
                if row.txt_cleaned: continue
                if row.source_platform and args.platforms:
                    sp = set(ast.literal_eval(row.source_platform))
                    if not sp.intersection(set(args.platforms)): continue
                

                if row.title:
                    s = row.title
                    try:
                        s = clean.clean(s, tolower=True)
                        s = Stop.purge(s)
                    except:
                        if not s: s = row.title
                    row.title_cleaned = s

                if row.txt:
                    s = row.txt
                    try:
                        s = clean.clean(s, tolower=True)
                        s = Stop.purge(s)
                    except:
                        if not s: s = row.txt
                    row.txt_cleaned = s
            except:
                try:
                    s = 'Rolling back because of error:\t%s' % e
                    log(s, 'both')
                    mmodb.SESSION.rollback()
                except:
                    pass
            else:
                mmodb.SESSION.flush() #commit everytime, sod it
            finally:
                PP.increment(show_time_left=True)

        try:
            mmodb.SESSION.commit()
        except:
            try:
                mmodb.SESSION.rollback()
            except:
                pass

        if len(row_cnt) < WINDOW_SIZE or PP.iteration >= PP.max: break
        WINDOW_IDX += 1

    #endregion
    



if __name__ == "__main__":
    main()
            