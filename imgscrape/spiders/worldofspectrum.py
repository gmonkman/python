# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable,anomalous-backslash-in-string,no-self-use,unused-import
#This contains an example of
#looping ove a selector to extract all thread posts
'''spiders'''
import string
from copy import deepcopy

import scrapy
from scrapy.spiders import Spider
from scrapy.utils.response import open_in_browser
import imgscrape.items as _items
import imgscrape.pipelines as pipelines
import imgscrape.settings as settings
from funclib import stringslib

U = 'unknown'

ROM_TYPES = {'(perfect tzx tape image)':200, '((non-tzx) tap tape image)':100, '((non-tzx) z80 snapshot image)':50, '(tr-dos disk image)':25, '(zx interface 2 cartridge rom image dump)':13, '(+3 disk image)':12, U:1}
GAME_STATUS = {'':1, 'bugfix':100}
AVAILABILITY = {'missing in action!':0, 'available':1, 'distribution denied':0, 'never released':0, U:0}
ORIGIN_ALL = {'':0, 'original release':200, 're-release':50, U:0}

LANGUAGES_KEEP = ['english']

GAME_TYPES_ALL = {x.lower() for x in ["Adventure: Dungeon Crawl", "Adventure: Graphic", "Adventure: RPG", "Adventure: Text",
              "Arcade: Action", "Arcade: Adventure", "Arcade: Gang beat-em-up", "Arcade: Solo beat-em-up",
              "Arcade: Maze", "Arcade: Pinball", "Arcade: Platform", "Arcade: Race 'n' Chase",
              "Arcade: Shoot-em-up", "Arcade: Vehicle", "Board Game", "Card Game", "Gambling: Games",
              "Gambling: Utilities", "Puzzle", "Quiz", "Simulation", "Sport: Action", "Sport: Management",
              "Strategy: Management", "Strategy: War", "Tactical Combat", "Educational", "Business", "Domestic",
              "Industrial", "Programming: Assembler/Mcode", "Programming: BASIC", "Programming: General", "Utility: Astronomy",
              "Utility: Clip-Art", "Utility: Copy/Backup", "Utility: Database/Filing", "Utility: Electronics", "Utility: Fonts & UDGs",
              "Utility: Game Editor", "Utility: Graphics", "Utility: Hacker/Security", "Utility: I/O Handling",
              "Utility: Maths & Science", "Utility: Media Admin", "Utility: Music", "Utility: Prediction", "Utility: Sound/Speech",
              "Utility: Spreadsheet", "Utility: Visual/Screen", "Utility: Word Processor", "e-Book", "Music", "Demo", "Scene Demo",
              "Compilation", "Covertape", "Electronic Magazine"]}

GAME_TYPES_KEEP = {x.lower() for x in ["Adventure: Dungeon Crawl", "Adventure: Graphic", "Adventure: RPG", "Adventure: Text", "Arcade: Action", "Arcade: Adventure", "Arcade: Gang beat-em-up", "Arcade: Solo beat-em-up", "Arcade: Maze", "Arcade: Pinball", "Arcade: Platform", "Arcade: Race 'n' Chase", "Arcade: Shoot-em-up", "Arcade: Vehicle", "Board Game", "Card Game", "Gambling: Games", "Gambling: Utilities", "Puzzle", "Quiz", "Simulation", "Sport: Action", "Sport: Management", "Strategy: Management", "Strategy: War", "Tactical Combat"]}


LETTERS = settings.WorldOfSpectrumSettings.letters






class Game():
    '''game cls'''
    def __init__(self, full_title, year_released=U, publisher=U, machine_type=U, language=U, game_type=U, score=0, votes=0, availability=U, original_publication=U, letter=U, download_weight=None, rom_type='', is_mod=0, url='', origin=U):
        assert isinstance(full_title, str)
        if not isinstance(full_title, str): raise ValueError('Full title was not a string')
        if full_title is None: raise ValueError('Full title was None')
        self.full_title = full_title.lower()
        self.year_released = year_released
        self.publisher = publisher.lower()
        self.machine_type = machine_type.lower()
        self.language = language.lower()
        self.original_publication = original_publication.lower()
        self.game_type = game_type.lower()
        self.score = score
        self.votes = votes
        self.availability = availability.lower()
        self.letter = letter.lower()
        self.download_weight = download_weight
        self.rom_type = rom_type.lower()
        self.is_mod = is_mod
        self.url = url
        self.origin = origin
        self.score_weight = 0


class WOSDataOnly(Spider):
    '''spider'''
    name = "WOSData"
    source = 'www.worldofspectrum.org'
    allowed_domains = ['www.worldofspectrum.org']
    base_url = 'https://www.worldofspectrum.org'
    start_urls = ['%s%s.html' % ('https://www.worldofspectrum.org/games/', x) for x in LETTERS]    

    def parse(self, response):
        '''generate links to pages in a board        '''
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        assert len(LETTERS) == len(WOSDataOnly.start_urls), 'Setup list lengths DO NOT match'  
        for i, url in enumerate(WOSDataOnly.start_urls):
            yield scrapy.Request(url, callback=self.crawl_letters, dont_filter=False, meta={'letter':LETTERS[i]})


    def crawl_letters(self, response):
        '''crawl'''
        letter = response.meta.get('letter')
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        hrefs = response.selector.xpath('.//pre//a/@href').extract()
        hrefs = [response.urljoin(x) for x in hrefs]
        for i, href in enumerate(hrefs):
            yield scrapy.Request(href, callback=self.crawl_game, dont_filter=True, meta={'letter':letter})


    def crawl_game(self, response):
        '''crawl'''
        readstr_ = lambda x: x.lower() if x else ''
        letter = response.meta.get('letter')
         
        G = Game(response.selector.xpath('(//body/table)[3]/tr[td//text()[contains(., "Full title")]]/td[2]//text()').extract()[0])
        if G.full_title.lower() == '[mod]':
            G.full_title = response.selector.xpath('(//body/table)[3]/tr[td//text()[contains(., "Full title")]]/td[2]//text()').extract()[1]
        
        try:
            G.is_mod = any(response.selector.xpath('//*[text()[contains(., "[MOD]")]]'))
        except:
            G.is_mod = False
        G.is_mod = int(G.is_mod)

        try:
            G.availability = readstr_(response.selector.xpath('(//body/table)[3]/tr[td//text()[contains(., "Availability")]]/td[2]//text()').extract()[0])
        except:
            G.availability = ''

        try:
            G.game_type = readstr_(response.selector.xpath('(//body/table)[3]/tr[td//text()[contains(., "Type")]]/td[2]//text()').extract()[0])
        except:
            G.game_type = ''

        try:
            G.language = readstr_(response.selector.xpath('(//body/table)[3]/tr[td//text()[contains(., "Message language")]]/td[2]//text()').extract()[0])
        except:
            G.language = ''

        try:
            G.machine_type = readstr_(response.selector.xpath('(//body/table)[3]/tr[td//text()[contains(., "Machine type")]]/td[2]//text()').extract()[0])
        except:
            G.machine_type = ''

        try:
            G.publisher = readstr_(response.selector.xpath('(//body/table)[3]/tr[td//text()[contains(., "Publisher")]]/td[2]//text()').extract()[0])
        except:
            G.publisher = ''

        try:
            G.original_publication = readstr_(response.selector.xpath('(//body/table)[3]/tr[td//text()[contains(., "Original publication")]]/td[2]//text()').extract()[0])
        except:
            G.original_publication = ''

        try:
            G.score = stringslib.numbers_in_str2(readstr_(response.selector.xpath('(//body/table)[3]/tr[td//text()[contains(., "Score")]]/td[2]//text()').extract()[0]))[0]
        except:
            G.score = -1
        if not isinstance(G.score, float): G.score = -1

        try:
            G.votes = stringslib.numbers_in_str(readf(response.selector.xpath('(//body/table)[3]/tr[td//text()[contains(., "Score")]]/td[2]//text()').extract()[1]), type_=int)[0]
        except:
            G.votes = -1
        if not isinstance(G.votes, (float, int)): G.votes = -1

        try:
            G.year_released = stringslib.numbers_in_str(readstr_(response.selector.xpath('(//body/table)[3]/tr[td//text()[contains(., "Year of release")]]/td[2]//text()').extract()[0]), type_=int)[0]
        except:
            G.year_released = 9999
        if not isinstance(G.year_released, (float, int)): G.year_released = 9999
        
        z80_bonus = 0
        try:
            encoding_sheme = any(readstr_(response.selector.xpath('//*[text()[contains(., "Encoding scheme")]]')))
        except:
            encoding_sheme = False
        if encoding_sheme: z80_bonus = 9999
        
        # Could also ignore Original publication != 'Commercial'
        Gs = []
        if not any(response.selector.xpath('//*[text()[contains(., "Download and play links")]]')):
            G.download_weight = 0
            G.rom_type = ''
            Gs.append(deepcopy(G))
        else:
            #now read all the rom types, rows here is ofcourse a list of scrapy.selector.unified.Selector
            rows = response.selector.xpath('(//body/table)[4]/tr')
            if not G.game_type in GAME_TYPES_KEEP:
                G.download_weight = 0
            elif G.language not in ('english', '', U):
                G.download_weight = 0
            elif bool(G.is_mod):
                G.download_weight = 0
            elif G.original_publication != 'commercial':
                G.download_weight = 0
            elif G.year_released > 1993 or not G.year_released:
                G.download_weight = 0

            if G.download_weight == 0:
                G.url = 'n/a'
                G.rom_type = 'n/a'
                G.origin = 'n/a'
                Gs.append(deepcopy(G))
            else:
                if rows:
                    for i, r in enumerate(rows[1:]):  #first row is header
                        Gs.append(deepcopy(G))
                        Gs[i].url = response.urljoin(readf(r.xpath('./td[3]//@href').extract()[0]))
                        Gs[i].rom_type = readf(r.xpath('./td[5]//text()').extract()[0])
                        Gs[i].origin = readf(r.xpath('./td[6]//text()').extract())
                        set_download_weight(Gs[i], z80_bonus)
                        Gs[i].download_weight = Gs[i].download_weight if Gs[i].url else 0 #if we havent got a link, force score to 0
                        set_score_weight(Gs[i])
                else:
                    G.download_weight = 0
                    G.url = 'No links'
                    G.rom_type = 'No links'
                    G.origin = 'No links'
                    Gs.append(deepcopy(G))


        for Gg in Gs:
            L = _items.WOSGameLdr(item=_items.WOSGame(), response=response)

            #loop through all user members of G, add as item value, setting the value - don't have to change if add new values
            attrs = [attr for attr in dir(Gg) if not callable(getattr(Gg, attr)) and not attr.startswith("__")]
            for a in attrs:
                s = getattr(Gg, a)
                print('%s %s' % (a,s))
                L.add_value(a, getattr(Gg, a))
        
            I = L.load_item()
            yield I






#HELPER  FUNCS
def readf(v):
    '''readf'''
    if isinstance(v, str):
        return v.lower()

    if isinstance(v, (int, float, bool)):
        return v

    if isinstance(v, (list, tuple, set)):
        if not v:
            return ''

        r = v[0]
        if isinstance(r, str):
            return r.lower()

        if isinstance(r, (int, float, bool)):
            return r

    return ''


def set_download_weight(G, z80_bonus):
    '''ByREF. Set the download_weight for instance of Game
    z80_bonus is used if there is an encoding scheme on the game'''
    assert isinstance(G, Game)
    G.download_weight = 0
    if G.rom_type == '((non-tzx) z80 snapshot image)': G.download_weight += z80_bonus
    G.download_weight += ROM_TYPES.get(G.rom_type, 1)
    G.download_weight += ORIGIN_ALL.get(G.origin, 1)
    G.download_weight -= len(G.url.split('/')[-1]) #favour shorter titles


def set_score_weight(G):
    '''how good is the game'''
    assert isinstance(G, Game)
    try:
        G.score_weight = G.score * G.votes
    except:
        G.score_weight = -1