# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''basic functions'''
from nltk.corpus import wordnet as _wordnet
import pattern.en as _pattern
from pattern.en import pluralize, singularize


import funclib.stringslib as _stringslib

#see https://wordnet.princeton.edu/documentation/lexnames5wn
WORDNET_LEXNAMES = ['adj.all', 'adj.pert', 'adv.all', 'noun.tops', 'noun.act', 'noun.animal', 'noun.artifact', 'noun.attribute', 'noun.body', 'noun.cognition', 'noun.communication', 'noun.event', 'noun.feeling', 'noun.food', 'noun.group', 'noun.location', 'noun.motive', 'noun.object', 'noun.person', 'noun.phenomenon', 'noun.plant', 'noun.possession', 'noun.process', 'noun.quantity', 'noun.relation', 'noun.shape', 'noun.state', 'noun.substance', 'noun.time', 'verb.body', 'verb.change', 'verb.cognition', 'verb.communication', 'verb.competition', 'verb.consumption', 'verb.contact', 'verb.creation', 'verb.emotion', 'verb.motion', 'verb.perception', 'verb.possession', 'verb.social', 'verb.stative', 'verb.weather', 'adj.ppl']

class WordnetLexnames():
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

    all_nouns = [noun_tops, noun_act, noun_animal, noun_artifact, noun_attribute, noun_body, noun_cognition, noun_communication, noun_event, noun_feeling, noun_food, noun_group, noun_location, noun_motive, noun_object, noun_person, noun_phenomenon, noun_plant, noun_possession, noun_process, noun_quantity, noun_relation, noun_shape, noun_state, noun_substance, noun_time]
    all_verbs = [verb_body, verb_change, verb_cognition, verb_communication, verb_competition, verb_consumption, verb_contact, verb_creation, verb_emotion, verb_motion, verb_perception, verb_possession, verb_social, verb_stative, verb_weather]
    all_adjectives = [adj_ppl, adj_all, adj_pert, adv_all]



def _clean_list(strlist):
    'basic cleaning'''
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


def similiar(s, lexname='', no_underscored=True, force_plural=False, force_conjugate=False):
    '''(str, str|List, float, bool, bool, bool) -> str
    gets list of similiar/related word versions

    str:word to check
    lexname:restrict synsets which match this lexname, or list of lexnames. See baselib.WordnetLexnames
    no_underscored:some synsets have words with undescores, use this to drop them

    Example:
    >>>similiar('kayak', lexname=WordnetLexnames.adj_all)
    ['kayaked', 'kayaking', 'kayaks', 'kayak']
    '''

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

    final = []
    for Synset in Synsets:
        if Synset.lexname().lower() in WordnetLexnames.all_nouns or force_plural:
            for w in Synset.lemma_names():
                final.append(w)
                _listadd(final, _pattern.pluralize(w))
                _listadd(final, _pattern.singularize(w))
        elif Synset.lexname().lower() in WordnetLexnames.all_verbs or force_conjugate:
                final.append(w)
                _listadd(final, _pattern.lexeme(w))
        else:
                final.append(w)

    if no_underscored:
        final = [w for w in final if not '_' in w]

    return list(set(final))


def _listadd(list_, list_or_val):
    '''extend/append to a list'''
    if isinstance(list_or_val, list):
        list_.extend(list_or_val)
    else:
        list_.append(list_or_val)