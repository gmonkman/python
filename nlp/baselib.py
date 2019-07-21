# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unreachable
'''basic functions'''
import itertools as _iter
from nltk.corpus import wordnet as _wordnet
from nltk.tokenize import word_tokenize as _word_tokenize
from nltk.corpus.reader.wordnet import Synset as _Synset
import pattern.en as _pattern

import inflect as _inflect
import nlp.relib as _relib
import funclib.stringslib as _stringslib

#see https://wordnet.princeton.edu/documentation/lexnames5wn
WORDNET_LEXNAMES = ['adj.all', 'adj.pert', 'adv.all', 'noun.tops', 'noun.act', 'noun.animal', 'noun.artifact', 'noun.attribute', 'noun.body', 'noun.cognition', 'noun.communication', 'noun.event', 'noun.feeling', 'noun.food', 'noun.group', 'noun.location', 'noun.motive', 'noun.object', 'noun.person', 'noun.phenomenon', 'noun.plant', 'noun.possession', 'noun.process', 'noun.quantity', 'noun.relation', 'noun.shape', 'noun.state', 'noun.substance', 'noun.time', 'verb.body', 'verb.change', 'verb.cognition', 'verb.communication', 'verb.competition', 'verb.consumption', 'verb.contact', 'verb.creation', 'verb.emotion', 'verb.motion', 'verb.perception', 'verb.possession', 'verb.social', 'verb.stative', 'verb.weather', 'adj.ppl']

class WordnetLexnames():
    '''enumeration of wordnet lexnames'''
    adj_all = 'adj.all'
    adj_pert = 'adj.pert'
    adv_all = 'adv.all'
    noun_tops = 'noun.tops'
    noun_act = 'noun.act'
    noun_animal = 'noun.animal'
    noun_artifact = 'noun.artifact'
    noun_attribute = 'noun.attribute'
    noun_body = 'noun.body'
    noun_cognition = 'noun.cognition'
    noun_communication = 'noun.communication'
    noun_event = 'noun.event'
    noun_feeling = 'noun.feeling'
    noun_food = 'noun.food'
    noun_group = 'noun.group'
    noun_location = 'noun.location'
    noun_motive = 'noun.motive'
    noun_object = 'noun.object'
    noun_person = 'noun.person'
    noun_phenomenon = 'noun.phenomenon'
    noun_plant = 'noun.plant'
    noun_possession = 'noun.possession'
    noun_process = 'noun.process'
    noun_quantity = 'noun.quantity'
    noun_relation = 'noun.relation'
    noun_shape = 'noun.shape'
    noun_state = 'noun.state'
    noun_substance = 'noun.substance'
    noun_time = 'noun.time'
    verb_body = 'verb.body'
    verb_change = 'verb.change'
    verb_cognition = 'verb.cognition'
    verb_communication = 'verb.communication'
    verb_competition = 'verb.competition'
    verb_consumption = 'verb.consumption'
    verb_contact = 'verb.contact'
    verb_creation = 'verb.creation'
    verb_emotion = 'verb.emotion'
    verb_motion = 'verb.motion'
    verb_perception = 'verb.perception'
    verb_possession = 'verb.possession'
    verb_social = 'verb.social'
    verb_stative = 'verb.stative'
    verb_weather = 'verb.weather'
    adj_ppl = 'adj.ppl'

    all_nouns = set([noun_tops, noun_act, noun_animal, noun_artifact, noun_attribute, noun_body, noun_cognition, noun_communication, noun_event, noun_feeling, noun_food, noun_group, noun_location, noun_motive, noun_object, noun_person, noun_phenomenon, noun_plant, noun_possession, noun_process, noun_quantity, noun_relation, noun_shape, noun_state, noun_substance, noun_time])
    all_verbs = set([verb_body, verb_change, verb_cognition, verb_communication, verb_competition, verb_consumption, verb_contact, verb_creation, verb_emotion, verb_motion, verb_perception, verb_possession, verb_social, verb_stative, verb_weather])
    all_adjectives = set([adj_ppl, adj_all, adj_pert, adv_all])
    all = set(list(all_nouns) + list(all_verbs) + list(all_adjectives))


#region helpers
def _clean(s):
    s = s.replace(' ', '')
    return _stringslib.filter_alphanumeric1(s, strict=True, allow_cr=False, allow_lf=False, remove_double_quote=True, remove_single_quote=True)

def _fixitr(s, type_=list, tolower=True):
    if not s: return s
    was_string = True if isinstance(s, str) else False
    if isinstance(s, (str, int, float, _Synset)):
        s = type_(s)
    if tolower and was_string:
        s = [w.lower() for w in s]
    return type_(s)

def _listadd(list_, list_or_val):
    '''extend/append to a list'''
    if not list_or_val: return
    if isinstance(list_or_val, list):
        list_.extend(list_or_val)
    else:
        list_.append(list_or_val)

def _clean_list(strlist):
    'basic cleaning'''
    l = [s.lstrip().rstrip().lower() for s in strlist]
    return list(set(l))
#endregion



def plural_sing(word):
    '''(str) -> list
    add plural or singular forms returning
    a list including <word>'''
    if not word: return ''
    word = word.lstrip().rstrip()
    final = []
    final.append(word)
    _listadd(final, _inflect.engine().plural(word))
    _listadd(final, _inflect.engine().singular_noun(word))
    return final


def conjugate(word):
    '''(str) -> list
    conjugate word'''
    if not word: return ''
    word = word.lstrip().rstrip()
    return _pattern.lexeme(word)


def synonym_lemma_bag(s):
    '''(str)->list
    Get synonyms for all lemmas which match s.

    Note this can cross 'meaning' boundaries.
    '''
    if s == '': return ''
    s = _clean(s)
    if s.split(' ')[0] != s: raise ValueError('Argument had multiple words')
    synonyms = []

    for syn in _wordnet.synsets(s):
        for l in syn.lemmas():
            synonyms.append(l.name())
    return _clean_list(synonyms)


def antonym_lemma_bag(s):
    '''(str)->list
    Return list of antonyms
    '''
    if s == '': return ''
    s = _clean(s)
    antonyms = []
    if s.split(' ')[0] != s: raise ValueError('Argument had multiple words')
    for syn in _wordnet.synsets(s):
        for l in syn.lemmas():
            if l.antonyms():
                antonyms.append(l.antonyms()[0].name())
    return _clean_list(antonyms)


def lemma_bag_all(word, lexname='', no_underscored=True, force_plural=False, force_conjugate=False):
    '''(str, str|List, float, bool, bool, bool) -> str
    gets list of all lemmas and their conjugates, synonyms
    and plurals of s

    This crosses "meaning" boundaries.

    str:word to check
    lexname:restrict synsets which match this lexname, or list of lexnames. See baselib.WordnetLexnames
    no_underscored:some synsets have words with undescores, use this to drop them

    Example:
    >>>lemma_bag_all('kayak', lexname=WordnetLexnames.adj_all)
    ['kayaked', 'kayaking', 'kayaks', 'kayak']
    '''

    if not word: return ''
    word = word.lstrip().rstrip()
    SS = _wordnet.synsets(word)

    if lexname and isinstance(lexname, str):
        lexname = [lexname]

    lexn = [ss.lower() for ss in lexname]
    if lexn:
        Synsets = [S for S in SS if S.lexname().lower() in lexn]
    else:
        Synsets = SS

    final = []
    for Synset in Synsets:
        if Synset.lexname().lower() in WordnetLexnames.all_nouns or force_plural:
            for w in Synset.lemma_names():
                final.append(w)
                _listadd(final, _inflect.engine().plural(w))
                _listadd(final, _inflect.engine().singular_noun(w))
        elif Synset.lexname().lower() in WordnetLexnames.all_verbs or force_conjugate:
            for w in Synset.lemma_names():
                final.append(w)
            _listadd(final, _pattern.lexeme(w))
        else:
            final.append(w)

    if no_underscored:
        final = [w for w in final if not '_' in w]

    return list(set(final))


#TODO allow depth to be set - need to write a recursion
def common_meaning_bag(word, lexname_in=(), hyper_in=(), hypo_in=(), pos=('a', 'n', 'v'), search_nr_synsets=(), dist_threshs=(), sim_threshs=0, no_underscored=True, force_plural=False, force_conjugate=False, clean=False):
    '''(str, iter|str, iter|str, iter|str, iter|str, iter:synsets, iter:int, bool, bool, bool) -> list
    gets list of similiar/related words, their conjugates and plurals

    Currently fixed to a depth of 1

    str:word to check
    lexname:restrict synsets which match this lexname, or list of lexnames. See baselib.WordnetLexnames
    no_underscored:some synsets have words with undescores, use this to drop them
    hyper_in, hypo_in:
    Example:
    >>>similiar('kayak', lexname=WordnetLexnames.adj_all)
    ['kayaked', 'kayaking', 'kayaks', 'kayak']

    Also see test_baselib.py for more examples
    '''
    if clean: s = _clean(s)
    SS = _wordnet.synsets(word)
    if not lexname_in: lexname_in = WordnetLexnames.all
    lexname_in = [ss.lower() for ss in _fixitr(lexname_in, tuple)]
    hyper_in = _fixitr(hyper_in, tuple)
    hypo_in = _fixitr(hypo_in)
    pos = _fixitr(pos, tuple)
    dist_threshs = _fixitr(dist_threshs, tuple)


    #we filter the candiates
    Synsets = filter_synsets(SS, pos=pos, lexname_in=lexname_in, dist_synsets=search_nr_synsets, dist_threshs=dist_threshs, sim_threshs=sim_threshs)

    AllS = []
    AllS += [S.hyponyms for S in Synsets]
    AllS += [S.hypernyms for S in Synsets]
    AllS = filter_synsets(AllS, pos=pos, lexname_in=lexname_in, dist_synsets=search_nr_synsets, dist_threshs=dist_threshs, sim_threshs=sim_threshs)

    final = []
    for Synset in AllS:
        if Synset.lexname().lower() in WordnetLexnames.all_nouns or force_plural:
            w = Synset.lemma_names()[0]
            final.append(w)
            _listadd(final, _inflect.engine().plural(w))
            _listadd(final, _inflect.engine().singular_noun(w))
        elif Synset.lexname().lower() in WordnetLexnames.all_verbs or force_conjugate:
            final.append(w)
            _listadd(final, _pattern.lexeme(w))
        else:
            final.append(w)

    if no_underscored:
        final = [w for w in final if not '_' in w]

    return list(set(final))



def filter_synsets(Synsets, pos=('a', 'n', 'v'), lexname_in=WordnetLexnames.all, dist_synsets=(), dist_threshs=(), sim_threshs=()):
    '''(list:SynSet, iter:str, iter:str, float, iter:Synset, iter:int, iter:float) -> List:Synsets
    filter synsets

    synsets: synset list to filter
    pos: iterable of matching pos strings, i.e. n:noun, v:verb, a:adjective
    lexname_in: filter on the lexname, e.g. noun.plant, use WordnetLexnames for recognise strings
    similarity_thresh:similarty threshold between 0 and 1, keeps >= similarity_thresh
    dist,dist_synset: only keep synsets which are dist or less "hops" from dist_synset, accepts
                        singular values of lists, where dist_synset[n] uses distance dists[n]

    Returns: filtered list of synsets

    Example:
    >>>filter_synsets([wordnet.synset('bicycle.n.01'),
    '''
    pos = _fixitr(pos)
    dist_synsets = _fixitr(dist_synsets)
    dist_threshs = _fixitr(dist_threshs)
    sim_threshs = _fixitr(sim_threshs)

    SS = [S for S in [S for S in Synsets if S.pos in pos] if S.lexname in lexname_in]

    # loop through each synset against which we wish to check path distance and similarity
    # rebuilding list with synsets which meet the criteria
    for n, dS in enumerate(dist_synsets):
        SS = [S for S in [S for S in SS if SS.shortest_path_distance(dS) <= dist_threshs[n]] if S.path_similarity(dS) >= sim_threshs[n]]
    return list(set(filter_synsets))





def prettyprint_synset(words, printit=True, pos=('a', 'n', 'v'), lexname_in=(), dist_synsets=(), dist_threshs=(), sim_threshs=()):
    '''str|iter->str
    words can be fully defined, e.g. 'cycle.n.01'

    See func filter_synsets for arguments

    print synset details for words'''
    SS = []
    if not lexname_in: lexname_in = WordnetLexnames.all
    for word in words:
        if '.' in word:
            SS += _wordnet.synset(word)
        else:
            SS += [S for S in _wordnet.synsets(word)]

    SS = filter_synsets(SS, pos=pos, lexname_in=lexname_in, dist_synsets=dist_synsets, dist_threshs=dist_threshs, sim_threshs=sim_threshs)
    bld = []
    iif = lambda s: s if s else ''
    for S in SS:
        bld += 'Name: %s' % iif(', '.join(S.lemma_names()[0]))
        bld += 'Lemmas: %s' % iif(', '.join(S.lemma_names()[1:]))
        bld += 'Lexname: %s' % iif(S.lexname())
        bld += 'Definition: %s' % iif(S.definition())
        bld += 'Examples: %s' % iif(S.examples())
        bld += '\n--------------------'
    txt = '\n'.join(bld)
    print(txt)
    return txt


def expansions(words, expansion_words):
    '''(iter|str, dic) -> dic
    add words based on alternate spellings provided in
    the expansion_words dictionary

    Returns original words as well
    Example:
    >>>expansion(['North Point', 'South Point'], {'Point':['End', 'Spit']})
    ['North Point', 'South Point', 'North End, 'North Spit', 'South End', 'South Spit']
    '''
    words = _fixitr(words)
    assert isinstance(expansion_words, dict)
    assert isinstance(words, list)
    out = list(words)

    for word in words:
        for key, word_list in expansion_words.items():
            if not key in word: continue

            for w in word_list:
                w = _relib.replace_whole_word(word, key, w)
                if not w: continue
                out += w
    return out


def conjugations(word_list, lexname_list, exclude=()):
    '''(iterable, iterable|str, iterable|str ) -> list
    Get original list and add conjugations (for verbs)

    word_list:iterable of of words

    '''
    if isinstance(exclude, str):
        exclude = (exclude, )

    out = []
    for w in word_list:
        out.extend(lemma_bag_all(w, lexname_list))

    for e in exclude:
        out.remove(e)

    return list(set(out))


def typos(wordlist, dist=1, exclude=()):
    '''(iterable, list) -> list
    Get original list and add typos for QWERTY

    word_list:iterable of of words
    l:keyboard distance, recommend 1
    exclude:words in this list will be excluded (can also be a str)

    Example:
    >>>typos(['kayak', 'moken'])
    [
    '''
    if isinstance(exclude, str):
        exclude = (exclude, )

    out = []
    out.extend(_typo.typos(wordlist, dist, exclude))
    return out


#TODO finish this, idea is to recusively generate to depth=depth
def genhyper(synset, depth=2):
    '''to generate'''
    raise NotImplementedError
    assert isinstance(synset, _wordnet.Synset), 'Expected a synset'
    if depth == 0:
        print('done')
        return

    



class SlidingWindow():
    '''Generate dict of text with
    the windows windows.

    Leafs (word itearables) are sets
    
    Example:
    >>>SlidingWindow('one two three four five', (2,3))
    {2: {'one two', 'two three', 'three four', 'four five'},
    3: {'one two three', 'three four five'}}
    '''
    def __init__(self, s, windows=(1,2,3)):
        winds = {}
        for sz in windows:
            winds[sz] = set()

        self._s = s
        self.tokenized = _word_tokenize(self._s)


        for sz in windows:
            for x in range(0, len(self.tokenized) - sz + 1):
                winds[sz] |= set([' '.join(self.tokenized[x:x + sz])])
            
        self.windowed = winds
 

    def get(self):
        '''return it'''
        return self.windowed

