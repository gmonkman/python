# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''basic functions'''
from nltk.corpus import wordnet as _wordnet
import pattern.en as _pattern

import funclib.stringslib as _stringslib

#see https://wordnet.princeton.edu/documentation/lexnames5wn
WORDNET_LEXNAMES = ['adj.all', 'adj.pert', 'adv.all', 'noun.tops', 'noun.act', 'noun.animal', 'noun.artifact', 'noun.attribute', 'noun.body', 'noun.cognition', 'noun.communication', 'noun.event', 'noun.feeling', 'noun.food', 'noun.group', 'noun.location', 'noun.motive', 'noun.object', 'noun.person', 'noun.phenomenon', 'noun.plant', 'noun.possession', 'noun.process', 'noun.quantity', 'noun.relation', 'noun.shape', 'noun.state', 'noun.substance', 'noun.time', 'verb.body', 'verb.change', 'verb.cognition', 'verb.communication', 'verb.competition', 'verb.consumption', 'verb.contact', 'verb.creation', 'verb.emotion', 'verb.motion', 'verb.perception', 'verb.possession', 'verb.social', 'verb.stative', 'verb.weather', 'adj.ppl']


def _clean_list(strlist):
    '''basic cleaning'''
    l = [s.lstrip().rstrip().lower() for s in strlist]
    return list(set(l))


def synonyms(s):
    '''(str)->list
    '''
    if s=='': return ''
    s = s.lstrip().rstrip()
    if s.split(' ')[0] != s: raise ValueError('Argument had multiple words')
    synonyms = []

    for syn in _wordnet.synsets(s):
        for l in syn.lemmas():
            synonyms.append(l.name())
    return _clean_list(synonyms)


def antonyms(s):
    '''(str)->list
    Return list of antonyms
    '''
    if s=='': return ''
    s = s.lstrip().rstrip()
    antonyms = []
    if s.split(' ')[0] != s: raise ValueError('Argument had multiple words')
    synonyms = []

    for syn in _wordnet.synsets(s):
        for l in syn.lemmas():
            if l.antonyms():
                antonyms.append(l.antonyms()[0].name())
    return _clean_list(antonyms)


def similiar(s, lexname=''):
    '''(str, str|List, float) -> str
    gets list of similiar/related word versions'''
    if s=='': return ''
    s = s.lstrip().rstrip()
    SS = _wordnet.synsets(s)

    if lexname and isinstance(lexname, str):
        lexname = [lexname]
    words = []
    lexn = [ss.lower() for ss in lexname]
    if lexn:
        Synsets = [S for S in SS if S.lexname().lower() in lexn]
    else:
        Synsets = SS

    for Synset in Synsets:
        words.extend(Synset.lemma_names())
    final = []
    for w in words:
        final.append(w)
        _listadd(final, _pattern.pluralize(w))
        _listadd(final, _pattern.singularize(w))
        _listadd(final, _pattern.lexeme(w))
    return list(set(final))


def _listadd(list_, list_or_val):
    '''extend/append to a list'''
    if isinstance(list_or_val, list):
        list_.extend(list_or_val)
    else:
        list_.append(list_or_val)