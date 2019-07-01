# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, attribute-defined-outside-init

'''doc'''
####################################################################################
### If new classes are added here, we must add to write_hints._get_white_list_words#
####################################################################################

##################################################################################
# if add another UNSPECIFIED class, update mmo.write_hints.py:make_species_hints #
##################################################################################

import os.path as _path
import funclib.stringslib as _stringslib

from funclib.baselib import list_flatten as _flat
import gazetteerdb.gaz as _gaz
from mmodb import species as _species
from nlp import baselib as _nlpbase
from nlp import typo as _typo
from nlp import relib as _relib
import funclib.iolib as _iolib
import mmo.settings as _settings



all_ = set()
all_single = set()


class Substitutions():
    '''known substitutions used to expand the gazetteer'''
    scars = ['scar', 'scars', 'skier', 'skiers', 'skeer', 'skeers']
    docks = ['dock', 'docks']
    beach = ['beach', 'sand', 'sands']
    prom = ['prom', 'promenade', 'esplanade']
    breakwater = ['breakwater', 'breaky', 'breakey', 'breakie']
    marsh = ['marsh', 'marshes', 'marshs']
    rock = ['rock', 'rocks']
    ledge = ['ledge', 'ledges']
    platform = ['platform', 'platforms']
    jetty = ['jetty', 'quay']
    headland = ['headland', 'promontory', 'ness']




class UnspecifiedKeys():
    '''dictionary keys for unspecified
    dicts. for convieniance'''
    blenny = 'blenny (unspecified)'
    bream = 'bream (unspecified)'
    eel = 'eel (unspecified)'
    flatfish = 'flatfish (unspecified)'
    goby = 'goby (unspecified)'
    gurnard = 'gurnard (unspecified)'
    mullet = 'mullet (unspecified)'
    pipefish = 'pipefish (unspecified)'
    rockling = 'rockling (unspecified)'
    sand_eel = 'sand eel (unspecified)'
    sea_scorpion = 'sea scorpion (unspecified)'
    shad = 'shad (unspecified)'
    skate_ray = 'skate/ray (unspecified)'
    sole = 'sole (unspecified)'
    squid = 'squid (unspecified)'
    sturgeon = 'sturgeon (unspecified)'
    weeverfish = 'weeverfish (unspecified)'
    wrasse = 'wrasse (unspecified)'


#region helper funcs
def _clean(lst):
    '''clean list'''
    return  [_stringslib.filter_alphanumeric1(s, strict=True, remove_double_quote=True, remove_single_quote=True).lower() for s in lst]

def _fixiter(v, type_=list):
    '''fx'''
    if isinstance(v, (float, int, str)):
        return type_(v)
    return v

def _get_season(month_key):
    '''given a month get the season'''
    if month_key in ['december', 'january', 'february']: return 'winter'
    if month_key in ['march', 'april', 'may']: return 'spring'
    if month_key in ['june', 'july', 'august']: return 'summer'
    return 'autumn'
#endregion

TYPOS_MIN_LENGTH = 5
TYPOS_FIX_FIRST_N_CHARS = 2
TYPO_OPTIONS_ALL = set(('nouns_common', 'nouns_proper', 'verbs', 'phrases', 'adjectives')) #these match the allowed word types in NEBLists, they arnt relevant for the dict classes because they are all nouns

#also see spreadsheet sources_master.xlsx
FORUM_IFCA = {'sea fishing and venue questions': ['north west'],
                'north-west-fishing-reports': ['north west'],
                'humber estuary': ['north east', 'eastern'], 
                'north east catch reports': ['north east', 'northumberland'],
                'easy access venues/directions for all areas': ['north west'],
                'thames estuary': ['kent and essex', 'eastern'],
                'tsf sea fishing': ['cornwall', 'devon and severn', 'eastern', 'isles of scilly', 'kent and essex', 'north east', 'north west', 'northumberland', 'southern', 'sussex'],
                'isle of wight': ['southern'],
                'south west coast': ['devon and severn', 'cornwall', 'isles of scilly'],
                'east-coast-sea-fishing-reports': ['eastern', 'kent and essex'],
                'dorset fishing': ['southern'],
                'east coast catch reports': ['eastern', 'kent and essex'],
                'south-west-sea-fishing-reports': ['devon and severn', 'cornwall', 'isles of scilly'],
                'south-east-sea-fishing-reports': ['sussex', 'eastern'],
                'east coast': ['eastern', 'north east', 'northumberland'],
                'cornwall fishing': ['cornwall'],
                'north west coast': ['north west'],
                'north east coast': ['north east', 'northumberland'],
                'south east coast': ['sussex', 'kent and essex', 'eastern'],
                'beach talk': ['southern', 'cornwall', 'devon and severn'],
                'south east catch reports': ['sussex', 'kent and essex'],
                'south-coast-sea-fishing-reports': ['sussex', 'southern'],
                'south coast & ci catch reports': ['southern', 'sussex'], 
                'south west catch reports': ['southern', 'devon and severn', 'cornwall', 'isles of scilly'],
                'fishing session reports': ['north west'],
                'north west & the isle of man catch reports': ['north west'],
                'somerset fishing': ['devon and severn'],
                'devon fishing': ['devon and severn'],
                'north-east-sea-fishing-reports': ['north east', 'northumberland'],
                'merseyside/fylde coast/cumbrian venues/directions': ['north west'],
                'sea fishing': ['cornwall', 'devon and severn', 'eastern', 'isles of scilly', 'kent and essex', 'north east', 'north west', 'northumberland', 'southern', 'sussex'],
                'west coast': ['cornwall', 'devon and severn'],
                'where-to-sea-fish': ['cornwall', 'devon and severn', 'eastern', 'isles of scilly', 'kent and essex', 'north east', 'north west', 'northumberland', 'southern', 'sussex'],
                'shore catch reports nesa': ['north east', 'northumberland'],
                'shore fishing nesa': ['north east', 'northumberland'],
                'boat catch reports nesa': ['north east', 'northumberland'],
                'lure fishing nesa': ['north east', 'northumberland'],
                'lure catch reports nesa': ['north east', 'northumberland'],
                'boat fishing nesa': ['north east', 'northumberland'],
                'shore fishing missed nesa': ['north east', 'northumberland'],
                'boat angling / angling afloat': ['cornwall', 'devon and severn', 'eastern', 'isles of scilly', 'kent and essex', 'north east', 'north west', 'northumberland', 'southern', 'sussex'],
                'kayak angling forum': ['cornwall', 'devon and severn', 'eastern', 'isles of scilly', 'kent and essex', 'north east', 'north west', 'northumberland', 'southern', 'sussex'],
                'kayak fishing reports': ['north east', 'north west', 'northumberland'],
                'boat fishing reports': ['north east', 'north west', 'northumberland'],
                'boat talk': ['cornwall', 'devon and severn', 'southern'],
                'general boat fishing talk': ['cornwall', 'devon and severn', 'southern'],
                'fishing kayaks': ['cornwall', 'devon and severn', 'southern'],
                'kayak fishing': ['cornwall', 'devon and severn', 'eastern', 'isles of scilly', 'kent and essex', 'north east', 'north west', 'northumberland', 'southern', 'sussex'],
                'kayak': ['cornwall', 'devon and severn', 'eastern', 'isles of scilly', 'kent and essex', 'north east', 'north west', 'northumberland', 'southern', 'sussex'],
                'boat owners forum': ['cornwall', 'devon and severn', 'eastern', 'isles of scilly', 'kent and essex', 'north east', 'north west', 'northumberland', 'southern', 'sussex'],
                'south coast': ['southern', 'sussex'], 'whitby, holderness & the humber catch reports': ['north east', 'eastern']}

IFCAS = {'cornwall', 'devon and severn', 'eastern', 'isles of scilly', 'kent and essex', 'north east', 'north west', 'northumberland', 'southern', 'sussex'}




class Typos():
    '''This are for the 
    list handler. The dict
    based stuff accepts true or false'''
    phrases = 'phrases'
    verbs = 'verbs'
    nouns_proper = 'nouns_proper'
    nouns_common = 'nouns_common'
    adjectives = 'adjectives'


class GazetteerWords():
    '''gaz words'''
    #from  ifca_area_wgs84
    VALID_IFCAS = ['cornwall', 'devon and severn', 'eastern', 'isles of scilly', 'kent and essex', 'north east', 'north west', 'northumberland', 'southern', 'sussex']
    #from counties_wgs84
    VALID_COUNTIES = ['barking and dagenham', 'bath and north east somerset', 'bedfordshire', 'berkshire', 'bexley', 'blackburn with darwen', 'bournemouth', 'brent', 'brighton and hove', 'bristol', 'bromley', 'buckinghamshire', 'cambridgeshire', 'camden', 'cheshire', 'cornwall', 'croydon', 'cumbria', 'darlington', 'derby', 'derbyshire', 'devon', 'dorset', 'durham', 'ealing', 'east riding of yorkshire', 'east sussex', 'enfield', 'essex', 'gloucestershire', 'greenwich', 'hackney', 'halton', 'hammersmith and fulham', 'hampshire', 'haringey', 'harrow', 'hartlepool', 'havering', 'herefordshire', 'hertfordshire', 'hillingdon', 'hounslow', 'isle of wight', 'islington', 'kensington and chelsea', 'kent', 'kingston upon hull', 'kingston upon thames', 'lambeth', 'lancashire', 'leicester', 'leicestershire', 'lewisham', 'lincolnshire', 'london', 'luton', 'manchester', 'medway', 'merseyside', 'merton', 'middlesbrough', 'milton keynes', 'newham', 'norfolk', 'north east lincolnshire', 'north lincolnshire', 'north somerset', 'north yorkshire', 'northamptonshire', 'northumberland', 'nottingham', 'nottinghamshire', 'oxfordshire', 'peterborough', 'plymouth', 'poole', 'portsmouth', 'redbridge', 'redcar and cleveland', 'richmond upon thames', 'rutland', 'shropshire', 'somerset', 'south gloucestershire', 'south yorkshire', 'southampton', 'southend-on-sea', 'southwark', 'staffordshire', 'stockton-on-tees', 'stoke-on-trent', 'suffolk', 'surrey', 'sutton', 'swindon', 'telford and wrekin', 'thurrock', 'torbay', 'tower hamlets', 'tyne and wear', 'waltham forest', 'wandsworth', 'warrington', 'warwickshire', 'west midlands', 'west sussex', 'west yorkshire', 'westminster', 'wiltshire', 'worcestershire', 'york', 'antrim', 'ards', 'armagh', 'ballymena', 'ballymoney', 'banbridge', 'belfast', 'carrickfergus', 'castlereagh', 'coleraine', 'cookstown', 'craigavon', 'derry', 'down', 'dungannon', 'fermanagh', 'larne', 'limavady', 'lisburn', 'magherafelt', 'moyle', 'newry and mourne', 'newtownabbey', 'north down', 'omagh', 'strabane', 'aberdeen', 'aberdeenshire', 'angus', 'argyll and bute', 'clackmannanshire', 'dumfries and galloway', 'dundee', 'east ayrshire', 'east dunbartonshire', 'east lothian', 'east renfrewshire', 'edinburgh', 'eilean siar', 'falkirk', 'fife', 'glasgow', 'highland', 'inverclyde', 'midlothian', 'moray', 'north ayshire', 'north lanarkshire', 'orkney islands', 'perthshire and kinross', 'renfrewshire', 'scottish borders', 'shetland islands', 'south ayrshire', 'south lanarkshire', 'stirling', 'west dunbartonshire', 'west lothian', 'anglesey', 'blaenau gwent', 'bridgend', 'caerphilly', 'cardiff', 'carmarthenshire', 'ceredigion', 'conwy', 'denbighshire', 'flintshire', 'gwynedd', 'merthyr tydfil', 'monmouthshire', 'neath port talbot', 'newport', 'pembrokeshire', 'powys', 'rhondda, cynon, taff', 'swansea', 'torfaen', 'vale of glamorgan', 'wrexham']
    #from counties_wgs84
    UK_COUNTRIES = ['england', 'northern ireland', 'scotland', 'wales']



class GroupsForUnspecified():
    '''these are used to determine if we have found a specifc species
    in write hints.py, if we have not, we then look for group terms'''
    SOLE_SPECIFIED_KEYS = set(_clean(['Dover Sole', 'Lemon Sole', 'Sand Sole']))
    SKATE_RAY_SPECIFIED_KEYS = set(_clean(['Common Stingray', 'Ray (Blonde)', 'Ray (Cuckoo)', 'Ray (Eagle)', 'Ray (Electric)', 'Ray (Marbled-Electric)', 'Ray (Sandy)', 'Ray (Shagreen)', 'Ray (Small Eyed)', 'Ray (Spotted)', 'Ray (Starry)', 'Ray (Thornback)', 'Ray (Undulate)']))
    BREAM_SPECIFIED_KEYS = set(_clean(["Black Bream", "Couch's Seabream", "Gilthead Sea Bream", "Pandora Sea Bream", "Ray's Bream", "Red Sea Bream", "White Sea Bream"]))
    MULLET_SPECIFIED_KEYS = set(_clean(["Golden-Grey Mullet", "Red Mullet", "Thick Lipped Grey Mullet", "Thin Lipped Grey Mullet"]))
    FLATFISH_SPECIFIED_KEYS = set(_clean(['Brill', 'Dab', 'Dover Sole', 'Flounder', 'Lemon Sole', 'Long Rough Dab', 'Megrim', 'Plaice', 'Sand Sole', 'Topknot', 'Turbot', 'Witch']))


#region LISTS HANDLER
class _NamedEntityBase():
    '''base class for named entities
    This handles the automated extending of word lists
    from the subclassing class according to variable naming
    ie. do variable names contain noun verb etc

    common nouns are pluralised
    verbs are conjugated
    typos are generated for all word types, according to typos argument
    '''

    def __init__(self):
        '''init'''
        self.allwords = set()
        self.all_base_words = set()
        self.all_base_words |= self.nouns_common
        self.all_base_words |= self.nouns_proper
        self.all_base_words |= self.verbs
        self.all_base_words |= self.adjectives
        self.all_base_words |= self.phrases
        self._get()
        
    

    def _get(self):

        if self._dump_load():
            assert self.allwords, 'allwords loaded from file system, but it is empty'
            print('Loaded words for %s from file' % self.dump_name)
            return

        print('Getting typos for %s' % self.dump_name)
        nouns_proper = set(self.nouns_proper); verbs = set(self.verbs); phrases = set(self.phrases); nouns_common = set(self.nouns_common); adjectives = set(self.adjectives)
        if self.typos: #typos can be none
            if isinstance(self.typos, str): self.typos = (self.typos,)
            assert set(self.typos).issubset(TYPO_OPTIONS_ALL), 'Invalid typos options. Typos must be in %s. Check subclass initialisation.' % TYPO_OPTIONS_ALL
        nouns_proper = set(self.nouns_proper)

        if self.add_similiar:
            wds = []
            for w in self.nouns_common:
                wds.append(w)
                wds.extend(_nlpbase.lemma_bag_all(w, force_plural=True))
            nouns_common |= set(wds)

            wds = []
            for w in verbs:
                wds.append(w)
                wds.extend(_nlpbase.lemma_bag_all(w)) #lamma_bag_all obeys verb and nouns plural/conjugation by default
            verbs |= set(wds)
        if self.typos:
            if 'phrases' in self.typos: phrases |= set(_typo.typos(phrases, filter_start_n=TYPOS_FIX_FIRST_N_CHARS, min_length=TYPOS_MIN_LENGTH))
            if 'verbs' in self.typos: verbs |= set(_typo.typos(verbs, filter_start_n=TYPOS_FIX_FIRST_N_CHARS, min_length=TYPOS_MIN_LENGTH))
            if 'nouns_proper' in self.typos: nouns_proper |= set(_typo.typos(nouns_proper, filter_start_n=TYPOS_FIX_FIRST_N_CHARS, min_length=TYPOS_MIN_LENGTH))
            if 'nouns_common' in self.typos: nouns_common |= set(_typo.typos(nouns_common, filter_start_n=TYPOS_FIX_FIRST_N_CHARS, min_length=TYPOS_MIN_LENGTH))
            if 'adjectives' in self.typos: adjectives |= set(_typo.typos(adjectives, filter_start_n=TYPOS_FIX_FIRST_N_CHARS, min_length=TYPOS_MIN_LENGTH))
        self.allwords |= nouns_proper 
        self.allwords |= verbs
        self.allwords |= phrases 
        self.allwords |= nouns_common 
        self.allwords |= adjectives
        try:
            self._dump_dump()
            print('Dumped allwords for %s' % self.dump_name) 
        except Exception as _:
            print('allwords created, but dump failed for %s' % self.dump_name)


    def _dump_get_name(self, varname):
        fname = '%s_%s.pkl' % (self.dump_name, varname)
        return _path.normpath(_path.join(_settings.PATHS.NAMED_ENTITIES_DUMP_FOLDER, fname))


    def _dump_load(self):
        try:
            self.allwords = _iolib.unpickle(self._dump_get_name('allwords'))
            if not self.allwords:
                self.allwords = set()
                return False
            return True
        except Exception as _:
            return False

    def _dump_dump(self):
        s = self._dump_get_name('allwords')
        _iolib.pickle(self.allwords, s)


    def indices(self, s, use_proper=False):
        '''(str, bool) -> dict
        returns a dictionary with the word frequencies
        found in str for all words in the class

        s: the text to search
        use_proper: use the original word set, not the set with typos etc.

        Example:
        >>>instr('the black black fox is grey')
        {'black':[1]}
        '''
        
        out = {}
        if not s: return out
        if use_proper:
            words = self.all_base_words
        else:
            words = self.allwords

        for word in words:
            inds = _relib.get_indices(s, word)
            if inds:
                out[word] = inds
        return out


    def lookup(self, s):
        '''simple lookup for word s'''
        m = []
        if s in self.nouns_common: m += ['nouns_common']
        if s in self.nouns_common: m += ['nouns_proper']
        if s in self.nouns_common: m += ['verb']
        if s in self.nouns_common: m += ['adjective']
        if s in self.nouns_common: m += ['phrase']
        if s in self.all_words: m += ['phrase']
        print(' '.join(s))
                



class NEBLists(_NamedEntityBase):
    '''Create an list of words based on kwarg options

    Supported kwargs are:
    add_similiar=False
    force_conjugate=False
    typos=('nouns', 'verbs', 'phrases', 'others')
    force_plural_singular=False
    '''
    def __init__(self, dump_name, nouns_proper=None, nouns_common=None, verbs=None, phrases=None, adjectives=None, add_similiar=False, typos=('nouns_common', 'nouns_proper', 'verbs', 'phrases', 'adjectives')):
        ld = lambda v: set(v) if v else set()
        self.nouns_common = ld(nouns_common)
        self.nouns_proper = ld(nouns_proper)
        self.dump_name = dump_name
        self.verbs = ld(verbs)
        self.phrases = ld(phrases)
        self.adjectives = ld(adjectives)
        self.add_similiar = add_similiar
        self.typos = typos
        super().__init__()
#endregion






#region DICT HANDLER

class _NamedEntityBaseDict():

    def __init__(self):
        self._setdic()

    
    def _setdic(self):
        '''Sets self.noun_dict_all by generating
        typos and plurals using noun_dict, where
        noun_dict is set by the inheriting class
        '''
        assert isinstance(self.nouns_dict, dict), 'nouns_dict was not a dict in %s' % self.dump_name
        assert self.nouns_dict, 'nouns_dict was empty in %s' % self.dump_name
        if self._dump_load():
            assert self.nouns_dict_all, 'noun_dicts_all loaded, but was empty for %s' % self.dump_name
            print('Loaded noun_dicts_all for %s' % self.dump_name)
            return

        self.nouns_dict_all = {} #explicit
        print('Generating words for %s' % self.dump_name)
        for key, key_words in self.nouns_dict.items():  #speciesid is the proper name, it should also be in words as the alias includes the proper name
            assert key_words, 'noun_dict %s was empty' % key
            wds = []            
            for w in key_words:
                if 'unspecified' in w: continue #TODO temporary kludge to exclude unspecified
                wds += _nlpbase.plural_sing(w)

            if self.typos:
                wds += _typo.typos(wds, filter_start_n=TYPOS_FIX_FIRST_N_CHARS, min_length=TYPOS_MIN_LENGTH)

            self.nouns_dict_all[key] = set(wds)

        try:
            self._dump_dump()
            print('Dumped nouns_dict_all for %s' % self.dump_name) 
        except Exception as _:
            print('nouns_dict_all created, but dump failed for %s' % self.dump_name)
                    

    def _dump_get_name(self, varname):
        fname = '%s_%s.pkl' % (self.dump_name, varname)
        return _path.normpath(_path.join(_settings.PATHS.NAMED_ENTITIES_DUMP_FOLDER, fname))


    def _dump_load(self):
        try:
            self.nouns_dict_all = _iolib.unpickle(self._dump_get_name('nouns_dict_all'))
            if not self.nouns_dict_all:
                self.nouns_dict_all = set()
                return False
            return True
        except Exception as _:
            return False

    def _dump_dump(self):
        s = self._dump_get_name('nouns_dict_all')
        _iolib.pickle(self.nouns_dict_all, s)


    def indices(self, s, keyid):
        '''(str, str)

        check if any verson exists in keyid
        returns a dictionary with the word frequencies
        found in str which are in the class

        kwargs are passed to the base get function and are:
        add_similiar:bool
        force_conjugate:bool
        typos=('nouns', 'verbs', 'phrases', 'others')
        force_plural_singular:bool
        as_set:bool

        Example:
        >>>indices('the black black fox is grey')
        {'black':[5,11]}
        '''
        out = {}
        words = self.nouns_dict_all.get(keyid)
        assert words, 'nouns_dict_all had no items for key %s' % keyid
        for word in words:
            inds = _relib.get_indices(s, word)
            if inds:
                out[word] = inds
        return out


    def get_by_key(self, key, use_proper=False):
        '''this gets a list of values for the dict key key,
        where key identifies the groups, eg the key may be
        speciesid

        key: dictionary key text identifying all versions of a word, eg they dictionary key
        'bass', which contains different words for bass. {'bass':['silver', 'bass', 'schoolie' ..]}
        use_proper: use the list without typos and plurals, otherwise uses 
        '''
        assert self.nouns_dict, 'nouns_dict was empty'
        assert self.nouns_dict_all, 'nouns_dict was empty'
        if use_proper:
            words = self.nouns_dict[key]
        else:
            words = self.nouns_dict_all[key]
        return set(words)


    def get_flat_set(self):
        '''() -> set
        Gets a set of all words.
        This is used as a whitelist filter for stopwords
        '''
        assert self.nouns_dict_all, 'self.all was accessed, but self.all was empty.'
        a = _flat([list(x) for x in self.nouns_dict_all.values()])
        return set(a)

    
    def lookup(self, s):
        '''simple lookup for words'''
        m = []

        for k, it in self.nouns_dict_all():
            if s in it: m += [k]
        if m:
            print(' '.join(m))
                




class NEBDicts(_NamedEntityBaseDict):
    '''class to hand dicts of words
    '''

    def __init__(self, nouns_dict, dump_name, typos=True):
        self.nouns_dict = nouns_dict
        assert isinstance(nouns_dict, dict), 'Unexpected type %s' % type(nouns_dict)
        self.typos = typos
        self.dump_name = dump_name
        self.nouns_dict_all = set()
        super().__init__()
#endregion


#region NamedEntity Subclasses
Afloat = NEBLists(
    dump_name='Afloat',
    adjectives=['seasick', 'sick'],
    nouns_proper=['pescador'],  #kayak and a boat
    nouns_common=["boat", "tub", "ship", "inflatable", "sail", "onboard", "drift", "anchor", 'slipway', 'tiller', 'starboard', 'aft', 'engine', 'outboard', 'prop', 'propellor'],
    verbs=["launch", "sail", "drift", 'steamed', 'motored', "launched", "sailed", "drifting", "anchored", 'puke'],
    phrases=["sea sick", "dropped anchor"],
    typos=(Typos.verbs, Typos.nouns_proper)
    )



l = _clean(["Misty Blue", "Aries", "Aries II", "Three Sisters", "Amino", "Drakkar", "Amarisa", "Upholder", "Serenity", "Angelus", "Thistle", "Thistle B", "Aquavitesse", "Atlanta", "Atlantic Diver", "Bounty", "Becca Marie", "Becca-Marie", "Beowulf", "Bessie", "Bessie Vee", "Blazer", "Blazer 2", "Bluefin", "Blue Fin", "Blue Thunder", "Blue Turtle", "Peace and Plenty", "Endeavour", "Kimberley", "Providence", "Mistress", "Bootlegger", "Boy Carl", "Grey Viking", "Brighton Diver", "Jay Jay", "Enterprise", "Robert Mark", "Channel Cheiftain", "Carrick Lee", "Castaway", "Great Escape", "Celtic Warrior", "Channel Diver", "Channel Warrior", "Charisma", "Aquila", "Chinquita", "Enterprise", "Christyann", "Cloud 9", "Cloud Nine", "Ali-Cat", "Alicat", "Ali Cat", "Glad Tidings", "Jessica Hettie", "Wave Cheiftain", "Mermaid II", "Capriole", "Crimson Tide", "Dannyboy", "Samuel Irvin", "Dawn Breaker", "Dawn Raider", "Dawn Tide", "Dawn Venture", "Deep Blue", "Offshore Rebel", "Shande", "Rapid Fisher", "Dentex", "Discovery", "Sha-King", "Shaking", "Dominator", "Final Answer", "Panther", "Emma Kate", "Galloper", "Evelyn-Jane", "Evelyn Jane", "Excalibur", "Famous", "Fire Fox", "Grey Fox", "Greyfox", "Duke IV", "Duke 4", "Suveran", "Jensen", "Mystique", "Folkestone Voyager", "Piscine", "Gemini", "Girl Mandy", "Gold-Rush", "Highlander", "Independent", "Jean K", "Jenifers Pride", "Jo-Dan", "Jo Dan", "Jodan", "Daphne Carole", "Jolly Fisherman", "Telmar", "Manta Ray", "Manta-ray", "mantaray", "Katie Ann", "Kellys Hero", "Katrina", "Lady Anne", "Lady Essex", "Lady Mary", "Excel 2", "Excel II", "Lizy", "Louise Jane", "Obsession", "Frances Jane", "Amaretto III", "Amaretto 3", "Kraken", "Marie F", "Neptune", "Boy Richard", "Charlotte Louise", "Margaret Elaine", "Tracy Jane", "Shogun", "Penetrater", "Meerkat", "Razorbill", "Sovereign", "Venus", "Mistress", "Kaimalino", "Morgan M", "MV Freedom", "Mystique", "Predator", "Atlantis", "Che Sara Sara", "North Star", "Ocean-Pearl II", "Ocean Pearl", "Ocean-Pearl", "Ocean Warrior", "Optimist", "Osprey", "Our Gemma", "Our Joe-L", "Our Joe", "Our Joy", "Outlaw", "Out Rage", "Adventuress", "Panther", "Pathfinder", "Path finder", "Celtic Fox", "Chinoo", "Atlantis", "Piscary", "Size Matters", "C Cheetah", "Secret Star", "Sea Tradar", "Blue Duo", "Danda", "Ruby-D", "Ruby D", "RubyD", "Private Venture", "Queensferry", "Better Days", "Random Harvest", "Random Harvest", "Reecer", "Rocket", "Royal Charlotte", "Portia", "Royal Eagle", "Anglo Dawn", "Sally Ann", "Saltwind", "Sarah JFK", "Scooby Doo Too", "Sea Angler II", "Sea Angler 2", "Lady Elsie", "Sea Breeze 3", "Sea Breeze III", "Sea Fire", "Kingfisher", "Voyager", "Waderbay", "Sea Fox", "Dolly P", "DollyP", "White Marlin", "Why Worry", "Wight Huntress", "Sea-Juicer", "Sea Juicer", "SeaJuicer", "Sea Leopard", "Sea Leopard", "Sea-Otter", "Sea Otter", "Sea Searcher", "Sea Spray", "Seeker", "Jo Dan", "Typhoon", "Carrie Jane", "Shy-Torque", "Shy Torque", "Silver Sea", "Silver Spray", "Skerry Belle", "Sophie Lea", "Emma Jayne", "Bounty Hunter", "Spirit Of Arun", "Supanova", "Susie B", "SusieB", "Purdy", "Flamer", "San Gina", "Tango", "African Queen", "Chieftain", "Tiger", "Southern Angler", "Tina Dawn", "Last Laugh", "Trot On", "True Blue", "Two Dogs", "Predator", "Unity", "Viking", "Laura III", "Laura 3", "Christine Ann", "Dawn Mist", "Wetwheels", "Meerkat", "Never Can Tell A", "Lone Shark", "Sea Urchin II", "Sea Urchin 2", "White Maiden", "Wight Sapphire", "Wight Spirit", "Lowestoft Provider", "Hvita", "Penetrater", "Trojan Warrior", "Diablo", "Dulcie T", "Southern Star", "Force 10", "Bonaventure", "Serenity", "Rachel K", "RachelK", "Lillie May", "Warlord", "Sambe", "On A Promise", "Yorkshireman", "Gloria B", "Kingfisher", "In-T-Net", "Malaki", "Rose-Ann", "Kittiwake", "Buccaneer", "Mia Jay", "High Flyer", "Bluedawn", "Wight Rebel", "T.J. Gannet", "TJ Gannet", "Danny Boy", "Bachanalian", "Ocean Lass", "Valkyrie", "Lady D", "LadyD", "Cobra III", "Cobra 3", "Kayleigh-L", "KayleighL", "Lynander", "George Griffiths", "Lead Us", "Cleveland Princess", "Jozilee", "Challenger", "Fulmar", "AlyKat", "Edwin John", "Mary Ellen", "Jo-Jo", "Optimist", "Trio 3", "Trio III", "Missy Moo", "Madonna", "She Likes It 2", "She Likes It II", "Marlin", "Catch 22", "Sapphire", "Joy Belle", "Anne Clare", "Misty Lady", "Trya", "Eastern Promise", "Shokwave", "Lady Grace", "Tiger Lily", "Yorkshire Lass", "Heidi J", "HeidiJ", "Ocean Crusader", "Bon Amy", "Telmar", "Starfish", "Torbay Belle", "Lady Ann", "Pace Arrow", "Saxon Lady", "Tuonela", "Hard Labour", "Jolly Roger", "Lady Helen", "Blue Mink", "Crusader", "Elegance", "Toplines", "Atlantic Blue", "Lady Lucy", "Pride and Joy", "Pride & Joy", "Three Sisters", "Lady Sarah", "Red 5", "Red V", "Lady Of The Lake", "Nemesis", "Patrice", "Great White", "Adelaide", "Osprey", "Yellowfin", "Mirage", "Aces High", "Kaimalino", "Tamesis", "Reel Action", "Bramblewick", "Flamer", "Top Cat", "Lone Shark", "Als Spirit", "Ailish", "Racheal Jane", "Swordfish", "Trio III", "Trio 3", "Porbeagle", "Freedom", "Joint Venture", "Aldeburgh Angler", "Karyl-Anne", "Julie D", "JulieD", "Barracuda", "Blue Marlin", "Escapade", "Lily Lolo", "Wild Frontier", "Dawn Tide", "Dusk Diver", "Sunrise", "Osprey", "Stoney Broke", "Natalie Kristen", "Branscombe Pearl", "Striker", "Morning Breeze", "Oberon", "Moonshine", "Sportsmans Night", "Predator", "Venture", "Senija", "Kingfisher", "Mistress Linda", "Danse De Leau", "Swin Ranger", "Tamesis", "Foxy Lady", "Pioneer", "Restorick", "Morgan James", "Dakala Mist", "Lady Tina", "Top Cat", "Michelle Mary", "Swallow IV", "Swallow 4", "Moonraker", "Pegasus", "Miss Patty", "Sea Fever", "She Likes It Rough" "Chrisanda", "Jubrae", "Thresher", "Bonwey", "Heartbeat", "Sarah Michelle", "Mac", "Sally Ann", "Duchess II", "Defiant", "Shalimar", "Orca", "Bayside", "Rose-Ann", "Rose Ann", "Caroline"])
l = [n.lower() for n in l]
AfloatCharterBoat = NEBLists(
    dump_name='AfloatCharterBoat',
    nouns_proper=l,
    verbs=["charter", "skipper", "hire"],
    nouns_common=['charter', 'inflatable'],
    phrases=['charter boat'],
    typos=(Typos.nouns_common, Typos.verbs)
    )


AfloatKayak = NEBLists(
    dump_name='AfloatKayak',
    nouns_common=["kayak", "yak", "prowler"],
    nouns_proper=["tarpon", "trident", "scupper", "paddle", "fatyak", "dorado", "teksport", "emotion", 'cuda', 'mirage', 'profish', 'outback', 'sturgeon', 'wilderness', 'aquago', 'juntos', 'malibu', 'huntsman', 'profisha', 'revo 16', 'gosea', 'tetra', 'feelfree', 'hobbie', 'dorado', 'wilderness systems', 'wido', 'riber', 'perception', 'systemx', 'tootega', "kaskazi", 'galaxy', 'viking', 'werner', 'railblaza'],
    phrases=['mirage outback', 'pelican catch', 'lifetime muskie', "fat yak", 'system x', 'jackson cuda', 'cuda 14'],
    verbs=['kayaking', 'paddled'],
    typos=None)


AfloatPrivate = NEBLists(
    dump_name='AfloatPrivate',
    nouns_common=['rib', 'oar', "dinghy", 'dory', 'outboard'],
    nouns_proper=['arvor', 'fibramar', 'treeve', 'quicksilver', 'fastliner', 'strikeline', 'leisurecat', 'mallon', 'beneteau', 'antares', 'reiver', 'saltram', 'colvic', 'navistar'],
    phrases=['wilson flyer', 'nord star', 'cougar cat', 'mitchell 22', 'sea line', 'orkney 520'],
    verbs=['rowed'],
    typos=None)


GearAngling = NEBLists(
    dump_name='GearAngling',
    nouns_common=["rod", "beachcaster", "beachcasters", "rod", "bait", "plug", 'lure', 'spinner'],
    nouns_proper=['redgill'],
    phrases=['beach caster', 'beach casters', 'livebait', 'live bait', 'lrf', 'light rock fishing', 'feathering', 'red gill', 'red gills', 'savage gear'],
    verbs=["spinning", 'cast', 'plugging'],
    typos=None)



GearNoneAngling = NEBLists(
    dump_name='GearNoneAngling',
    nouns_common=['seine'],
    verbs=['netting'],
    phrases=['spear gun', 'long lines', 'long line', 'purse net', 'seine net'],
    typos=None)


MetrologicalAll = NEBLists(
    dump_name='MetrologicalAll',
    adjectives=['heavy', 'big', 'small', 'huge', 'giant', 'tiny', 'little', 'loads', 'plenty', 'lots'],
    nouns_common=["pound", "pounds", "kilos", "kilo", "kilogram", "kilograms", "grams", "gram", "ounce", "ounces", "lb",
                  "lbs", "ozs", "kg", "kgs", "meter", "meters", "metre", "metres", "cm", "cms", "centimeters",
                  "centimeter", "centimetres", "centimetre", "inch", "inches", "foot", "feet"],
    add_similiar=False,
    typos=None
    )



Session = NEBLists(
    dump_name='Session',
    adjectives=['early', 'late'],
    nouns_common=['session', 'trip', "hour", "minute", "hour", 'morning', 'afternoon', 'noon', 'midday', 'flood', 'ebb'],
    phrases=["before low", "after low", "to low", "after high", "to high", "before high", "either side", 'upto low', 'upto high', 'the flood', 'the ebb', 'incoming tide',
             "around high", "around low", "tide out", "tide down", "tide in", "tide up", "packed up", "went home", "p.m.", "a.m.", 'pm', 'a.m', 'p.m', "hrs", "mins", "pound mark","way back"],
    verbs=['angling', 'arrived', 'casting', 'catch', 'ended', 'fishing', 'hook', 'land', 'leave', 'leave', 'release', 'start', 'stop', 'trolling', 'unhook', 'blanked'],
    typos=None
    )


MackerelAsBait = NEBLists(
    dump_name='MackerelAsBait',
    adjectives=['frozen'],
    mackerel=['mackeerel', 'makey', 'mackkrel', 'mackkeral', 'macrel', 'makeral', 'maackie',
                 'maccarel', 'macarrel', 'mackrell', 'makey', 'mackrrell', 'makerell', 'mackerall', 'maceral', 'maacky',
                 'makerrel', 'maackerel', 'maackrel', 'mackie', 'mackks', 'mackiee', 'macarell', 'macckerel', 'mackerell',
                 'mackkerel', 'mackky', 'mackerral', 'makrell', 'maackrell',
                 'mackerrel', 'maackey', 'mack', 'makerel', 'mackeraal', 'maakerel', 'makrel', 'maccky',
                 'macckrel', 'mackey', 'macki', 'macckey', 'macck', 'makeal', 'mackkie',
                 'makie', 'mackrrel', 'makereel', 'mackrl', 'mackyy', 'mackrel', 'mackeral',
                 'maackeral', 'mackkey', 'macareel', 'maerel', 'macerel', 'makeels', 'mackreel',
                 'mackral', 'mackreell', 'maack', 'mackerel', 'macky', 'mackrll', 'mackereel',
                 'mackkrell', 'makeraal', 'mackeeral', 'makkerel', 'makerral'],
    verbs=['baited', 'livebaited', 'deadbaited', 'tipped', 'using'], 
    nouns_common=['fillet', 'side', 'head', 'belly', 'chunk', 'sliver', 'bait', 'flapper', 'strip', 'cocktail', 'head'],
    phrases=['on mackerel', 'on mack', 'on mackeral', 'on mackie', 'on mackey', 'on macky', 'whole mackerel', 'whole mackie', 'whole macky', 'whole mackey', '0.5 mackerel', '0.5 mackey',
                '0.5 macky', '0.5 mackie', 'loaded with mackerel', 'loaded with mackie', 'loaded with mack', 'loaded with macky'],
    typos=None
    )


BaitSpecies = NEBLists(
    dump_name='BaitSpecies',
    nouns_common=['worm', 'black', 'squid', 'lug', 'sewie', 'prawn', 'crab', 'peeler', 'softies', 'softys', 'softy', 'bluey',
                'sandeel', 'rag', 'ragworm', 'clam', 'mussel', 'mussle', 'runnydown', 'maddies'
                )
    
#endregion






#region _NamedEntityBaseDict subclasses

##################################################################################
# if add another unspecified class, update mmo.write_hints.py:make_species_hints #
##################################################################################


#These are all entities which require a lookup under a key
#for examples, we need to know that codling and coddo
#are both cod


DateTimeDayOfWeek = NEBDicts(
    nouns_dict={'monday':['monday', 'mon', 'mond', 'monda', 'mdy'], 'tuesday':['tuesday', 'tue', 'tues', 'tuesd', 'tu'],
     'wednesday':['wednesday', 'wed', 'wedn', 'wedne', 'wds'], 'thursday':['thursday', 'thu', 'thur', 'thurs'],
     'friday':['friday', 'fri', 'frid', 'frida', 'fr'], 'saturday':['saturday', 'sat', 'satu', 'satur'],
     'sunday':['sunday', 'sun', 'sund', 'sunda']},
    typos=None,
    dump_name='DateTimeDayOfWeek')



DateTimeMonth = NEBDicts(
    nouns_dict={'january':['january', 'jan'], 'february':['february', 'feb'], 'march':['march', 'mar'], 'april':['april', 'apr'], 'may':['may'],
     'june':['june', 'jun'], 'july':['july', 'jul'], 'august':['august', 'aug'],
     'september':['september', 'sep', 'sept'], 'october':['october', 'oct'], 'november':['november', 'nov'], 'december':['december', 'dec']},
    typos=True,
    dump_name='DateTimeMonth')
DateTimeMonth.get_season = _get_season #append the getseason function for convieniance



DateTimeSeason = NEBDicts(
    nouns_dict={'spring':['spring'], 'winter':['winter', 'wntr'], 'autumn':['autumn', 'aut', 'atmn'], 'summer':['summer']},
    typos=None,
    dump_name='DateTimeSeason'
    )
DateTimeSeason.get_season = _get_season




d = _species.get_species_as_dict_all()
assert d, '_species.get_species_as_dict_all() failed'
SpeciesAll = NEBDicts(nouns_dict=d,
                            typos=True,
                            dump_name='SpeciesAll')



d = _species.get_species_as_dict_sans_unspecified()
assert d, '_species.get_species_as_dict_sans_unspecified() failed'
SpeciesSpecified = NEBDicts(nouns_dict=d,
                            typos=True,
                            dump_name='SpeciesSpecified')


d = _species.get_species_as_dict_unspecified()
assert d, '_species.get_species_as_dict_unspecified() failed'
SpeciesUnspecified = NEBDicts(nouns_dict=d,
                              typos=True,
                              dump_name='SpeciesUnspecified')



assert d, '_species.get_species_sole() failed'
SpeciesUnspecifiedSole = NEBDicts(nouns_dict=d,
                                  typos=None,
                                  dump_name='SpeciesUnspecifiedSole')


d = _species.get_species_flatfish_unspecified()
assert d, '_species.get_species_flatfish() failed'
SpeciesUnspecifiedFlatfish = NEBDicts(nouns_dict=d,
                                      typos=True,
                                      dump_name='SpeciesUnspecifiedFlatfish')


d = _species.get_species_mullet_unspecified()
assert d, '_species.get_species_mullet() failed'
SpeciesUnspecifiedMullet = NEBDicts(nouns_dict=d,
                                    typos=None,
                                    dump_name='SpeciesUnspecifiedMullet')


d = _species.get_species_bream_unspecified()
assert d, '_species.get_species_bream() failed'
SpeciesUnspecifiedBream = NEBDicts(nouns_dict=d,
                                   typos=True,
                                   dump_name='SpeciesUnspecifiedBream')


d = _species.get_species_skates_rays_unspecified()
assert d, '_species.get_species_skates_rays() failed'
SpeciesUnspecifiedSkatesRays = NEBDicts(nouns_dict=d,
                                        typos=True,
                                        dump_name='SpeciesUnspecifiedSkatesRays')
#endregion
 




def _bld_global_sets(force_dump):
    '''build/load/save global sets
    all_single is primarily for use as a whitelist nlp.stopwords
    '''
    global all_; global all_single
    
    def _bld(word_set):
        '''build whitelist of words for nlp.stopwords'''
        global all_; global all_single       
        ss = {w for w in _flat([v.split() for v in word_set])}
        all_single |= ss  #every single word as a single word, eg 'to high' will be split to 'to', 'high'
        all_ |= word_set #all words and phrases as they appear, e.g. 'to high' will still be 'to high'

    if _iolib.file_exists(_settings.PATHS.NAMED_ENTITIES_ALL) and not force_dump:
        all_ = _iolib.unpickle(_settings.PATHS.NAMED_ENTITIES_ALL)
        print('Loaded named_entities.all from file system')

    if _iolib.file_exists(_settings.PATHS.NAMED_ENTITIES_ALL_SINGLE) and not force_dump:
        all_single = _iolib.unpickle(_settings.PATHS.NAMED_ENTITIES_ALL_SINGLE)
        print('Loaded named_entities.all_single from file system')

    if all_ and all_single: return
    all_single = set(); all_ = set() #just make sure
    print('**loading and dumping named entities ....**')
    _bld(Afloat.allwords)
    _bld(AfloatCharterBoat.allwords)
    _bld(AfloatKayak.allwords)
    _bld(AfloatPrivate.allwords)
    _bld(GearAngling.allwords)
    _bld(GearNoneAngling.allwords)
    _bld(MetrologicalAll.allwords)
    _bld(MetrologicalAll.allwords)
    _bld(DateTimeDayOfWeek.get_flat_set())
    _bld(DateTimeMonth.get_flat_set())
    _bld(DateTimeSeason.get_flat_set())
    _bld(SpeciesAll.get_flat_set())

    #now try the gazetteer
    try:
        _bld(_gaz.get_all_as_set())
    except AttributeError as e:
        print('Failed to load the gazetter. This will happen if name_cleaned is empty or blank for all gazetter records.\n\nRun mmo.clean_gaz.py.')

    if force_dump or not _iolib.file_exists(_settings.PATHS.NAMED_ENTITIES_ALL):
        _iolib.pickle(all_, _settings.PATHS.NAMED_ENTITIES_ALL)

    if force_dump or not _iolib.file_exists(_settings.PATHS.NAMED_ENTITIES_ALL_SINGLE):
        _iolib.pickle(all_single, _settings.PATHS.NAMED_ENTITIES_ALL_SINGLE)


_bld_global_sets(False)


if __name__ == '__main__':
    print('s')
    quit()
