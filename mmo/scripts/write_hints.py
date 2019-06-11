'''run some SQLS to fix common text mistakes'''
import argparse
from warnings import warn


import sqlalchemy
from sqlalchemy.orm import load_only


#import spacy
#Doc = spacy.load('en_core_web_sm')

from funclib.iolib import files_delete2
import mmo.settings as settings
import nlp as _nlp
import nlp.clean as nlpclean

import mmodb
import mmodb.model as model
from mmodb.model import Ugc, UgcHint
from mmo import name_entities as ne
from nlp import find
from funclib import baselib
import funclib.iolib as iolib
from funclib.stopwatch import StopWatch

#if iolib.wait_key('\n\n%s\nPress "Q" to quit\n' % mmodb.ENGINE) == 'q':
    #quit()


SHORE_VOTE_THRESH = 2


#region setup log
from pysimplelog import Logger
files_delete2(settings.PATHS.LOG_WRITE_HINTS)
Log = Logger(name='train', logToStdout=False, logToFile=True, logFileMaxSize=1)
Log.set_log_file(settings.PATHS.LOG_WRITE_HINTS)
print('\nLogging to %s\n' % settings.PATHS.LOG_WRITE_HINTS)


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



def make_date_hints(title, post_txt):
    '''(str, str) -> list, list, list, list, list, list, list, list, list
    get date hints
    
    title:post title
    post_txt: post main text
    returns: hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, date_hint
    '''
    hint_types = []; poss = []; source_texts = []; hints = []; speciesids = []; pos_lists = []; ns = []; sources = []; ugc_hint = {}
    dts = find.get_dates(title) #TODO Support multiple dates
    if dts:
        if not ugc_hint: ugc_hint = {'ugc_hint':dts[0]} #return this to write the best date to ugc table
        for d in dts:
            hints += [d]
            sources += [Sources.title]

    dts = find.get_dates(post_txt)
    if dts:
        if not ugc_hint: ugc_hint = {'ugc_hint':dts[0]} #return this to write the best date to ugc table
        for d in dts:
            hints += [d]
            sources += [Sources.post_text]

    if hints:
        hint_types = [HintTypes.date_hint] * len(hints)
        poss = [None] * len(hints)
        speciesids = [None] * len(hints)
        ns = [None] * len(hints)
        pos_lists = [None] * len(hints)
        source_texts = [None] * len(hints)
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
    for key, inds in dic.items():
        hints += [hint]
        source_texts += [key]
        sources += [source]
        poss += [None]
        pos_lists.append(inds)
        ns += [len(inds)]
        cnt += len(inds) #a vote count
        if hint in ne.SpeciesAll.nouns_dict_all.keys():
            speciesids += [hint]
        else:
            speciesids += [None]
    return cnt


def make_trip_hints(title, post_txt):
    '''platform stuff'''
    hint_types = []; poss = []; source_texts = []; hints = []; speciesids = []; pos_lists = []; ns = []; sources = []; ugc_hint = {}
    ugc_hint = {'ugc_hint':None}

    all_keywords = ne.Session.allwords
    all_keywords |= ne.MetrologicalAll.allwords
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
    hint_types = []; poss = []; source_texts = []; hints = []; speciesids = []; pos_lists = []; ns = []; sources = []; ugc_hint = {}
    ugc_hint = {'ugc_hint':None}
    vote_cnts = {}
    #args after Sources.title are BYREF
    _vc(vote_cnts, 'afloat', _addit(ne.Afloat.indices(title), 'afloat', Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids)) 
    _vc(vote_cnts, 'charter', _addit(ne.AfloatCharterBoat.indices(title), 'charter', Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids))
    _vc(vote_cnts, 'kayak', _addit(ne.AfloatKayak.indices(title), 'kayak', Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids))
    _vc(vote_cnts, 'private', _addit(ne.AfloatPrivate.indices(title), 'private', Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids))

    _vc(vote_cnts, 'afloat', _addit(ne.Afloat.indices(post_txt), 'afloat', Sources.post_text, hints, source_texts, poss, pos_lists, sources, ns, speciesids))
    _vc(vote_cnts, 'charter', _addit(ne.AfloatCharterBoat.indices(post_txt), 'charter', Sources.post_text, hints, source_texts, poss, pos_lists, sources, ns, speciesids))
    _vc(vote_cnts, 'kayak', _addit(ne.AfloatKayak.indices(post_txt), 'kayak', Sources.post_text, hints, source_texts, poss, pos_lists, sources, ns, speciesids))
    _vc(vote_cnts, 'private', _addit(ne.AfloatPrivate.indices(post_txt), 'private', Sources.post_text, hints, source_texts, poss, pos_lists, sources, ns, speciesids))
    assert isinstance(vote_cnts, dict)
    hint_types = [HintTypes.platform] * len(hints)
    votes = sum([x for x in vote_cnts.values()])

    #NOW Get the platform hint to write to UGC table - ie what platform do we think the post was reporting
    if votes < SHORE_VOTE_THRESH:
        ugc_hint = {'ugc_hint': 'shore'}
    else:
        ugc_hint = {'ugc_hint': baselib.dic_key_with_max_val(vote_cnts)}

    return hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint


def _vc(vote_cnts, key, int_):
    '''byref'''
    if int_ > 0:
        if vote_cnts.get(key):
            vote_cnts[key] += int_
        else:
            vote_cnts[key] = int_


#this is the simple frequency of species mentions in the text
def make_species_hints(title, post_text):
    '''detect occurence of species names and count them
    hints contains speciesids
    '''
    #This is a little different as we need to add speciesids for the spelling we have found
    hint_types = []; poss = []; source_texts = []; hints = []; speciesids = []; pos_lists = []; ns = []; sources = []
    
    vote_cnts = {}
    ugc_hint = {'ugc_hint':None}
    for speciesid in ne.SpeciesSpecified.nouns_dict_all.keys(): #addit processes the list of species under each key
        _vc(vote_cnts, speciesid, _addit(ne.SpeciesSpecified.indices(title, speciesid), speciesid, Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids))
        _vc(vote_cnts, speciesid, _addit(ne.SpeciesSpecified.indices(post_text, speciesid), speciesid, Sources.post_text, hints, source_texts, poss, pos_lists, sources, ns, speciesids))
    
    all_found = set(list(vote_cnts.keys()))
    if all_found.isdisjoint(ne.GroupsForUnspecified.SOLE_SPECIFIED_KEYS):
        for speciesid in ne.SpeciesUnspecifiedSole.nouns_dict_all.keys():        #do sole, the more specific first
            _vc(vote_cnts, speciesid, _addit(ne.SpeciesUnspecifiedSole.indices(title, speciesid), speciesid, Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids))
            _vc(vote_cnts, speciesid, _addit(ne.SpeciesUnspecifiedSole.indices(post_text, speciesid), speciesid, Sources.post_text, hints, source_texts, poss, pos_lists, sources, ns, speciesids))

    if all_found.isdisjoint(ne.GroupsForUnspecified.FLATFISH_SPECIFIED_KEYS):
        for speciesid in ne.SpeciesUnspecifiedFlatfish.nouns_dict_all.keys():        #do sole, the more specific first
            _vc(vote_cnts, speciesid, _addit(ne.SpeciesUnspecifiedFlatfish.indices(title, speciesid), speciesid, Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids))
            _vc(vote_cnts, speciesid, _addit(ne.SpeciesUnspecifiedFlatfish.indices(post_text, speciesid), speciesid, Sources.post_text, hints, source_texts, poss, pos_lists, sources, ns, speciesids))

    if all_found.isdisjoint(ne.GroupsForUnspecified.BREAM_SPECIFIED_KEYS):
        for speciesid in ne.SpeciesUnspecifiedBream.nouns_dict_all.keys():        #do sole, the more specific first
            _vc(vote_cnts, speciesid, _addit(ne.SpeciesUnspecifiedBream.indices(title, speciesid), speciesid, Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids))
            _vc(vote_cnts, speciesid, _addit(ne.SpeciesUnspecifiedBream.indices(post_text, speciesid), speciesid, Sources.post_text, hints, source_texts, poss, pos_lists, sources, ns, speciesids))

    if all_found.isdisjoint(ne.GroupsForUnspecified.MULLET_SPECIFIED_KEYS):
        for speciesid in ne.SpeciesUnspecifiedMullet.nouns_dict_all.keys():        #do sole, the more specific first
            _vc(vote_cnts, speciesid, _addit(ne.SpeciesUnspecifiedMullet.indices(title, speciesid), speciesid, Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids))
            _vc(vote_cnts, speciesid, _addit(ne.SpeciesUnspecifiedMullet.indices(post_text, speciesid), speciesid, Sources.post_text, hints, source_texts, poss, pos_lists, sources, ns, speciesids))

    if all_found.isdisjoint(ne.GroupsForUnspecified.SKATE_RAY_SPECIFIED_KEYS):
        for speciesid in ne.SpeciesUnspecifiedSkatesRays.nouns_dict_all.keys():        #do sole, the more specific first
            _vc(vote_cnts, speciesid, _addit(ne.SpeciesUnspecifiedSkatesRays.indices(title, speciesid), speciesid, Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids))
            _vc(vote_cnts, speciesid, _addit(ne.SpeciesUnspecifiedSkatesRays.indices(post_text, speciesid), speciesid, Sources.post_text, hints, source_texts, poss, pos_lists, sources, ns, speciesids))

    speciesids = hints 
    hint_types = [HintTypes.species] * len(hints)
    return hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint


def make_month_hints(title, post_text):
    '''date fragment hints, e.g. summer, spring, may'''
    #This is a little different as we need to add speciesids for the spelling we have found
    hint_types = []; poss = []; source_texts = []; hints = []; speciesids = []; pos_lists = []; ns = []; sources = []; ugc_hint = {}
    
    vote_cnts = {}

    for monthid in ne.DateTimeMonth.nouns_dict_all.keys(): #addit processes the list of species under each key
        _vc(vote_cnts, monthid, _addit(ne.DateTimeMonth.indices(title, monthid), monthid, Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids))
        _vc(vote_cnts, monthid, _addit(ne.DateTimeMonth.indices(post_text, monthid), monthid, Sources.post_text, hints, source_texts, poss, pos_lists, sources, ns, speciesids))

    assert isinstance(vote_cnts, dict)
    if hints:
        hint_types = [HintTypes.month_hint] * len(hints)
    #NOW Get the month with the most votes, provided something appeared
    if any([x > 0 for x in vote_cnts.values()]):
        ugc_hint = {'ugc_hint': max(vote_cnts, key=lambda key: vote_cnts[key])}

    return hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint


def make_season_hints(title, post_text):
    '''date fragment hints, e.g. summer, spring, may'''
    #This is a little different as we need to add speciesids for the spelling we have found
    hint_types = []; poss = []; source_texts = []; hints = []; speciesids = []; pos_lists = []; ns = []; sources = []; ugc_hint = {}
    
    vote_cnts = {}

    for seasonid in ne.DateTimeSeason.nouns_dict_all.keys(): #addit processes the list of species under each key
        _vc(vote_cnts, seasonid, _addit(ne.DateTimeSeason.indices(title, seasonid), seasonid, Sources.title, hints, source_texts, poss, pos_lists, sources, ns, speciesids))
        _vc(vote_cnts, seasonid, _addit(ne.DateTimeSeason.indices(post_text, seasonid), seasonid, Sources.post_text, hints, source_texts, poss, pos_lists, sources, ns, speciesids))


    assert isinstance(vote_cnts, dict)
    if hints:
        hint_types = [HintTypes.season_hint] * len(hints)

    #NOW Get the month with the most votes, provided something appeared
    if any([x > 0 for x in vote_cnts.values()]):
        ugc_hint = {'ugc_hint': max(vote_cnts, key=lambda key: vote_cnts[key])}

    return hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint


def make_catch_hints(title, post_text):
    '''catch hints'''    
    hint_types = []; poss = []; source_texts = []; hints = []; speciesids = []; pos_lists = []; ns = []; sources = []; ugc_hint = {}

    def _fillit(SpeciesDict, title, post_text):
        nonlocal hints, source_texts, sources
        for speciesid, aliass in SpeciesDict.items(): #addit processes the list of species under each key
            for s in aliass:
                if title and _nlp.relib.CheckDistanceAnyNumber(title, s, 8):
                    hints += [speciesid]
                    source_texts += [s]
                    sources += [Sources.post_text]

                if post_text and _nlp.relib.CheckDistanceAnyNumber(post_text, s, 8):
                    hints += [speciesid]
                    source_texts += [s]
                    sources += [Sources.title]


    #yes, we are just looking for a number by a species name anywhere
    _fillit(ne.SpeciesSpecified.nouns_dict_all, title, post_text)  
    all_found = set(hints)
    if all_found.isdisjoint(ne.GroupsForUnspecified.SOLE_SPECIFIED_KEYS):
        _fillit(ne.SpeciesUnspecifiedSole.nouns_dict_all, title, post_text) 

    if all_found.isdisjoint(ne.GroupsForUnspecified.FLATFISH_SPECIFIED_KEYS):
        _fillit(ne.SpeciesUnspecifiedFlatfish.nouns_dict_all, title, post_text) 

    if all_found.isdisjoint(ne.GroupsForUnspecified.BREAM_SPECIFIED_KEYS):
        _fillit(ne.SpeciesUnspecifiedBream.nouns_dict_all, title, post_text) 

    if all_found.isdisjoint(ne.GroupsForUnspecified.MULLET_SPECIFIED_KEYS):
        _fillit(ne.SpeciesUnspecifiedMullet.nouns_dict_all, title, post_text) 

    if all_found.isdisjoint(ne.GroupsForUnspecified.SKATE_RAY_SPECIFIED_KEYS):
        _fillit(ne.SpeciesUnspecifiedSkatesRays.nouns_dict_all, title, post_text) 

    #if we say we caught a fish, we say it was a trip
    if hints:
        ns = [1] * len(hints)
        pos_lists = [None] * len(hints)
        poss = [None] * len(hints)
        hint_types = [HintTypes.species_catch] * len(hints)
        ugc_hint = {'ugc_hint': True}
    else:
        ugc_hint = {'ugc_hint': False}
    return hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint



def write_hints(ugcid, hint_types, hints, sources=None, source_texts=None, poss=None, speciesids=None, pos_lists=None, ns=None, skip_on_zero_n=True):
    '''write date hints'''
    #the following are optional, so if nothing passed, we create them
    
    if not hints: return

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
        Item.hint = hint

        #now the nullablefields
        if source_texts: Item.source_text = source_texts[i]
        if poss: Item.pos = poss[i]
        if speciesids: Item.speciesid = speciesids[i]
        if pos_lists: Item.pos_list = str(pos_lists[i])
        if sources: Item.source = sources[i]
        if ns: Item.n = ns[i]
        mmodb.SESSION.add(Item)



def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__) #use the module __doc__
    f = lambda s: [str(item) for item in s.split(',')]
    cmdline.add_argument('-s', '--slice', help='Record slice, eg -s 0,1000', type=f)
    args = cmdline.parse_args()

    offset = int(args.slice[0])
    max_row = args.slice[1]
    if max_row in ('max', 'end', 'last'):
        max_row = mmodb.SESSION.query(Ugc.ugcid).count()
    else:
        max_row = int(max_row)

    row_cnt = mmodb.SESSION.query(Ugc.ugcid).filter_by(processed=0).order_by(Ugc.ugcid).slice(offset, max_row).count()
    PP = iolib.PrintProgress(row_cnt, bar_length=20)

    window_size = 10  # or whatever limit you like
    window_idx = 0
    

    while True:
        start, stop = window_size * window_idx + offset, window_size * (window_idx + 1) + offset
        rows = mmodb.SESSION.query(Ugc).options(load_only('ugcid', 'title', 'txt_cleaned', 'platform_hint', 'processed', 'season_hint', 'month_hint', 'trip_hint', 'catch_hint')).filter_by(processed=0).order_by(Ugc.ugcid).slice(start, stop).all()
        if rows is None:
            break
        SW = StopWatch()
        try:
            for row in rows:
                assert isinstance(row, Ugc)
                mmodb.SESSION.query(UgcHint).filter(UgcHint.ugcid == row.ugcid).delete()
                txt_cleaned = row.txt_cleaned; title = nlpclean.clean(row.title)
                if not txt_cleaned: PP.increment(show_time_left=True); continue

                SW.lap()
                hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint = make_species_hints(title, txt_cleaned)
                if not hints: SW.lap(); PP.increment(show_time_left=True); continue #if it doesnt mention species, skip the rest           
                write_hints(row.ugcid, hint_types, hints, sources, source_texts, poss, speciesids, pos_lists, ns)
                SW.lap(); print('make_species_hints:%s' % SW.pretty_time(SW.event_rate_last))
            

                #print('hint_type:\t%s\nhints:\t%s\nsource_texts:\t%s\nnpos_lists:\t%s\nns%s' % (hint_types, hints, source_texts, pos_lists, ns))
                SW.lap()
                hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint = make_month_hints(title, txt_cleaned)
                row.month_hint = ugc_hint.get('ugc_hint') if ugc_hint.get('ugc_hint') else None
                write_hints(row.ugcid, hint_types, hints, sources, source_texts, poss, speciesids, pos_lists, ns)
                SW.lap(); print('make_month_hints:%s' % SW.pretty_time(SW.event_rate_last))


                SW.lap()
                #hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint = make_season_hints(title, txt)
                #row.month_hint = ugc_hint.get('ugc_hint') if ugc_hint.get('ugc_hint') else None
                #write_hints(row.ugcid, hint_types, hints, sources, source_texts, poss, speciesids, pos_lists, ns)
                SW.lap(); print('make_season_hints:%s' % SW.pretty_time(SW.event_rate_last))


                #TODO Reenable at some point
                #hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint = make_date_hints(title, txt)
                #row.date_hint = ugc_hint.get('ugc_hint') if ugc_hint.get('ugc_hint') else row.published_date
                #write_hints(row.ugcid, hint_types, hints, sources, source_texts, poss, speciesids, pos_lists, ns) #order changed from the make call because some are by ref
            
                SW.lap()
                hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint = make_platform_hints(title, txt_cleaned)
                row.platform_hint = ugc_hint.get('ugc_hint') if ugc_hint.get('ugc_hint') else 'shore'
                write_hints(row.ugcid, hint_types, hints, sources, source_texts, poss, speciesids, pos_lists, ns)
                SW.lap(); print('make_platform_hints:%s' % SW.pretty_time(SW.event_rate_last))

                #SW.lap()
                #hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint = make_catch_hints(title, txt)
                #was_catch = ugc_hint.get('ugc_hint')
                #write_hints(row.ugcid, hint_types, hints, sources, source_texts, poss, speciesids, pos_lists, ns)
                #SW.lap(); print('make_catch_hints:%s' % SW.pretty_time(SW.event_rate_last))

                #SW.lap()
                #hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, ugc_hint = make_trip_hints(title, txt)
                #if not was_catch:
                #    row.catch_hint = bool(ugc_hint.get('ugc_hint'))
                #else:
                #    row.catch_hint = was_catch
                #row.catch_hint = was_catch
                #write_hints(row.ugcid, hint_types, hints, sources, source_texts, poss, speciesids, pos_lists, ns)
                #SW.lap(); print('make_trip_hints:%s' % SW.pretty_time(SW.event_rate_last))


                row.processed = True
                mmodb.SESSION.flush() #this sends the local changes cached in SQLAlchemy to the open transaction on the SQL Server
                PP.increment(show_time_left=True)

                mmodb.SESSION.commit()
        except Exception as e:
            s = 'Rolling back because of error:\t%s' % e
            log(s, 'both')
            mmodb.SESSION.rollback()


        if len(rows) < window_size:
            break
        window_idx += 1




if __name__ == "__main__":
    main()
