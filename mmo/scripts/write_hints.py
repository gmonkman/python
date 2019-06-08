'''run some SQLS to fix common text mistakes'''
import argparse
from warnings import warn


import sqlalchemy
from pysimplelog import Logger
#import spacy
#Doc = spacy.load('en_core_web_sm')

from funclib.iolib import files_delete2
import mmo.settings as settings
import nlp as _nlp

import mmodb
import mmodb.model as model
from mmodb.model import Ugc, UgcHint
from mmo import name_entities as ne
from mmo.name_entities import UnspecifiedKeys #this is just an enumeration
from nlp import find
from funclib import baselib
import funclib.iolib as iolib


if iolib.wait_key('\n\n%s\nPress "Q" to quit\n' % mmodb.ENGINE) == 'q':
    quit()


SHORE_VOTE_THRESH = 2


class NamedEntities():
    print('\nSetting Up Named Entities...\n')
    Afloat = ne.Afloat()
    AfloatCharterBoat =  ne.AfloatCharterBoat()
    AfloatKayak = ne.AfloatKayak()
    AfloatPrivate = ne.AfloatPrivate()
    DateTimeDayOfWeek = ne.DateTimeDayOfWeek()
    DateTimeMonth = ne.DateTimeMonth()
    DateTimeSeason = ne.DateTimeSeason()
    GearAngling = ne.GearAngling()
    GearNoneAngling = ne.GearNoneAngling()
    Metrological = ne.MetrologicalAll()
    Session = ne.Session()
    SpeciesSpecified = ne.SpeciesSpecified()
    SpeciesUnspecified = ne.SpeciesUnspecified()
    SpeciesUnspecifiedBream = ne.SpeciesUnspecifiedBream()
    SpeciesUnspecifiedFlatfish = ne.SpeciesUnspecifiedFlatfish()
    SpeciesUnspecifiedMullet = ne.SpeciesUnspecifiedMullet()
    SpeciesUnspecifiedSole = ne.SpeciesUnspecifiedSole()


#region setup log
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
    except Exception as _:
        try:
            print('Log file failed to print.')
        except Exception as _:
            pass
#endregion



class HintTypes():
    '''hint type enumeration'''
    platform = 'platform'
    date_hint = 'date_hint' #use hint to avoid keywords in SQL
    species = 'species' #frequency of species mentions
    species_catch = 'species_catch' #actual species catches, will require sentence parsing, not used atm
    month_hint = 'month_hint'
    season_hint = 'season_hint'
    trip = 'trip' #does it look like a trip



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
        NamedEntities.Afloat._get(add_similiar=True) + \
        NamedEntities.AfloatCharterBoat._get(add_similiar=True) + \
        NamedEntities.AfloatKayak._get(add_similiar=True) + \
        NamedEntities.AfloatPrivate._get(add_similiar=True) + \
        NamedEntities.DateTimeDayOfWeek.NOUN_DICT_ALL + \
        NamedEntities.DateTimeMonth.NOUN_DICT_ALL + \
        NamedEntities.DateTimeSeason.NOUN_DICT_ALL + \
        NamedEntities.GearAngling._get(add_similiar=True) + \
        NamedEntities.GearNoNamedEntitiesAngling.get(add_similiar=True) + \
        NamedEntities.Metrological._get(add_similiar=True) + \
        NamedEntities.Session._get(add_similiar=True) + \
        NamedEntities.SpeciesSpecified.NOUN_DICT_ALL + \
        NamedEntities.SpeciesUnspecified.NOUN_DICT_ALL + \
        NamedEntities.SpeciesUnspecifiedBream.NOUN_DICT_ALL + \
        NamedEntities.SpeciesUnspecifiedFlatfish.NOUN_DICT_ALL + \
        NamedEntities.SpeciesUnspecifiedMullet.NOUN_DICT_ALL + \
        NamedEntities.SpeciesUnspecifiedSole.NOUN_DICT_ALL

    if dump_list:
        iolib.pickle(words, settings.PATHS.WHITELIST_WORDS)
    return words


def _clean(s):
    '''clean open text'''
    #the order of this matters
    assert isinstance(s, str)
    s = _nlp.clean.strip_urls_list(s)
    s = _nlp.clean.sep_num_from_words(s)
    s = _nlp.clean.base_substitutons(s) #base substitutions would make urls unidentifiable
    s = _nlp.clean.stop_words(s, _get_whitelist_words(False))
    s = s.replace("'", "")
    s = s.replace('"', '')
    s = _nlp.clean.non_breaking_space2space(s)
    s = _nlp.clean.newline_del_multi(s)
    s = _nlp.clean.txt2nr(s)
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
        if hint in NamedEntities.SpeciesSpecified.SPECIES_DICT.keys():
            speciesids += hint
        else:
            speciesids += None
    return cnt


def make_trip_hints(title, post_txt):
    '''platform stuff'''
    hints = []; source_texts = []; poss = []; pos_lists = []; sources = []; ns = []; speciesids = []
    ugc_hint = {'ugc_hint':None}

    all_keywords = NamedEntities.Session._get() + NamedEntities.Metrological._get()
    found = False
    for w in all_keywords:
        if w in title:
            hints = [w]
            source_texts = [Sources.title]
            found = True
            break

        if w in post_txt:
            hints = [w]
            source_texts = [Sources.post_text]
            found = True
            break

    hint_types = [HintTypes.trip]
    ugc_hint = {'ugc_hint': int(found)}
    ns = [1]
    return hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint





def make_platform_hints(title, post_txt):
    '''platform stuff'''
    hints = []; source_texts = []; poss = []; pos_lists = []; sources = []; ns = []; speciesids = []
    ugc_hint = {'ugc_hint':None}
    vote_cnts = {'afloat':0, 'charter':0, 'kayak':0, 'private':0}

    #args after Sources.title are BYREF
    vote_cnts['afloat'] += _addit(NamedEntities.Afloat.indices(title), 'afloat', Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids) 
    vote_cnts['charter'] += _addit(NamedEntities.AfloatCharterBoat.indices(title), 'charter', Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids)
    vote_cnts['kayak'] += _addit(NamedEntities.AfloatKayak.indices(title), 'kayak', Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids)
    vote_cnts['private'] += _addit(NamedEntities.AfloatPrivate.indices(title), 'private', Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids)

    vote_cnts['afloat'] += _addit(NamedEntities.Afloat.indices(post_txt), 'afloat', Sources.post_text, hints, source_texts, poss, pos_lists, sources, ns, speciesids)
    vote_cnts['charter'] += _addit(NamedEntities.AfloatCharterBoat.indices(post_txt), 'charter', Sources.post_text, hints, source_texts, poss, pos_lists, sources, ns, speciesids)
    vote_cnts['kayak'] += _addit(NamedEntities.AfloatKayak.indices(post_txt), 'kayak', Sources.post_text, hints, source_texts, poss, pos_lists, sources, ns, speciesids)
    vote_cnts['private'] += _addit(NamedEntities.AfloatPrivate.indices(post_txt), 'private', Sources.post_text, hints, source_texts, poss, pos_lists, sources, ns, speciesids)
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


#this is the simple frequency of species mentions in the text
def make_species_hints(title, post_text):
    '''detect occurence of species names and count them
    hints contains speciesids
    '''
    #This is a little different as we need to add speciesids for the spelling we have found
    hints = []; source_texts = []; poss = []; pos_lists = []; sources = []; ns = []; speciesids = []
    
    vote_cnts = {}

    for speciesid in NamedEntities.SpeciesSpecified.NOUN_DICT_ALL.keys(): #addit processes the list of species under each key
        if not vote_cnts.get(speciesid): vote_cnts[speciesid] = 0
        vote_cnts[speciesid] += _addit(NamedEntities.SpeciesSpecified.indices(title, speciesid), speciesid, Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids)
        vote_cnts[speciesid] += _addit(NamedEntities.SpeciesSpecified.indices(post_text, speciesid), speciesid, Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids)
    
    all_found = set(list(vote_cnts.keys()))
    #now we have to deal with unspecifieds
    #we are deleting all the keys in unspecified where
    #there has been a specific species match for that unspecified category
    #e.g. 
    #dUnspecified={'breams':['black', 'couch'}
    #vote_cnts = {'black bream':1, 'bass':4}, so all found = ['black bream', 'bass']
    #we then delete all keys from dUnspecified which with values in all found
    #we use sets as they are fast
    dUnspecified = dict(NamedEntities.SpeciesUnspecified.NOUN_DICT)
    for speciesid, species in NamedEntities.SpeciesUnspecified.NOUN_DICT:
        if not set(species).isdisjoint(all_found):
            del(dUnspecified[speciesid])

    #dUnspecified should now just contain unspecified species
    #where more specific species have not been found
    if UnspecifiedKeys.sole in dUnspecified.keys():
        for speciesid in NamedEntities.SpeciesUnspecifiedSole.NOUN_DICT_ALL.keys():        #do sole, the more specific first
            if not vote_cnts.get(speciesid): vote_cnts[speciesid] = 0
            vote_cnts[speciesid] += _addit(NamedEntities.SpeciesUnspecifiedSole.indices(title, speciesid), speciesid, Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids)
            vote_cnts[speciesid] += _addit(NamedEntities.SpeciesUnspecifiedSole.indices(post_text, speciesid), speciesid, Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids)

    if UnspecifiedKeys.flatfish in dUnspecified.keys():
        for speciesid in NamedEntities.SpeciesUnspecifiedFlatfish.NOUN_DICT_ALL.keys():        #do sole, the more specific first
            if not vote_cnts.get(speciesid): vote_cnts[speciesid] = 0
            vote_cnts[speciesid] += _addit(NamedEntities.SpeciesUnspecifiedSole.indices(title, speciesid), speciesid, Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids)
            vote_cnts[speciesid] += _addit(NamedEntities.SpeciesUnspecifiedSole.indices(post_text, speciesid), speciesid, Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids)

    if UnspecifiedKeys.bream in dUnspecified.keys():
        for speciesid in NamedEntities.SpeciesUnspecifiedBream.NOUN_DICT_ALL.keys():        #do sole, the more specific first
            if not vote_cnts.get(speciesid): vote_cnts[speciesid] = 0
            vote_cnts[speciesid] += _addit(NamedEntities.SpeciesUnspecifiedSole.indices(title, speciesid), speciesid, Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids)
            vote_cnts[speciesid] += _addit(NamedEntities.SpeciesUnspecifiedSole.indices(post_text, speciesid), speciesid, Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids)

    if UnspecifiedKeys.mullet in dUnspecified.keys():
        for speciesid in NamedEntities.SpeciesUnspecifiedMullet.NOUN_DICT_ALL.keys():        #do sole, the more specific first
            if not vote_cnts.get(speciesid): vote_cnts[speciesid] = 0
            vote_cnts[speciesid] += _addit(NamedEntities.SpeciesUnspecifiedSole.indices(title, speciesid), speciesid, Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids)
            vote_cnts[speciesid] += _addit(NamedEntities.SpeciesUnspecifiedSole.indices(post_text, speciesid), speciesid, Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids)

    if UnspecifiedKeys.skate_ray in dUnspecified.keys():
        for speciesid in NamedEntities.SpeciesUnspecifiedSkatesRays.NOUN_DICT_ALL.keys():        #do sole, the more specific first
            if not vote_cnts.get(speciesid): vote_cnts[speciesid] = 0
            vote_cnts[speciesid] += _addit(NamedEntities.SpeciesUnspecifiedSole.indices(title, speciesid), speciesid, Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids)
            vote_cnts[speciesid] += _addit(NamedEntities.SpeciesUnspecifiedSole.indices(post_text, speciesid), speciesid, Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids)


    hint_types = [HintTypes.species] * len(hints)
    return hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, {'ugc_hint':None}


def make_month_hints(title, post_text):
    '''date fragment hints, e.g. summer, spring, may'''
    #This is a little different as we need to add speciesids for the spelling we have found
    hints = []; source_texts = []; poss = []; pos_lists = []; sources = []; ns = []; speciesids = []
    
    vote_cnts = {}

    for monthid in NamedEntities.DateTimeMonth.NOUN_DICT_ALL.keys(): #addit processes the list of species under each key
        if not vote_cnts.get(monthid): vote_cnts[monthid] = 0
        vote_cnts[monthid] += _addit(NamedEntities.DateTimeMonth.indices(title, monthid), monthid, Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids)
        vote_cnts[monthid] += _addit(NamedEntities.DateTimeMonth.indices(title, monthid), monthid, Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids)

    assert isinstance(vote_cnts, dict)
    hint_types = [HintTypes.season_hint] * len(hints)

    #NOW Get the month with the most votes, provided something appeared
    if any([x > 0 for x in vote_cnts.values()]):
        ugc_hint = {'ugc_hint': max(vote_cnts, key=lambda key: max(s, key=lambda key: s[key])[key])}

    return hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint


def make_season_hints(title, post_text):
    '''date fragment hints, e.g. summer, spring, may'''
    #This is a little different as we need to add speciesids for the spelling we have found
    hints = []; source_texts = []; poss = []; pos_lists = []; sources = []; ns = []; speciesids = []
    
    vote_cnts = {}

    for seasonid in NamedEntities.DateTimeSeason.NOUN_DICT_ALL.keys(): #addit processes the list of species under each key
        if not vote_cnts.get(seasonid): vote_cnts[seasonid] = 0
        vote_cnts[seasonid] += _addit(NamedEntities.DateTimeSeason.indices(title, seasonid), seasonid, Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids)
        vote_cnts[seasonid] += _addit(NamedEntities.DateTimeSeason.indices(title, seasonid), seasonid, Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids)

    assert isinstance(vote_cnts, dict)
    hint_types = [HintTypes.season_hint] * len(hints)

    #NOW Get the month with the most votes, provided something appeared
    if any([x > 0 for x in vote_cnts.values()]):
        ugc_hint = {'ugc_hint': max(vote_cnts, key=lambda key: max(s, key=lambda key: s[key])[key])}

    return hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint


def make_catch_hints(title, post_text):
    '''catch hints'''
    
    hints = []; source_texts = []; poss = []; pos_lists = []; sources = []; ns = []; speciesids = []
    
    vote_cnts = {}
    addit_ = {}

    
    def _fillit(SpeciesDict, title, post_text):
        nonlocal hints, source_texts, sources
        for speciesid, aliass in SpeciesDict.items(): #addit processes the list of species under each key
            for s in aliass:
                if title and _nlp.relib.CheckDistanceAnyNumber(title, s, 8):
                    hints += speciesid
                    source_texts += s
                    sources += Sources.post_text

                if post_text and _nlp.relib.CheckDistanceAnyNumber(post_text, s, 8):
                    hints += speciesid
                    hint_type += HintTypes.species_catch
                    source_texts += s
                    sources += Sources.title


    #yes, we are just looking for a number by a species name anywhere
    _fillit(NamedEntities.SpeciesSpecified.NOUN_DICT_ALL, title, post_text)
         
    all_found = set(hints)
    #now we have to deal with unspecifieds
    #we are deleting all the keys in unspecified where
    #there has been a specific species match for that unspecified category
    #e.g. 
    #dUnspecified={'breams':['black', 'couch'}
    #vote_cnts = {'black bream':1, 'bass':4}, so all found = ['black bream', 'bass']
    #we then delete all keys from dUnspecified which with values in all found
    #we use sets as they are fast
    dUnspecified = dict(NamedEntities.SpeciesUnspecified.NOUN_DICT)
    for speciesid, species in NamedEntities.SpeciesUnspecified.NOUN_DICT:
        if not set(species).isdisjoint(all_found):
            del(dUnspecified[speciesid])

    #Udnspecified should now just contain unspecified species
    #where more specific species have not been found
    if UnspecifiedKeys.sole in dUnspecified.keys():
        _fillit(NamedEntities.SpeciesUnspecifiedSole.NOUN_DICT_ALL, title, post_text) 

    if UnspecifiedKeys.flatfish in dUnspecified.keys():
        _fillit(NamedEntities.SpeciesUnspecifiedFlatfish.NOUN_DICT_ALL, title, post_text) 

    if UnspecifiedKeys.bream in dUnspecified.keys():
        _fillit(NamedEntities.SpeciesUnspecifiedBream.NOUN_DICT_ALL, title, post_text) 

    if UnspecifiedKeys.mullet in dUnspecified.keys():
        _fillit(NamedEntities.SpeciesUnspecifiedMullet.NOUN_DICT_ALL, title, post_text) 

    if UnspecifiedKeys.skate_ray in dUnspecified.keys():
        _fillit(NamedEntities.SpeciesUnspecifiedSkatesRays.NOUN_DICT_ALL, title, post_text) 

    ns = [1] * len(hints)
    pos_lists = [None] * len(hints)
    poss = [None] * len(hints)

    #if we say we caught a fish, we say it was a trip
    if hints:
        ugc_hint = {'ugc_hint': True}
    else:
        ugc_hint = {'ugc_hint': False}
    return hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint



def write_hints(ugcid, hint_types, hints, sources=None, source_texts=None, poss=None, speciesids=None, pos_lists=None, ns=None, skip_on_zero_n=True):
    '''write date hints'''
    #the following are optional, so if nothing passed, we create them
    
    if not hints:
        return

    fx = lambda lst, val: lst if lst else [val] * len(hints)
    ns = fx(ns, 1)
    speciesids = fx(speciesids, None)
    source_texts = fx(source_texts, None)
    pos_lists = fx(pos_lists, None)

    for i, hint in enumerate(hints):
        if ns:
            if ns[i]:
                if ns[i] == 0 and skip_on_zero_n:
                    continue
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
    cmdliNamedEntities.add_argument('-s', '--slice', help='Record slice, eg -l 0,1000', type=f)
    args = cmdliNamedEntities.parse_args()

    offset = int(args.slice[0])
    max_row = int(args.slice[1])
    if not max_row or max_row in ('max', 'end', 'last'):
        max_row = mmodb.SESSION.query(Ugc.ugcid).count()
    else:
        max_row = int(max_row)

    row_cnt = mmodb.SESSION.query(Ugc.ugcid).slice(offset, max_row).count()
    PP = iolib.PrintProgress(row_cnt, bar_length=20)

    window_size = 10  # or whatever limit you like
    window_idx = 0
    start, stop = window_size * window_idx + offset, window_size * (window_idx + 1) + offset

    while True:
        rows = mmodb.SESSION.query(Ugc).filter_by(processed=0).order_by(Ugc.ugcid).slice(start, stop).all()
        if rows is None:
            break

        for row in rows:
            assert isinstance(row, Ugc)
            mmodb.SESSION.query(UgcHint).options(load_only('ugcid', 'source', 'title', 'txt_post_sql', 'date_hint', 'platform_hint', 'processed', 'season_hint', 'month_hint')).filter(UgcHint.ugcid == row.ugcid).delete()
            txt_post_sql = _clean(row.txt_post_sql) #the raw text, after running clean sqls separately on sql server
            title = _clean(row.title)

            hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint = make_date_hints(title, txt_post_sql)
            row.date_hint = ugc_hint.get('ugc_hint') if ugc_hint.get('ugc_hint') else row.published_date
            write_hints(row.ugcid, hint_types, hints, sources, source_texts, poss, speciesids, pos_lists, ns) #order changed from the make call because some are by ref
            
            hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint = make_platform_hints(title, txt_post_sql)
            row.platform_hint = ugc_hint.get('ugc_hint') if ugc_hint.get('ugc_hint') else 'shore'
            write_hints(row.ugcid, hint_types, hints, sources, source_texts, poss, speciesids, pos_lists, ns)

            hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint = make_month_hints(title, txt_post_sql)
            row.month_hint = ugc_hint.get('ugc_hint') if ugc_hint.get('ugc_hint') else None
            write_hints(row.ugcid, hint_types, hints, sources, source_texts, poss, speciesids, pos_lists, ns)

            hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint = make_season_hints(title, txt_post_sql)
            row.month_hint = ugc_hint.get('ugc_hint') if ugc_hint.get('ugc_hint') else None
            write_hints(row.ugcid, hint_types, hints, sources, source_texts, poss, speciesids, pos_lists, ns)

            hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint = make_species_hints(title, txt_post_sql)
            #There is no platform hint for species
            write_hints(row.ugcid, hint_types, hints, sources, source_texts, poss, speciesids, pos_lists, ns)

            hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint = make_catch_hints(title, txt_post_sql)
            was_catch = ugc_hint.get('ugc_hint')
            write_hints(row.ugcid, hint_types, hints, sources, source_texts, poss, speciesids, pos_lists, ns)


            hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint = make_trip_hints(title, txt_post_sql)
            if not was_catch:
                row.catch_hint = bool(ugc_hint.get('ugc_hint'))
            else:
                row.catch_hint = was_catch
            row.catch_hint = was_catch
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
