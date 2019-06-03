'''run some SQLS to fix common text mistakes'''
import sqlalchemy

import spacy as _sp
Doc = spacy.load('en_core_web_sm')


from warnings import warn


import mmodb
import mmodb.model as model
from mmodb.model import Ugc, UgcHint
from mmo import name_entities as ne
from mmo import settings


from nlp import clean, find

import funclib.iolib as iolib

assert isinstance(mmodb.SESSION, sqlalchemy.orm.Session)

if iolib.wait_key('\n\n%s\nPress "Q" to quit\n' % mmodb.ENGINE) == 'q':
    quit()


class HintTypes():
    platform = 'platform'
    when = 'when'
    species = 'species'
    species_catch = 'species_catch' #actual species catches, will require sentence parsing


class Sources():
    title = 'title'
    post_text = 'post text'



def get_whitelist_words(dump_list):
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
        ne.SESSION.get(add_similiar=True) + \
        ne.Species.get(add_similiar=False, force_plural_singular=True) + \
        ne.TIME(add_similiar=True, force_plural_singular=True)

    if dump_list:
        iolib.pickle(words, settings.PATHS.WHITELIST_WORDS)
    return words


def clean(txt):
    '''clean open text'''
    s = clean.strip_urls_list(s)
    s = clean.base_substitutons(s) #base substitutions would make urls unidentifiable
    s = clean.stop_words(s, get_whitelist_words(False))
    s = replace("'", "")
    s = replace('"', '')
    s = clean.non_breaking_space2space(s)
    s = clean.newline_del_multi(s)
    s = clean.txt2nr(s)
    return s



def make_date_hints(title, post_txt):
    hints = []; source_text = []; sources = []
    dts = find.get_dates(title)
    if dts: date_hint = {'date_hint':dts[0]} #return this to write the best date to ugc table
    sources += [Sources.title] * len(dts)
    hints += dts

    dts = find.get_dates(post_txt)
    if dts and not date_hint: {'date_hint':dts[0]}
    source += ['post body text'] * len(dts)
    hints += dts

    hint_types = [HintTypes.when] * len(hints)
    poss = [None] * len(out_dates)
    speciesids = [None] * len(out_dates)
    ns = [None] * len(out_dates)
    pos_lists = [None] * len(out_dates)
    sources = [None] * len(out_dates)
    return hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, date_hint




def make_platform_hints(title, post_txt):
    '''platform stuff'''
    hints = []; source_texts = [];pos_lists = []; sources = []; ns = []
    platform_hint = {'platform_hint':None}
    def addit(dic, hint, source):
        nonlocal hints, source_texts, pos_lists
        for it in dic.items():
            hints += hint
            source_texts += it[0]
            sources += source
            pos_lists += it[1]
            ns += len(it[1])

    addit(ne.Afloat.indices(title), 'afloat', Sources.title)
    addit(ne.AfloatCharterBoat.indices(title), 'charter', Sources.title)
    addit(ne.AfloatKayak.indices(title), 'kayak', Sources.title)
    addit(ne.AfloatPrivate.indices(title), 'private', Sources.title)

    addit(ne.Afloat.indices(post_txt), 'afloat', Sources.post_text)
    addit(ne.AfloatCharterBoat.indices(post_txt), 'charter', Sources.post_text)
    addit(ne.AfloatKayak.indices(post_txt), 'kayak', Sources.post_text)
    addit(ne.AfloatPrivate.indices(post_txt), 'private', Sources.post_text)


    hints += dts

    dts = find.get_dates(post_txt)
    if dts and not date_hint: {'date_hint':dts[0]}
    source_text += ['post body text'] * len(dts)
    hints += dts

    hint_types = [HintTypes.platform] * len(hints)
    poss = [None] * len(out_dates)
    return hint_types, poss, source_texts, hints, speciesids, pos_lists, ns, sources, platform_hint





def write_hints(ugcid, hint_types, hints, sources=None, source_texts=None, poss=None, speciesids=None, pos_lists=None, ns=None):
    '''write date hints'''
    #hint_type in ('month', 'year', 'day', 'season', 'date', 'published_date')
    #assert len(hint_types) == len(poss) == len(source_texts) == len(hints) == len(speciesids)

    if not n: n = [1] * len(hints)
    for i, hint in enumerate(hints):
        Item = UgcHint()
        Item.ugcid = ugcItem.ugcid
        Item.hint_type = hint_types[i]
        Item.hint = hint[i]

        #now the nullablefields
        if source_texts: Item.source_text = source_texts[i]
        if poss: Item.pos = poss[i]
        if speciesids: Item.speciesid = speciesids[i]
        if pos_list: Item.pos_list = pos_lists[i]
        if sources: Item.source = sources[i]
        if n: Item.n = ns[i]
        mmodb.SESSION.add(Item)



def main():
    cmdline = argparse.ArgumentParser(description=__doc__) #use the module __doc__
    f = lambda s: [str(itme) for item in s.split(',')]
    parser.add_argument('-s', '--slice', help='Record slice, eg -l 0,1000', type=f)

    offset = int(argparse.slice[0])
    max_row = argparse.slice[1]

    n = mmodb.SESSION.query(OsOpenName.os_open_namesid).count()
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
            mmodb.SESSION.query(UgcDateHint).filter(UgcDateHint.ugcid==ugcItem.ugcid).delete()
            txt_post_sql = clean(row.txt_post_sql)
            title = clean(row.title)

            hint_types, poss, source_texts, hints, speciesids, dict_out = date_hints(sentence_pos)
            date_hint = dict['date_hint'] #write this to ugc
            if date_hint:
                    row.date_hint = date_hint
            else:
                    row.date_hint = row.published_date

            write_hints(row.ugcid, sentence, sentence_pos, hint_types, poss, source_texts, hints, speciesids, ns)


            mmodb.SESSION.flush() #this sends the local changes cached in SQLAlchemy to the open transaction on the SQL Server

            PP.increment()

            row.x = res[0][0]
            row.y = res[1][0]

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
    #place holder routine for if we want to actually detect
    #confirmed catches
    raise NotImplementedError
    sentences = Doc(txt_post_sql)
    for sent in sentences:
        sentence_pos = txt_post_sql.index(sent)
