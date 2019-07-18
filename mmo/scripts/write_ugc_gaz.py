# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''
make dictionary arrays of place names
with wordcounts
'''
import argparse
import ast
from sqlalchemy.orm import load_only
from sqlalchemy import text
import mmodb
from mmodb.model import UgcGaz, Ugc
import gazetteerdb
import funclib.iolib as iolib
from funclib.iolib import PrintProgress
from funclib.stringslib import wordcnt
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


class SourceRank():
    '''priority ranking for sources, lower is better'''
    #just got these from "select distinct source from gazetteer_shore.dbo.gazetteer_afloat"
    sources = ['lk', 'ukho_constructs', 'ukho_act_lic', 'os_gazetteer', 'os_open_name', 'ukho_seacover', 'ukho_gazetteer', 'medin', 'geonames', 'geonames_alias', 'geograph', 'charter_mmo.kml', 'substitutions']
    ranks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    assert len(sources) == len(ranks), 'SourceRank sources and ranks must be of equal length'


#D will look like:
#   {'cornwall':                A DICT
#       {1:                     A DICT
#           {'a', 'b' ..}       A SET
#   }, ...
def _addit(d, ifca, name, source, gazid):
    ifca = ifca.lower()
    if not d.get(ifca):
        d[ifca] = {}
    if not d[ifca].get(name):
        d[ifca][name] = {}
    if not d[ifca][name].get(source):
        d[ifca][name][source] = []
    d[ifca][name][source] += [gazid]


GAZ = iolib.unpickle(settings.PATHS.GAZ_WORDS_BY_WORD_COUNT)
assert isinstance(GAZ, dict), 'Expected dict for GAZ. Use make_gaz_wordcounts.py if %s does not exists.' % settings.PATHS.GAZ_WORDS_BY_WORD_COUNT


#GAZIDS_BY_NAME
#   {'mostyn':
#       {'southern':
#           {'os_open_name': [423,876...], .... }
buildit = True
try:
    GAZIDS_BY_NAME = iolib.unpickle(settings.PATHS.GAZETTEERIDS_BY_NAME)
    if GAZIDS_BY_NAME:
        print('Loaded gazetterid-name dict from filesystem')
        buildit = False
except:
    buildit = True

if buildit:
    GAZIDS_BY_NAME = {}
    print('Building gazetterid-name dict....')
    sql = "SELECT ifca, name_cleaned, source, gazetteerid, coast_dist_m, feature_class1 from gazetteer where isnull(name_cleaned, '') <> '' and isnull(ifca, '') <> ''"
    rs = gazetteerdb.SESSION.execute(text(sql)).fetchall()
    PP1 = PrintProgress(len(rs))
    assert rs, 'Building gazetterid-name dict failed - No records returned'
    skipped = 0
    for r in rs:
        PP1.increment()
        if r[4]:
            if r[5] in ['section of named road', 'named road'] and r[4] > 100:
                skipped += 1
                continue

            if r[4] > 1000:
                skipped += 1
                continue
        _addit(GAZIDS_BY_NAME, r[0], r[1], r[2], r[3])
    assert GAZIDS_BY_NAME, 'gazetterid-name dict was empty. Do you need to run clean_gaz.py?'
    iolib.pickle(GAZIDS_BY_NAME, settings.PATHS.GAZETTEERIDS_BY_NAME)
    print('Built and saved gazetterid-name dict. Skipped %s of %s.' % (skipped, len(rs)))



def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__) #use the module __doc__
    f = lambda s: [str(item) for item in s.split(',')]
    cmdline.add_argument('-s', '--slice', help='Record slice, eg -s 0,1000', type=f)
    cmdline.add_argument('-p', '--platforms', help="Process platforms which match this comma seperated list. Platforms for each forum board are in ugc.source_platform. platforms in ['private','shore','charter','kayak','all']", type=f)
    args = cmdline.parse_args()

    OFFSET = int(args.slice[0])
    max_row = args.slice[1]
    if max_row in ('max', 'end', 'last'):
        max_row = mmodb.SESSION.query(Ugc).count()
    else:
        max_row = int(max_row)

    
    row_cnt = mmodb.SESSION.query(Ugc).order_by(Ugc.ugcid).slice(OFFSET, max_row).count()
    PP = PrintProgress(row_cnt, bar_length=20)

    WINDOW_SIZE = 1000; WINDOW_IDX = 0
    if WINDOW_SIZE >= row_cnt: WINDOW_SIZE = row_cnt
    already_processed = 0; added = 0; skipped_platform = 0; skipped_board = 0
    
    VALID_BOARDS = {**NE.FORUM_IFCA_SHORE, **NE.FORUM_IFCA_KAYAK}
    
    while True:
        start, stop = WINDOW_SIZE * WINDOW_IDX + OFFSET, WINDOW_SIZE * (WINDOW_IDX + 1) + OFFSET
        #remember, filters don't work with slice if we are updating the records we filter on
        rows = mmodb.SESSION.query(Ugc).options(load_only('ugcid', 'board', 'txt_cleaned', 'processed_gaz', 'title_cleaned', 'source_platform')).order_by(Ugc.ugcid).slice(start, stop).all()
        for row in rows:
            try:
                if row.processed_gaz and not settings.UgcGazSettings.TEST_MODE:
                    already_processed += 1
                    continue

                if row.source_platform and args.platforms:
                    if not 'all' in args.platforms:
                        sp = set(ast.literal_eval(row.source_platform))
                        if not sp.intersection(set(args.platforms)): 
                            skipped_platform += 1
                            continue
                
                if not row.board in VALID_BOARDS.keys():
                    skipped_board += 1
                    continue

                try:  
                    txt = ' '.join([row.title_cleaned, row.txt_cleaned])
                except:
                    continue
                
                #txt = 'this is a test with st marys bay which should detect the 3 word version only'    
                SW = nlpbase.SlidingWindow(txt, tuple(i for i in range(1, MAX_WORDS+1)))
                win = SW.get()

#GAZ will look like:
#   {'cornwall':                A DICT
#       {1:                     A DICT
#           {'a', 'b' ..}       A SET
#   }, ...      
                
                brd = ''
                if row.board: brd = row.board.lower()
                for ifcaid in NE.FORUM_IFCA[brd]: #loop through each ifca associated with the board given in row.board, i set this up manually
                    all_found_words = {}                       
                    for num_key, ugc_words in sorted(list(win.items()), key=lambda x:x[0], reverse=True):  #loop over word windows in the post in reverse, 4 word matches, then three etc
                        assert isinstance(ugc_words, set)
                        if not ugc_words: continue
                        if not all_found_words.get(num_key): all_found_words[num_key] = [] #create dict item if doesnt exist

                        wds = GAZ.get(ifcaid, {}).get(num_key) #get all the place names <num_key in length, ie 4, 3, 2 1...
                        if not wds:
                            log('Failed to get places for ifca "%s", num_key "%s"' % (ifcaid, num_key), 'both')    
                            continue

                        #we now want to loop through all previously found word windows of greater kernel size
                        #and only add shorter phrases which dont match longer phrases, e.g. dont add Llandudno if we have already added Llandudno Pier
                        new_words = set()
                        for w in ugc_words.intersection(wds):   #test if ugc_words (our source content) matches our gazetteer for a given phrase length
                            addit = True
                            for found_key, found_list in all_found_words.items():   #found_key is the word count, found list is the matched place names of length = found_key
                                if found_key <= num_key: continue #only chek place names with more words
                                if w in found_list:
                                    addit = False
                                    break
                            if addit: new_words |= set([w])

                        all_found_words[num_key] = new_words
  
                    for num_key, words in all_found_words.items():
                        for w in words:
                            for source, gazids in GAZIDS_BY_NAME[ifcaid][w].items():
                                source = source.lower()
                                for gazid in gazids:
                                    if not settings.UgcGazSettings.TEST_MODE:
                                        mmodb.SESSION.add(UgcGaz(ugcid=row.ugcid, name=w, ifcaid=ifcaid, gazetteerid=gazid,
                                                                    gaz_rank=SourceRank.ranks[SourceRank.sources.index(source)],
                                                                    gaz_source=source, word_cnt=wordcnt(w)))
                                    added += 1

                if not settings.UgcGazSettings.TEST_MODE:
                    row.processed_gaz = True
                    mmodb.SESSION.flush()

            except Exception as e:
                try:
                    log('Error in loop:\t%s' % e, 'both')
                except Exception as _:
                    pass
            finally:
                PP.increment()

        try:
            if not settings.UgcGazSettings.TEST_MODE:
                mmodb.SESSION.commit()
            else: #just in case
                try:
                    mmodb.SESSION.rollback()
                except:
                    pass
        except Exception as e:
            try:
                log('Error in loop:\t%s' % e, 'both')
                mmodb.SESSION.rollback()
            except:
                pass


        if len(rows) < WINDOW_SIZE or PP.iteration >= PP.max: break
        WINDOW_IDX += 1

    print('[SKIPPED: %s processed; %s platform; %s board] %s ADDED %s' % (already_processed, skipped_platform, skipped_board, added))





if __name__ == "__main__":
    main()
              