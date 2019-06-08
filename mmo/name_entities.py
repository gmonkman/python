'''doc'''
####################################################################################
### If new classes are added here, we must add to write_hints._get_white_list_words#
####################################################################################

##################################################################################
# if add another UNSPECIFIED class, update mmo.write_hints.py:make_species_hints #
##################################################################################


import funclib.stringslib as _stringslib
import dblib.mssql as _mssql

from mmodb import species as _species
from nlp import baselib as _nlpbase
from nlp import typo as _typo
from nlp import relib as _relib

class UnspecifiedKeys():
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
#endregion

TYPOS_MIN_LENGTH = 5
TYPOS_FIX_FIRST_N_CHARS = 2
TYPO_OPTIONS_ALL = set(('nouns_common', 'nouns_proper', 'verbs', 'phrases', 'adjectives')) #these match the allowed word types in NEBLists, they arnt relevant for the dict classes because they are all nouns




#region LISTS HANDLER
class NEBLists(_NamedEntityBase):
    '''Create an list of words based on kwarg options

    Supported kwargs are:
    add_similiar=False
    force_conjugate=False
    typos=('nouns', 'verbs', 'phrases', 'others')
    force_plural_singular=False
    '''
    def __init__(self, nouns_proper=None, nouns_common=None, verbs=None, phrases=None, adjectives=None, add_similiar=False, typos=('nouns_common', 'nouns_proper', 'verbs', 'phrases', 'adjectives')):
        ld = lambda v: set(v) if v else set()
        self.nouns_common = ld(nouns_common)
        self.nouns_proper = ld(nouns_proper)
        self.verbs = ld(verbs)
        self.phrases = ld(phrases)
        self.adjectives = ld(adjectives)
        self.add_similiar=add_similiar
        self.typos = typos
        super().__init__()


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
        self.add_similiar = add_similiar
        self.allwords = set()
        self.all_base_words = set()
        self.all_base_words |= self.nouns_common
        self.all_base_words |= self.nouns_proper
        self.all_base_words |= self.verbs
        self.all_base_words |= self.adjectives
        self.all_base_words |= self.phrases

        typos = set(typos)
        assert set(typos).issubset(typos), 'Invalid options found in typos. Typos must be in %s' % TYPO_OPTIONS_ALL
        
        self._get()
        assert self.allwords, 'allwords was empty. This is unexpected'
    

    def _get(self):
        nouns_proper = set(); verbs = set(); phrases = set(); nouns_common = set(); adjectives = set()

        if add_similiar:
            wds = []
            for w in self.nouns_common:
                wds.append(w)
                wds.extend(_nlpbase.lemma_bag_all(w, force_plural=True, force_conjugate=False)) #TODO check lamma_bag_all does not conjugate on force_conjugate=false
            nouns_commom |= set(wds)

            wds = []
            for w in verbs:
                wds.append(w)
                wds.extend(_nlpbase.lemma_bag_all(w, force_plural=False, force_conjugate=True)) #TODO check lamma_bag_all does not conjugate on force_conjugate=false
            verbs |= set(wds)

        if 'phrases' in typos: phrases |= set(_typo.typos(phrases, filter_start_n=TYPOS_FIX_FIRST_N_CHARS))
        if 'verbs' in typos: verbs |= set(_typo.typos(verbs, filter_start_n=TYPOS_FIX_FIRST_N_CHARS))
        if 'nouns_proper' in typos: nouns_proper |= set(_typo.typos(nouns_common, filter_start_n=TYPOS_FIX_FIRST_N_CHARS))
        if 'nouns_common' in typos: nouns_common |= set(_typo.typos(nouns_common, filter_start_n=TYPOS_FIX_FIRST_N_CHARS))
        if 'adjectives' in typos: adjectives |= set(_typo.typos(others, filter_start_n=TYPOS_FIX_FIRST_N_CHARS))
        self.allwords |= nouns_proper 
        self.allwords |= verbs
        self.allwords |= phrases 
        self.allwords |= nouns_common 
        self.allwords |= adjectives



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
        lst = set()
        for word in self.allwords:
            inds = _relib.get_indices(s, word)
            if inds:
                out[word] = inds
        return out
#endregion








#region DICT HANDLER
class NEBDicts(_NamedEntityBaseDict):
    '''class to hand dicts of words
    '''

    def __init__(self, nouns, typos=True):
        self.nouns_dict = nouns
        assert isinstance(nouns_dict, dict), 'Unexpected type %s' % type(nouns_dict)
        self.typos = typos
        self.nouns_dict_all = set()
        super().__init__()



class _NamedEntityBaseDict():

    def __init__(self):
        assert isinstance(nouns, dict)
        #self.nouns_dict_all = {}
        #self.nouns_dict = {}
        #self.nouns = nouns  - this IS set by the subclass
        self._setdic()

    
    def _setdic(self):
        '''Sets self.noun_dict_all by generating
        typos and plurals using NOUN_DICT, where
        NOUN_DICT is set by the inheriting class
        '''
        self.nouns_dict_all = {}
        for key, key_words in self.nouns_dict:  #speciesid is the proper name, it should also be in words as the alias includes the proper name
            assert words, 'noun_dict %s was empty' % key
            wds = []            
            for w in words:
                wds += _nlpbase.plural_sing(w)

            if self.typos:
                wds += _typo.typos(wds, add_v=False, filter_start_n=TYPOS_FIX_FIRST_N_CHARS, MIN_LENGTH_FOR_TYPOS=TYPOS_MIN_LENGTH)

            self.nouns_dict_all[key] = set(wds)
        

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
        words = self.nouns_dict_all.get([keyid])
        assert words, 'nouns_all had no items for key %s' % keyid
        for word in words:
            inds = _relib.get_indices(s, word)
            if inds:
                out['word'] = inds
        return out


    def get_by_key(self, key, force_load=False, use_proper=False):
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
        return set(self.nouns_dict_all.values())
#endregion






#region NamedEntity Subclasses
Afloat = NEBLists(
    adjectives = ['seasick', 'sick'],
    nouns_proper = ['pescador'],  #kayak and a boat
    nouns_common = ["boat", "tub", "ship", "inflatable", "sail", "onboard", "drift", "anchor", 'slipway', 'tiller', 'starboard', 'aft', 'engine', 'outboard', 'prop', 'propellor'],
    verbs = ["launch", "sail", "drift", 'steamed', 'motored', "launched", "sailed", "drifting", "anchored", 'puke'],
    phrases = ["sea sick"])



l = _clean(["Misty Blue", "Aries II", "Three Sisters", "Amino", "Drakkar", "Amarisa", "Upholder", "Serenity", "Angelus", "Thistle B", "Aquavitesse", "Atlanta", "Atlantic Diver", "Bounty", "Becca-Marie", "Beowulf", "Bessie Vee", "Bite", "Blazer 2", "Bluefin", "Blue Fin", "Blue Thunder", "Blue Turtle", "Peace and Plenty", "Endeavour", "Kimberley", "Providence", "Mistress", "Bootlegger", "Boy Carl", "Grey Viking", "Brighton Diver", "Jay Jay", "Enterprise", "Robert Mark", "Channel Cheiftain 5", "Carrick Lee", "Castaway", "Great Escape", "Celtic Warrior", "Channel Diver", "Channel Warrior", "Charisma", "Aquila", "Chinquita", "Enterprise", "Christyann", "Cloud Nine", "Ali-Cat", "Glad Tidings", "Jessica Hettie", "Wave Cheiftain", "Mermaid II", "Capriole", "Crimson Tide", "Dannyboy II", "Samuel Irvin 3", "Dawn Breaker", "Dawn Raider", "Dawn Tide", "Dawn Venture", "Deep Blue", "Offshore Rebel IV", "Shande III", "Rapid Fisher", "Dentex", "Discovery", "Sha-King", "Dominator", "Final Answer", "Panther", "Emma Kate", "Galloper", "Evelyn-Jane", "Excalibur", "Famous", "Fire Fox", "Grey Fox", "Duke IV", "Suveran", "Jensen", "Mystique", "Folkestone Voyager", "Piscine", "Gemini 3", "Girl Mandy", "Gold-Rush", "Hermit", "Highlander", "Independent", "Jean K", "Jenifers Pride", "Jo-Dan", "Daphne Carole", "Jolly Fisherman", "Telmar", "Manta Ray", "Katie Ann", "Kellys Hero", "Katrina", "Lady Anne", "Lady Essex III", "Lady Mary", "Excel 2", "Lizy", "Louise Jane", "Obsession", "Frances Jane", "Amaretto III", "Kraken", "Marie F", "Neptune", "Boy Richard", "Charlotte Louise", "Margaret Elaine", "Tracy Jane", "Shogun", "M.V. Penetrater", "Penetrater", "Meerkat", "Razorbill 3", "Sovereign", "Venus", "Mistress", "Kaimalino", "Morgan M", "MV Freedom", "Mystique II", "Predator", "Atlantis", "Che Sara Sara", "North Star", "Ocean-Pearl II", "Ocean Warrior 3", "Optimist", "Osprey", "Our Gemma", "Our Joe-L", "Our Joy", "Outlaw", "Out Rage", "Adventuress", "Panther", "Pathfinder", "Celtic Fox", "Chinook 11", "Atlantis", "Piscary", "Size Matters", "C Cheetah", "Secret Star", "Sea Tradar", "Blue Duo", "Danda", "Ruby-D", "Predator", "Starfish", "Private Venture", "Queensferry", "Better Days", "Random Harvest", "Random Harvest II", "Reecer", "Rocket", "Royal Charlotte", "Portia", "Royal Eagle", "Anglo Dawn III", "Sally Ann", "Saltwind", "Sarah JFK", "Scooby Doo Too", "Sea Angler II", "Lady Elsie", "Sea Breeze 3", "Sea Fire ", "Kingfisher", "Voyager", "Waderbay", "Sea Fox", "Dolly P", "White Marlin", "Why Worry", "Wight Huntress", "Sea-Juicer", "Sea Leopard", "Sea Leopard", "Sea-Otter 2", "Sea Searcher", "Sea Spray", "Seeker", "Jo Dan", "Typhoon", "Carrie Jane", "Progress", "Shy-Torque III", "Silver Sea", "Silver Spray", "Skerry Belle", "Sophie Lea", "Emma Jayne", "Bounty Hunter", "Spirit Of Arun", "Supanova", "Susie B", "Purdy and Flamer 2", "San Gina II", "San Gina I", "Tango", "The African Queen", "Chieftain", "Tiger", "Southern Angler", "Tina Dawn", "Last Laugh", "Trot On", "True Blue", "Two Dogs", "Predator", "Unity", "Viking", "Laura III", "Christine Ann", "Dawn Mist", "Wetwheels", "Meerkat", "Never Can Tell A", "Lone Shark", "Sea Urchin II", "White Maiden", "Wight Sapphire", "Wight Spirit", "Lowestoft Provider", "Hvita", "Penetrater", "Trojan Warrior Whitby", "Diablo", "Dulcie T", "Southern Star", "Force 10", "Bonaventure II", "Serenity", "Rachel K", "Lillie May", "Warlord", "Sambe", "On A Promise", "Yorkshireman", "Gloria B11", "Kingfisher II", "In-T-Net", "Malaki", "Rose-Ann", "Kittiwake 3", "Buccaneer", "Mia Jay", "High Flyer", "Bluedawn", "Wight Rebel", "T.J. Gannet", "Danny Boy", "Bachanalian", "Ocean Lass", "Valkyrie", "Lady D", "Cobra 111 (Nab- cat)", "Kayleigh-L", "Lynander", "George Griffiths MBE", "Lead Us", "Cleveland Princess", "Chocolate", "Jozilee", "Challenger 2", "M.F.V. Fulmar", "AlyKat", "Edwin John", "Mary Ellen", "Jo-Jo", "Optimist", "Trio 3", "Missy Moo", "Madonna", "She Likes It 2", "Marlin", "Catch 22", "Sapphire", "Joy Belle", "Anne Clare", "Misty Lady", "Trya II", "Eastern Promise", "Shokwave", "Lady Grace", "Fish On!", "Tiger Lily", "Yorkshire Lass", "Heidi J", "Ocean Crusader", "Bon Amy", "Telmar II", "Starfish", "Torbay Belle", "Lady Ann", "Pace Arrow", "Saxon Lady", "Tuonela", "Hard Labour", "Jolly Roger", "Lady Helen", "Blue Mink", "Crusader 2", "Elegance", "Toplines", "Atlantic Blue", "Lady Lucy II", "Pride and Joy", "Three Sisters", "Lady Sarah", "Red 5", "Lady Of The Lake", "Nemesis", "Patrice II", "Great White", "Adelaide", "Osprey", "Yellowfin", "Mirage", "Aces High", "Kaimalino", "Tamesis", "Reel Action", "Bramblewick", "Flamer IV", "Top Cat III", "Lone Shark III", "Als Spirit", "Ailish", "Racheal Jane", "Swordfish", "Trio III", "Porbeagle", "Freedom", "Joint Venture", "Aldeburgh Angler", "Karyl-Anne", "Julie D", "Barracuda", "Blue Marlin", "Escapade", "Lily Lolo", "Wild Frontier", "Dawn Tide", "Dusk Diver", "Sunrise", "Osprey II", "Stoney Broke", "Natalie Kristen II", "Branscombe Pearl", "Striker", "Morning Breeze", "Oberon", "Moonshine", "Sportsmans Night", "Predator", "Venture", "Senija", "Kingfisher", "Mistress Linda", "Danse De Leau", "Swin Ranger", "M.F.V. Tamesis", "Foxy Lady", "Pioneer", "Restorick III", "Morgan James", "Dakala Mist", "Lady Tina", "Top Cat", "Michelle Mary", "Swallow IV", "Moonraker", "Pegasus", "Miss Patty", "Sea Fever", "She Likes It Rough 2", "Chrisanda", "Jubrae", "Thresher", "Bonwey", "Heartbeat", "Sarah Michelle", "Mac", "Sally Ann", "Duchess II", "Defiant", "Shalimar", "Orca", "Bayside", "Rose-Ann", "Rose Ann", "Caroline"])
l = [n.lower() for n in l]
AfloatCharterBoat = NEBLists(
    nouns_proper = l,
    verbs = ["charter", "skipper", "hire"],
    nouns_common = ['charter', 'inflatable'],
    phrases = ['charter boat'])


AfloatKayak = NEBLists(
    nouns_common = ["kayak", "yak", "prowler"],
    nouns_proper = ["tarpon", "trident", "scupper", "paddle", "fatyak", "dorado", "teksport", "emotion", 'cuda', 'mirage', 'profish', 'outback', 'sturgeon', 'wilderness', 'aquago', 'juntos', 'malibu', 'huntsman', 'profisha', 'revo 16', 'gosea', 'tetra', 'feelfree', 'hobbie', 'dorado', 'wilderness systems', 'wido', 'riber', 'perception', 'systemx', 'tootega', "kaskazi", 'galaxy', 'viking', 'werner', 'railblaza'],
    phrases = ['mirage outback', 'pelican catch', 'lifetime muskie', "fat yak", 'system x', 'jackson cuda', 'cuda 14'],
    verbs = ['kayaking', 'paddled'])


AfloatPrivate = NEBLists(
    nouns_common = ['rib', 'oar', "dinghy", 'dory', 'outboard'],
    nouns_proper = ['arvor', 'fibramar', 'treeve', 'quicksilver', 'fastliner', 'strikeline', 'leisurecat', 'mallon', 'beneteau', 'antares', 'reiver', 'saltram', 'colvic', 'navistar'],
    phrases = ['Wilson Flyer', 'nord star', 'cougar cat', 'mitchell 22', 'sea line', 'orkney 520'],
    verbs = ['rowed'])


GearAngling = NEBLists(
    nouns_common = ["rod", "beachcaster", "beachcasters", "rod", "bait", "plug", 'lure', 'spinner'],
    nouns_proper = ['redgill'],
    phrases = ['beach caster', 'beach casters', 'livebait', 'live bait', 'lrf', 'light rock fishing', 'feathering', 'red gill', 'red gills', 'savage gear'],
    verbs = ["spinning", 'cast', 'plugging'])


GearNoneAngling = NEBLists(
    nouns_common = ['seine'],
    verbs = ['netting'],
    phrases = ['spear gun', 'long lines', 'long line', 'purse net', 'seine net'])


MetrologicalAll = NEBLists(
    adjectives = ['heavy', 'big', 'small', 'huge', 'giant', 'tiny', 'little', 'loads', 'plenty', 'lots'],
    nouns_common = ["pound", "pounds", "kilos", "kilo", "kilogram", "kilograms", "grams", "gram", "ounce", "ounces", "lb", "lbs", "ozs", "kg", "kgs", "meter", "meters", "metre", "metres", "cm", "cms", "centimeters", "centimeter", "centimetres", "centimetre", "inch", "inches", "foot", "feet"],
    typos=('nouns_common'),
    add_similiar=False
    )


Session = NEBLists(
    adjectives = ['early', 'late'],
    nouns_common = ['session', 'trip', "hour", "minute", "hour", 'morning', 'afternoon', 'noon', 'midday', 'flood', 'ebb'],
    phrases = ["before low", "after low", "to low", "after high", "to high", "before high", "either side", "around high", "around low", "tide out", "tide down", "tide in", "tide up", "packed up", "went home", "p.m.", "a.m.", 'pm', 'a.m', 'p.m', "hrs", "mins"],
    verbs = ['angling', 'arrived', 'casting', 'catch', 'ended', 'fishing', 'hook', 'land', 'leave', 'leave', 'release', 'start', 'stop', 'trolling', 'unhook']
#endregion






#region _NamedEntityBaseDict subclasses

##################################################################################
# if add another unspecified class, update mmo.write_hints.py:make_species_hints #
##################################################################################


#These are all entities which require a lookup under a key
#for examples, we need to know that codling and coddo
#are both cod


DateTimeDayOfWeek = NEBDicts({'monday':['monday', 'mon', 'mond', 'monda', 'mdy'], 'tuesday':['tuesday', 'tue', 'tues', 'tuesd', 'tu'], 'wednesday':['wednesday', 'wed', 'wedn', 'wedne', 'wds'], 'thursday':['thursday', 'thu', 'thur', 'thurs'], 'friday':['friday', 'fri', 'frid', 'frida', 'fr'], 'saturday':['saturday', 'sat', 'satu', 'satur'], 'sunday':['sunday', 'sun', 'sund', 'sunda']},
                                    typos=False)


DateTimeMonth = NEBDicts({'january':['january', 'jan'], 'february':['february', 'feb'], 'march':['march', 'mar'], 'april':['april', 'apr'], 'may':['may'], 'june':['june', 'jun'], 'july':['july', 'jul'], 'august':['august', 'aug'], 'september':['september', 'sep', 'sept'], 'october':['october', 'oct'], 'november':['november', 'nov'], 'december':['december', 'dec']}, 
                         typos=False)
DateTimeMonth.get_season = _get_season #append the getseason function for convieniance


DateTimeSeason = NEBDicts({'spring':['spring'], 'winter':['winter', 'wntr'], 'autumn':['autumn', 'aut', 'atmn'], 'spring':['spring']}, typos=False)
DateTimeSeason.get_season = _get_season


d = _species.get_species_as_dict_sans_unspecified()
assert d, '_species.get_species_as_dict_sans_unspecified() failed'
SpeciesSpecified = NEBDicts(d)


d = _species.get_species_as_dict_unspecified()
assert d, '_species.get_species_as_dict_unspecified() failed'
SpeciesUnspecified = NEBDicts(d)


d = _species.get_species_sole()
assert d, '_species.get_species_sole() failed'
SpeciesUnspecifiedSole = NEBDicts(d)


d = _species.get_species_flatfish()
assert d, '_species.get_species_flatfish() failed'
SpeciesUnspecifiedFlatfish = NEBDicts(d)


d = _species.get_species_mullet()
assert d, '_species.get_species_mullet() failed'
SpeciesUnspecifiedMullet = NEBDicts(d)


d = _species.get_species_bream()
assert d, '_species.get_species_bream() failed'
SpeciesUnspecifiedBream = NEBDicts(d)


d = _species.get_species_skates_rays()
assert d, '_species.get_species_skates_rays() failed'
SpeciesUnspecifiedSkatesRays = NEBDcts(nouns=d)
#endregion


def _get_season(month_key):
    '''given a month get the season'''
    if month_key in ['december', 'january', 'february']: return 'winter'
    if month_key in ['march', 'april', 'may']: return 'spring'
    if month_key in ['june', 'july', 'august']: return 'summer'
    return 'autumn'