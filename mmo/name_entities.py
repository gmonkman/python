'''doc'''
import funclib.stringslib as _stringslib
import dblib.mssql as _mssql
from nlp import baselib as _nlpbase
from nlp import typo as _typo
from nlp import re as _re


def _clean(lst):
    '''clean list'''
    return  [_stringslib.filter_alphanumeric1(s, strict=True, remove_double_quote=True, remove_single_quote=True).lower() for s in lst]


class _NamedEntityBase():
    '''base class for named entities'''
    @staticmethod
    def conjugations(word_list, lexname_list, exclude=()):
        '''(iterable, iterable|str, iterable|str ) -> list
        Get original list and add conjugations (for verbs)

        word_list:iterable of of words

        '''
        if isinstance(exclude, str):
            exclude = (exclude, )

        out = []
        for w in word_list:
            out.extend(_nlpbase.similiar(w, lexname_list))

        for e in exclude:
            out.remove(e)

        return list(set(out))


    @staticmethod
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


    @staticmethod
    def pluralsingular(wordlist):
        '''add plural and singular'''

        out = []
        out = [_nlpbase.pluralize(w) for w in wordlist]
        for w in wordlist:
            out.append(_nlpbase.singularize(w))

        out = list(set(out))
        return out


    @classmethod
    def get(cls, add_similiar=False, force_conjugate=False, typos=('nouns', 'verbs', 'phrases', 'others'), force_plural_singular=False, as_set=False):
        '''this gets a list of words with misspellings, conjugates and plurals
        according to the class variable name

        e.g. if the class variable has contans noun, we don't conjugate

        Note for string comparisons, use sets
        '''
        def ext(wordlst, force_conjugate, force_plural):
            '''f'''
            wds = []
            for w in wordlst:
                wds.append(w)
                wds.extend(_nlpbase.similiar(w, force_plural=force_plural, force_conjugate=force_conjugate))
            return wds

        nouns = []; verbs = []; others = []; phrases = []
        for s in dir(cls):
            attr = getattr(cls, s)
            s = s.lower()
            if isinstance(attr, (list, tuple)):
                if callable(attr) and attr.startswith('__'): continue
                if 'noun' in s and 'proper' not in s:
                    nouns.extend(attr)
                elif 'verb' in s.lower():
                    verbs.extend(attr)
                elif 'phrase' in s:
                    phrases.extend(attr)
                else:
                    others.extend(attr)

        if add_similiar:
            nouns = ext(nouns, force_conjugate=force_conjugate, force_plural=True)
            verbs = ext(verbs, force_conjugate=True, force_plural=force_plural_singular)
            others = ext(others, force_conjugate=force_conjugate, force_plural=force_plural_singular)

        words = phrases + nouns + verbs + others #yes we can just add lists
        if typos: print('\nGenerating typos ...')
        if 'phrases' in typos: words.extend(cls.typos(phrases))
        if 'verbs' in typos: words.extend(cls.typos(verbs))
        if 'nouns' in typos: words.extend(cls.typos(nouns))
        if 'others' in typos: words.extend(cls.typos(others))

        if as_set:
            return set(words)

        return list(set(words))


    @classmethod
    def indices(cls, s, **kwargs):
        '''check if any verson exists instr
        returns a dictionary with the word frequencies
        found in str which are in the class

        kwargs are passed to the base get function and are:
        add_similiar:bool
        force_conjugate:bool
        typos=('nouns', 'verbs', 'phrases', 'others')
        force_plural_singular:bool
        as_set:bool

        Example:
        >>>instr('the black black fox is grey')
        {'black':[1]}
        '''
        out = {}
        for i, word in enumerate(cls.get(**kwargs)):
            inds = _re.get_indices(s, word)
            if inds:
                out['word'] = inds
        return out



class AfloatCharterBoat(_NamedEntityBase):
    '''doc'''
    NOUNS_PROPER = _clean(["Misty Blue", "Aries II", "Three Sisters", "Amino", "Drakkar", "Amarisa", "Upholder", "Serenity", "Angelus", "Thistle B", "Aquavitesse", "Atlanta", "Atlantic Diver", "Bounty", "Becca-Marie", "Beowulf", "Bessie Vee", "Bite", "Blazer 2", "Bluefin", "Blue Fin", "Blue Thunder", "Blue Turtle", "Peace and Plenty", "Endeavour", "Kimberley", "Providence", "Mistress", "Bootlegger", "Boy Carl", "Grey Viking", "Brighton Diver", "Jay Jay", "Enterprise", "Robert Mark", "Channel Cheiftain 5", "Carrick Lee", "Castaway", "Great Escape", "Celtic Warrior", "Channel Diver", "Channel Warrior", "Charisma", "Aquila", "Chinquita", "Enterprise", "Christyann", "Cloud Nine", "Ali-Cat", "Glad Tidings", "Jessica Hettie", "Wave Cheiftain", "Mermaid II", "Capriole", "Crimson Tide", "Dannyboy II", "Samuel Irvin 3", "Dawn Breaker", "Dawn Raider", "Dawn Tide", "Dawn Venture", "Deep Blue", "Offshore Rebel IV", "Shande III", "Rapid Fisher", "Dentex", "Discovery", "Sha-King", "Dominator", "Final Answer", "Panther", "Emma Kate", "Galloper", "Evelyn-Jane", "Excalibur", "Famous", "Fire Fox", "Grey Fox", "Duke IV", "Suveran", "Jensen", "Mystique", "Folkestone Voyager", "Piscine", "Gemini 3", "Girl Mandy", "Gold-Rush", "Hermit", "Highlander", "Independent", "Jean K", "Jenifers Pride", "Jo-Dan", "Daphne Carole", "Jolly Fisherman", "Telmar", "Manta Ray", "Katie Ann", "Kellys Hero", "Katrina", "Lady Anne", "Lady Essex III", "Lady Mary", "Excel 2", "Lizy", "Louise Jane", "Obsession", "Frances Jane", "Amaretto III", "Kraken", "Marie F", "Neptune", "Boy Richard", "Charlotte Louise", "Margaret Elaine", "Tracy Jane", "Shogun", "M.V. Penetrater", "Penetrater", "Meerkat", "Razorbill 3", "Sovereign", "Venus", "Mistress", "Kaimalino", "Morgan M", "MV Freedom", "Mystique II", "Predator", "Atlantis", "Che Sara Sara", "North Star", "Ocean-Pearl II", "Ocean Warrior 3", "Optimist", "Osprey", "Our Gemma", "Our Joe-L", "Our Joy", "Outlaw", "Out Rage", "Adventuress", "Panther", "Pathfinder", "Celtic Fox", "Chinook 11", "Atlantis", "Piscary", "Size Matters", "C Cheetah", "Secret Star", "Sea Tradar", "Blue Duo", "Danda", "Ruby-D", "Predator", "Starfish", "Private Venture", "Queensferry", "Better Days", "Random Harvest", "Random Harvest II", "Reecer", "Rocket", "Royal Charlotte", "Portia", "Royal Eagle", "Anglo Dawn III", "Sally Ann", "Saltwind", "Sarah JFK", "Scooby Doo Too", "Sea Angler II", "Lady Elsie", "Sea Breeze 3", "Sea Fire ", "Kingfisher", "Voyager", "Waderbay", "Sea Fox", "Dolly P", "White Marlin", "Why Worry", "Wight Huntress", "Sea-Juicer", "Sea Leopard", "Sea Leopard", "Sea-Otter 2", "Sea Searcher", "Sea Spray", "Seeker", "Jo Dan", "Typhoon", "Carrie Jane", "Progress", "Shy-Torque III", "Silver Sea", "Silver Spray", "Skerry Belle", "Sophie Lea", "Emma Jayne", "Bounty Hunter", "Spirit Of Arun", "Supanova", "Susie B", "Purdy and Flamer 2", "San Gina II", "San Gina I", "Tango", "The African Queen", "Chieftain", "Tiger", "Southern Angler", "Tina Dawn", "Last Laugh", "Trot On", "True Blue", "Two Dogs", "Predator", "Unity", "Viking", "Laura III", "Christine Ann", "Dawn Mist", "Wetwheels", "Meerkat", "Never Can Tell A", "Lone Shark", "Sea Urchin II", "White Maiden", "Wight Sapphire", "Wight Spirit", "Lowestoft Provider", "Hvita", "Penetrater", "Trojan Warrior Whitby", "Diablo", "Dulcie T", "Southern Star", "Force 10", "Bonaventure II", "Serenity", "Rachel K", "Lillie May", "Warlord", "Sambe", "On A Promise", "Yorkshireman", "Gloria B11", "Kingfisher II", "In-T-Net", "Malaki", "Rose-Ann", "Kittiwake 3", "Buccaneer", "Mia Jay", "High Flyer", "Bluedawn", "Wight Rebel", "T.J. Gannet", "Danny Boy", "Bachanalian", "Ocean Lass", "Valkyrie", "Lady D", "Cobra 111 (Nab- cat)", "Kayleigh-L", "Lynander", "George Griffiths MBE", "Lead Us", "Cleveland Princess", "Chocolate", "Jozilee", "Challenger 2", "M.F.V. Fulmar", "AlyKat", "Edwin John", "Mary Ellen", "Jo-Jo", "Optimist", "Trio 3", "Missy Moo", "Madonna", "She Likes It 2", "Marlin", "Catch 22", "Sapphire", "Joy Belle", "Anne Clare", "Misty Lady", "Trya II", "Eastern Promise", "Shokwave", "Lady Grace", "Fish On!", "Tiger Lily", "Yorkshire Lass", "Heidi J", "Ocean Crusader", "Bon Amy", "Telmar II", "Starfish", "Torbay Belle", "Lady Ann", "Pace Arrow", "Saxon Lady", "Tuonela", "Hard Labour", "Jolly Roger", "Lady Helen", "Blue Mink", "Crusader 2", "Elegance", "Toplines", "Atlantic Blue", "Lady Lucy II", "Pride and Joy", "Three Sisters", "Lady Sarah", "Red 5", "Lady Of The Lake", "Nemesis", "Patrice II", "Great White", "Adelaide", "Osprey", "Yellowfin", "Mirage", "Aces High", "Kaimalino", "Tamesis", "Reel Action", "Bramblewick", "Flamer IV", "Top Cat III", "Lone Shark III", "Als Spirit", "Ailish", "Racheal Jane", "Swordfish", "Trio III", "Porbeagle", "Freedom", "Joint Venture", "Aldeburgh Angler", "Karyl-Anne", "Julie D", "Barracuda", "Blue Marlin", "Escapade", "Lily Lolo", "Wild Frontier", "Dawn Tide", "Dusk Diver", "Sunrise", "Osprey II", "Stoney Broke", "Natalie Kristen II", "Branscombe Pearl", "Striker", "Morning Breeze", "Oberon", "Moonshine", "Sportsmans Night", "Predator", "Venture", "Senija", "Kingfisher", "Mistress Linda", "Danse De Leau", "Swin Ranger", "M.F.V. Tamesis", "Foxy Lady", "Pioneer", "Restorick III", "Morgan James", "Dakala Mist", "Lady Tina", "Top Cat", "Michelle Mary", "Swallow IV", "Moonraker", "Pegasus", "Miss Patty", "Sea Fever", "She Likes It Rough 2", "Chrisanda", "Jubrae", "Thresher", "Bonwey", "Heartbeat", "Sarah Michelle", "Mac", "Sally Ann", "Duchess II", "Defiant", "Shalimar", "Orca", "Bayside", "Rose-Ann", "Rose Ann", "Caroline"])
    VERBS = ["charter", "skipper", "hire"]
    NOUNS_COMMON = ['charter']
    ADJECTIVE = ["inflatable"]
    PHRASES = ["seasick", "sea sick", 'puked', 'puke']


class Afloat(_NamedEntityBase):
    '''doc'''
    NOUNS_PROPERT = ['pescador']  #kayak and a boat
    NOUNS_COMMON = ["boat", "tub", "ship", "inflatable", "sail", "onboard", "drift", "anchor", 'slipway', 'tiller', 'starboard', 'aft', 'engine', 'outboard']
    VERBS = ["launch", "sail", "drift", 'steamed', 'motored', "launched", "sailed", "drifting", "anchored"]
    OTHER = ['prop']


class AfloatPrivate(_NamedEntityBase):
    '''doc'''
    NOUNS_COMMON = ['rib', 'oar', "dinghy", 'dory']
    NOUNS_PROPER = ['arvor', 'fibramar', 'treeve', 'quicksilver', 'fastliner', 'strikeline', 'leisurecat', 'mallon', 'beneteau', 'antares', 'reiver', 'saltram', 'colvic', 'navistar']
    PHRASES = ['Wilson Flyer', 'nord star', 'cougar cat', 'mitchell 22', 'sea line', 'orkney 520']
    VERBS = ['rowed']


class AfloatKayak(_NamedEntityBase):
    '''kayak'''
    ADJECTIVES = []
    NOUNS_COMMON = ["kayak", "yak", "prowler"]
    NOUNS_MODEL = ["tarpon", "trident", "scupper", "paddle", "fatyak", "dorado", "kaskazi", "teksport", "emotion", 'cuda', 'mirage', 'profish', 'outback', 'galaxy', 'wilderness', 'aquago', 'juntos']
    NOUNS_PROPER_MANUFACTURER = ['feelfree', 'hobbie', 'hobie', 'dorado', 'wilderness systems', 'wildernes systems', 'wido', 'riber', 'perception']
    NOUNS_MISC = ['railblaza']
    PHRASES = ['mirage outback', 'pelican catch', 'lifetime muskie', "fat yak"]
    VERBS = ['kayaking', 'paddled']

#    @classmethod
 #   def get(cls): #not verbs
  #      super().get(force_conjugate=False)


class Metrological(_NamedEntityBase):
    '''doc'''
    ADJECTIVES = ['heavy', 'big', 'small', 'huge', 'giant', 'tiny', 'little', 'loads']
    NOUNS_WEIGHT = ["pound", "pounds", "kilos", "kilo", "kilogram", "kilograms", "grams", "gram", "ounce", "ounces", "lbs", "ozs", "kg", "kgs"]
    NOUNS_LENGTH = ["meter", "meters", "metre", "metres", "cm", "cms", "centimeters", "centimeter", "centimetres", "centimetre", "inch", "inches", "foot", "feet"]


class SESSION(_NamedEntityBase):
    '''doc'''
    ADJECTIVES = []
    NOUNS_COMMON = ['session', 'trip']
    PHRASES = ["before low", "after low", "to low", "after high", "to high", "before high", "either side", "around high", "around low", "tide out", "tide down", "tide in", "tide up", "packed up", "went home"]
    VERBS = ["arrived", "started", "fished", "fishing", "hour", "flood", "ebb", 'caught', 'landed', 'unhooked', 'hooked', 'released', "fished", "fishing", "arrived", "started", "stopped", "ended", "left", 'casting', 'leave']


class TIME(_NamedEntityBase):
    '''doc'''
    ADJECTIVES = ['early', 'late']
    NOUNS_COMMON = ["hour", "mins", "minutes", "hrs", "minute", "hours", "min", 'morning', 'afternoon', 'noon', 'midday']
    PHRASES = ["p.m.", "a.m", 'pm', 'am']
    VERBS = []


class GearAngling(_NamedEntityBase):
    '''doc'''
    ADJECTIVES = []
    NOUNS_COMMON = ["rod", "beachcaster", "beachcasters", "rod", "bait", "plug", 'lure', 'spinner']
    NOUNS_PROPER = ['redgill']
    PHRASES = ['beach caster', 'beach casters', 'livebait', 'live bait', 'lrf', 'light rock fishing', 'feathering', 'red gill', 'red gills', 'savage gear']
    VERBS = ["spinning", 'cast']


class GearNoneAngling(_NamedEntityBase):
    '''doc'''
    PHRASES = ['spear gun', 'long lines', 'long line', 'purse net', 'seine']


class Species(_NamedEntityBase):
    '''spp'''
    NOUNS = list(_mssql.get_as_list('species_alias', 'species_aliasid', 'mmo', to_lower=True, clean=True)


class Dates(_NamedEntityBase):
    NOUNS_DAY = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', 'mond', 'tues', 'wedn', 'thur', 'frid', 'satu', 'sund', 'monda', 'tuesd', 'wedne', 'thurs', 'frida', 'satur', 'sunda', 'fr', 'tu', 'wds', 'mdy']
    NOUNS_MONTHS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec', 'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december', 'jan.', 'feb.', 'mar.', 'apr.', 'may', 'june', 'july', 'aug.', 'sept.', 'oct.', 'nov.', 'dec.', 'sep.', 'jul.', 'jun.']
    NOUNS_SEASONS = ['summer', 'winter', 'autumn', 'spring']