'''run some SQLS to fix common text mistakes'''
import argparse
import sqlalchemy
from pysimplelog import Logger
from funclib.iolib import files_delete2
import mmo.settings as settings



files_delete2(settings.PATHS.LOG_WRITE_HINTS)
Log = Logger(name='train', logToStdout=False, logToFile=True, logFileMaxSize=1)
Log.set_log_file(settings.PATHS.LOG_WRITE_HINTS)
print('\nLogging to %s\n' % settings.PATHS.LOG_WRITE_HINTS)



def log(args, msg):
    '''(argparse.parse, str) -> void
    '''
    try:
        s = args.log.lower()
        if s in ['file', 'both']:
            Log.info(msg)

        if s in ['console', 'both']:
            print(msg)
    except Exception as e:
        try:
            print('Log file failed to print.')
        except Exception as e:
            pass



#Spacy will be used to generate sentences, see species_catch at the bottom of this module
#import spacy as _sp
#Doc = spacy.load('en_core_web_sm')


from warnings import warn


import mmodb
import mmodb.model as model
from mmodb.model import Ugc, UgcHint
from mmo import name_entities as ne
from mmo import settings


from nlp import find
from funclib import baselib
import funclib.iolib as iolib


assert isinstance(mmodb.SESSION, sqlalchemy.orm.Session)

if iolib.wait_key('\n\n%s\nPress "Q" to quit\n' % mmodb.ENGINE) == 'q':
    quit()


SHORE_VOTE_THRESH = 2



class HintTypes():
    '''hint type enumeration'''
    platform = 'platform'
    date_hint = 'date_hint' #use hint to avoid keywords in SQL
    species = 'species'
    species_catch = 'species_catch' #actual species catches, will require sentence parsing, not used atm
    date_fragment = 'date_fragment'
    season = 'season'
    month = 'month_hint'


class Sources():
    '''sources enumeration'''
    title = 'title'
    post_text = 'post text'



def _get_whitelist_words(dump_list):
    '''(bool) -> list
    Load whitelist if it exists, otherwise
    recreate list and redump it. This is used
    to ensure the stop list doesnt include words
    we want to keep
    '''
    if iolib.file_exists(settings.PATHS.WHITELIST_WORDS) and not dump_list:
        return iolib.unpickle(settings.PATHS.WHITELIST_WORDS)

    words = [] + \
        ne.Afloat.get(add_similiar=True) + \
        ne.AfloatCharterBoat.get(add_similiar=True) + \
        ne.AfloatKayak.get(add_similiar=True) + \
        ne.AfloatPrivate.get(add_similiar=True) + \
        ne.GearAngling.get(add_similiar=True) + \
        ne.GearNoneAngling.get(add_similiar=True) + \
        ne.Metrological.get(add_similiar=True) + \
        ne.Session.get(add_similiar=True) + \
        ne.Species.get(add_similiar=False, force_plural_singular=True) + \
        ne.Time(add_similiar=True, force_plural_singular=True)

    if dump_list:
        iolib.pickle(words, settings.PATHS.WHITELIST_WORDS)
    return words


def _clean(s):
    '''clean open text'''
    #the order of this matters
    assert isinstance(s, str)
    s = _clean.strip_urls_list(s)
    s = _clean.base_substitutons(s) #base substitutions would make urls unidentifiable
    s = _clean.stop_words(s, _get_whitelist_words(False))
    s = s.replace("'", "")
    s = s.replace('"', '')
    s = _clean.non_breaking_space2space(s)
    s = _clean.newline_del_multi(s)
    s = _clean.txt2nr(s)
    return s



def make_date_hints(title, post_txt):
    '''(str, str) -> list, list, list, list, list, list, list, list, list
    get date hints
    
    title:post title
    post_txt: post main text
    returns: hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, date_hint
    '''
    hints = []; source_texts = []; sources = []
    dts = find.get_dates(title)
    if dts: ugc_hint = {'ugc_hint':dts[0]} #return this to write the best date to ugc table
    sources += [Sources.title] * len(dts)
    hints += dts

    dts = find.get_dates(post_txt)
    if dts and not ugc_hint: ugc_hint = {'date_hint':dts[0]} #return this to write the best date to ugc table if we didnt get it from the title
    sources += ['post body text'] * len(dts)
    hints += dts

    hint_types = [HintTypes.when] * len(hints)
    poss = [None] * len(hints)
    speciesids = [None] * len(hints)
    ns = [None] * len(hints)
    pos_lists = [None] * len(hints)
    source_texts = ['n/a for date hints'] * len(hints)
    return hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint


#byref
def _addit(dic, hint, source, hints, source_texts, poss, pos_lists, sources, ns, speciesids):
    '''(dict, str, str, list, list, list, list, list, list) -> int
    NB: hints, source_texts, pos_lists, sources, ns -> BY REF

    for basic text matches using named entities and fills
    hints, source_texts, pos_lists, sources, ns.
    
    Note poss is built for completeness, but all the data is in pos_lists so
    poss is just populated with Nones

    Example:
    >>>addit({'atlanta':[10,20], 'skipper':[500]}, 'charter', 'post text', hints, source_texts, poss, pos_lists, sources, ns)
    3
    >>>print(hints, source_texts, pos_lists, sources, ns)
    ['charter', 'charter'], ['atlanta', 'serentit'], [[10, 20], [500]], ['post text', 'post text']]

    So we have two keywords, one keyword appears twice, hence we return two hint summary records, one with
    a frequency of two and one with a frequency of 1.
    '''
    cnt = 0
    #it should look like {'charter':1, 'chartered':2, 'Mary Sue':1}
    for it in dic.items():
        hints += hint
        source_texts += it[0]
        sources += source
        poss += None
        pos_lists += it[1]
        ns += len(it[1])
        cnt += sum(it[1]) #a vote count
        speciesids += None
    return cnt


def make_platform_hints(title, post_txt):
    '''platform stuff'''
    hints = []; source_texts = []; poss = []; pos_lists = []; sources = []; ns = []
    ugc_hint = {'ugc_hint':None}
    vote_cnts = {'afloat':0, 'charter':0, 'kayak':0, 'private':0}

    #args after Sources.title are BYREF
    vote_cnts['afloat'] += _addit(ne.Afloat.indices(title), 'afloat', Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids) 
    vote_cnts['charter'] += _addit(ne.AfloatCharterBoat.indices(title), 'charter', Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids)
    vote_cnts['kayak'] += _addit(ne.AfloatKayak.indices(title), 'kayak', Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids)
    vote_cnts['private'] += _addit(ne.AfloatPrivate.indices(title), 'private', Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids)

    vote_cnts['afloat'] += _addit(ne.Afloat.indices(post_txt), 'afloat', Sources.post_text, hints, source_texts, poss, pos_lists, sources, ns, speciesids)
    vote_cnts['charter'] += _addit(ne.AfloatCharterBoat.indices(post_txt), 'charter', Sources.post_text, hints, source_texts, poss, pos_lists, sources, ns, speciesids)
    vote_cnts['kayak'] += _addit(ne.AfloatKayak.indices(post_txt), 'kayak', Sources.post_text, hints, source_texts, poss, pos_lists, sources, ns, speciesids)
    vote_cnts['private'] += _addit(ne.AfloatPrivate.indices(post_txt), 'private', Sources.post_text, hints, source_texts, poss, pos_lists, sources, ns, speciesids)
    assert isinstance(vote_cnts, dict)
    hint_types = [HintTypes.platform] * len(hints)
    votes = sum([x for x in vote_cnts.itervalues()])

    #NOW Get the platform hint to write to UGC table - ie what platform do we think the post was reporting
    if votes < SHORE_VOTE_THRESH:
        ugc_hint = {'ugc_hint': 'shore'}
    else:
        ugc_hint = {'ugc_hint': baselib.dic_key_with_max_val(vote_cnts)}
    #TODO write platform hint
    return hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint


def make_species_hints(title, post_text):
    '''detect species'''
    hints = []; source_texts = []; poss = []; pos_lists = []; sources = []; ns = []

    #we wont write
    _addit(ne.Species.indices(title), 'species', Sources.title, hints, source_texts, pos_lists, sources, ns) #args after Sources.title are BYREF
    _addit(ne.Species.indices(post_txt), 'species', Sources.post_text, hints, source_texts, pos_lists, sources, ns)
    hint_types = [HintTypes.species] * len(hints)
    return hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, {'ugc_hint':None}


def write_hints(ugcid, hint_types, hints, sources=None, source_texts=None, poss=None, speciesids=None, pos_lists=None, ns=None):
    '''write date hints'''
    #the following are optional, so if nothing passed, we create them
    
    if not hints:
        return

    fx = lambda lst, val: l if l else [v] * len(hints)
    ns = fx(ns, 1)
    speciesids = fx(speciesids, None)
    source_texts = fx(source_texts, None)
    pos_lists = fx(pos_lists, None)

    for i, hint in enumerate(hints):
        Item = UgcHint()
        Item.ugcid = ugcid
        Item.hint_type = hint_types[i]
        Item.hint = hint[i]

        #now the nullablefields
        if source_texts: Item.source_text = source_texts[i]
        if poss: Item.pos = poss[i]
        if speciesids: Item.speciesid = speciesids[i]
        if pos_lists: Item.pos_list = pos_lists[i]
        if sources: Item.source = sources[i]
        if ns: Item.n = ns[i]
        mmodb.SESSION.add(Item)



def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__) #use the module __doc__
    f = lambda s: [str(item) for item in s.split(',')]
    cmdline.add_argument('-s', '--slice', help='Record slice, eg -l 0,1000', type=f)
    args = cmdline.parse_args()

    offset = int(args.slice[0])
    max_row = int(args.slice[1])
    if not max_row or max_row in ('max', 'end', 'last'):
        max_row = n
    else:
        max_row = int(max_row)

    row_cnt = mmodb.SESSION.query(Ugc.ugcid).slice(offset, max_row).count()
    PP = iolib.PrintProgress(row_cnt, bar_length=20)

    window_size = 10  # or whatever limit you like
    window_idx = 0
    start, stop = window_size * window_idx + offset, window_size * (window_idx + 1) + offset

    while True:
        rows = mmodb.SESSION.query(Ugc).order_by(Ugc.ugcid).slice(start, stop).all()
        if rows is None:
            break

        for row in rows:
            assert isinstance(row, Ugc)
            mmodb.SESSION.query(UgcHint).filter(UgcHint.ugcid==row.ugcid).delete()
            txt_post_sql = _clean(row.txt_post_sql) #the raw text, after running clean sqls separately on sql server
            title = _clean(row.title)

            hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint = make_date_hints(title, txt_post_sql)
            row.date_hint = ugc_hint.get('ugc_hint') if ugc_hint.get('ugc_hint') else row.published_date
            write_hints(row.ugcid, hint_types, hints, sources, source_texts, poss, speciesids, pos_lists, ns) #order changed from the make call because some are by ref
            
            hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint = make_platform_hints(title, txt_post_sql)
            row.platform_hint = ugc_hint.get('ugc_hint') if ugc_hint.get('ugc_hint') else row.published_date
            write_hints(row.ugcid, hint_types, hints, sources, source_texts, poss, speciesids, pos_lists, ns)

            hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint = make_species_hints(title, txt_post_sql)
            #There is no platform hint for species
            write_hints(row.ugcid, hint_types, hints, sources, source_texts, poss, speciesids, pos_lists, ns)

            
            row.processed = True
            mmodb.SESSION.flush() #this sends the local changes cached in SQLAlchemy to the open transaction on the SQL Server
            PP.increment()

        try:
            mmodb.SESSION.commit()
        except Exception as e:
            warn('***Rolling Back***: %s' % e)
            mmodb.SESSION.rollback()


        if len(rows) < window_size:
            break

        window_idx += 1
        PP.increment(step=window_size, show_time_left=True)




if __name__ == "__main__":
    main()



def species_catch(txt_post):
    '''TEMP'''
    #place holder routine for if we want to actually detect
    #confirmed catches
    raise NotImplementedError
    #sentences = Doc(txt_post_sql)
    #for sent in sentences:
     #   sentence_pos = txt_post_sql.index(sent)
