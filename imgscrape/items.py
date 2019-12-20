# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable,too-many-ancestors
'''items'''
from collections import OrderedDict as _OD
from types import FunctionType as _FT
from scrapy import Field as _Field
from scrapy import Item as _Item
import scrapy.loader as _loader
import scrapy.loader.processors as _processors


from imgscrape.processors import Clean_xa0 as _Clean_xa0
from imgscrape.processors import CleanStrict as _CleanStrict
from imgscrape.processors import VoteForOrAgainst as _VoteForOrAgainst
import imgscrape.processors as _myprocs



#https://stackoverflow.com/questions/52714584/how-to-import-scrapy-item-keys-in-the-correct-order
#force order of item fields in output
#tried this didnt seem to work, object does not support item assignment
class StaticOrderHelper(type):
    # Requires Python3
    def __prepare__(name, bases, **kwargs):
        return _OD()

    def __new__(mcls, name, bases, namespace, **kwargs):
        namespace['_field_order'] = [
                k
                for k, v in namespace.items()
                if not k.startswith('__') and not k.endswith('__')
                    and not isinstance(v, (_FT, classmethod, staticmethod))
        ]
        return type.__new__(mcls, name, bases, namespace, **kwargs)


# TakeFirst, MapCompose, Join
class PostedImages(_Item):
    '''postedimages item'''
    image_urls = _Field()
    images = _Field()



#Downloads
class Downloads(_Item):
    '''postedimages item'''
    file_urls = _Field()
    filenames = _Field()


class DownloadsLdr(_loader.ItemLoader):
    '''ldr'''
    default_item_class = Downloads
    default_output_processor = _processors.TakeFirst()



 


#World of Spectrum
#class WOSGame(metaclass=StaticOrderHelper):
class WOSGame(_Item):
    '''item'''
    game_url = _Field()
    full_title = _Field()
    availability = _Field()

    machine_type = _Field()
    
    language = _Field()
    is_mod = _Field()

    game_type = _Field()
    
    publisher = _Field()
    year_released = _Field()

    original_publication = _Field()
    origin = _Field()
    rom_type = _Field()
    
    url = _Field()
    download_weight = _Field()
    
    score = _Field()
    votes = _Field()
    score_weight = _Field()
    

class WOSGameLdr(_loader.ItemLoader):
    '''item loader
    '''
    default_input_processor = _myprocs.ListToValue() #always a lst, unless we takefirst
    default_output_processor = _myprocs.ListToValue()





#MMO Work
class ForumUGC(_Item):
    '''item for mmo user generated content database entity'''
    source = _Field()
    published_date = _Field()
    board = _Field()
    content_identifier = _Field()
    who = _Field()
    txt = _Field()
    url = _Field()
    title = _Field()
    boat = _Field()
    platform_hint = _Field()
    source_platform = _Field()
    charter_port = _Field()



class CBUKBoat(_Item):
    '''item for cbuk boat details page 
    e.g. http://www.charterboats-uk.co.uk/england/
    '''
    boat = _Field()
    harbour = _Field()
    distance = _Field()
    passengers = _Field()
    

class CBUKBoatLdr(_loader.ItemLoader):
    '''item ldr'''
    default_input_processor = _myprocs.ListToValue() #always a lst, unless we takefirst
    default_output_processor = _myprocs.ListToValue()

    txt_in = _myprocs.HTML2Txt()
    txt_out = _myprocs.ListToValue()

    title_in = _myprocs.Clean2Ascii()
    title_out = _myprocs.ListToValue()

 

class AnglingAddictsMMOLdr(_loader.ItemLoader):
    '''item loader
    '''
    default_input_processor = _myprocs.ListToValue() #always a lst, unless we takefirst
    default_output_processor = _myprocs.ListToValue()

    txt_in = _myprocs.HTML2Txt()
    txt_out = _myprocs.ListToValue()

    published_date_in = _myprocs.PostDateAsISO(date_fmt='%d %b %Y %H:%M') #get as iso format for sql server
    published_date_out = _myprocs.ListToValue()

    who_in = _myprocs.Encode64()
    who_out = _myprocs.ListToValue()
    title_in = _myprocs.Clean2Ascii()
    title_out = _myprocs.ListToValue()


class WirralSeaFishingLdr(_loader.ItemLoader):
    '''item loader
    '''
    default_input_processor = _myprocs.ListToValue() #always a lst, unless we takefirst
    default_output_processor = _myprocs.ListToValue()

    txt_in = _myprocs.HTML2Txt()
    txt_out = _myprocs.ListToValue()

    published_date_in = _myprocs.PostDateAsISO(date_fmt='%a %b %d %Y %H:%M %p') #'Sat Jan 12, 2019 06:54 PM' see http://strftime.org/, the processor removes ,
    published_date_out = _myprocs.ListToValue()

    who_in = _myprocs.Encode64()
    who_out = _myprocs.ListToValue()
    title_in = _myprocs.Clean2Ascii()
    title_out = _myprocs.ListToValue()



class TotalFishingLdr(_loader.ItemLoader):
    '''item loader
    '''
    DATE_FMT = '%d/%m/%Y at %H:%M %p'

    default_input_processor = _myprocs.ListToValue() #always a lst, unless we takefirst
    default_output_processor = _myprocs.ListToValue()

    txt_in = _myprocs.HTML2Txt()
    txt_out = _myprocs.ListToValue()

    published_date_in = _myprocs.PostDateAsISO(date_fmt='%d/%m/%Y at %H:%M %p') #18/03/2016 at 9:55 pm see http://strftime.org/
    published_date_out = _myprocs.ListToValue()

    who_in = _myprocs.Encode64()
    who_out = _myprocs.ListToValue()

    title_in = _myprocs.Clean2Ascii()
    title_out = _myprocs.ListToValue()


class WorldSeaFishingLdr(_loader.ItemLoader):
    '''item loader
    '''
    default_input_processor = _myprocs.ListToValue() #always a lst, unless we takefirst
    default_output_processor = _myprocs.ListToValue()

    txt_in = _myprocs.HTML2Txt()
    txt_out = _myprocs.ListToValue()

    published_date_in = _myprocs.PostDateAsISO(date_fmt='%b %d %Y at %H:%M %p') #'Mar 18, 2012 at 9:53 AM' see http://strftime.org/ - NOTE the comma is cleaned
    published_date_out = _myprocs.ListToValue()

    who_in = _myprocs.Encode64()
    who_out = _myprocs.ListToValue()
    title_in = _myprocs.Clean2Ascii()
    title_out = _myprocs.ListToValue()



class SeaFishingOrgLdr(_loader.ItemLoader):
    '''item loader
    '''
    default_input_processor = _myprocs.ListToValue() #always a lst, unless we takefirst
    default_output_processor = _myprocs.ListToValue()

    txt_in = _myprocs.HTML2Txt()
    txt_out = _myprocs.ListToValue()

    published_date_in = _myprocs.PostDateAsISO(date_fmt='%a %b %d %Y %H:%M %p') #'Wed Dec 30, 2015 4:53 pm' see http://strftime.org/ - NOTE the comma is cleaned
    published_date_out = _myprocs.ListToValue()

    who_in = _myprocs.Encode64()
    who_out = _myprocs.ListToValue()
    title_in = _myprocs.Clean2Ascii()
    title_out = _myprocs.ListToValue()


class SolentFishingForumsLdr(_loader.ItemLoader):
    '''item loader
    '''
    default_input_processor = _myprocs.ListToValue() #always a lst, unless we takefirst
    default_output_processor = _myprocs.ListToValue()

    txt_in = _myprocs.HTML2Txt()
    txt_out = _myprocs.ListToValue()

    published_date_in = _myprocs.PostDateAsISO(date_fmt='%d %B %Y %H:%M%p') #07 February 2008 6:12pm
    published_date_out = _myprocs.ListToValue()

    who_in = _myprocs.Encode64()
    who_out = _myprocs.ListToValue()
    title_in = _myprocs.Clean2Ascii()
    title_out = _myprocs.ListToValue()


class SouthWestSeaFishingLdr(_loader.ItemLoader):
    '''item loader
    '''
    default_input_processor = _myprocs.ListToValue() #always a lst, unless we takefirst
    default_output_processor = _myprocs.ListToValue()

    txt_in = _myprocs.HTML2Txt()
    txt_out = _myprocs.ListToValue()

    published_date_in = _processors.Identity()  #Cleaned in the scraper
    published_date_out = _myprocs.ListToValue()

    who_in = _myprocs.Encode64()
    who_out = _myprocs.ListToValue()
    title_in = _myprocs.Clean2Ascii()
    title_out = _myprocs.ListToValue()


class AnglersNetLdr(_loader.ItemLoader):
    '''item loader
    '''
    default_input_processor = _myprocs.ListToValue() #always a lst, unless we takefirst
    default_output_processor = _myprocs.ListToValue()

    txt_in = _myprocs.HTML2Txt()
    txt_out = _myprocs.ListToValue()

    published_date_in = _processors.Identity()  #Cleaned in the scraper
    published_date_out = _myprocs.ListToValue()

    who_in = _myprocs.Encode64()
    who_out = _myprocs.ListToValue()
    title_in = _myprocs.Clean2Ascii()
    title_out = _myprocs.ListToValue()


class CharterBoatUKLdr(_loader.ItemLoader):
    '''item loader
    '''
    default_input_processor = _myprocs.ListToValue() #always a lst, unless we takefirst
    default_output_processor = _myprocs.ListToValue()

    txt_in = _myprocs.HTML2Txt()
    txt_out = _myprocs.ListToValue()

    published_date_in = _myprocs.PostDateAsISO(date_fmt='%d/%m/%Y') #'Sat Jan 12, 2019 06:54 PM' see http://strftime.org/, the processor removes ,  #Cleaned in the scraper
    published_date_out = _myprocs.ListToValue()

    title_in = _myprocs.Clean2Ascii()
    title_out = _myprocs.ListToValue()
    

class NESALdr(_loader.ItemLoader):
    '''item loader
    '''
    default_input_processor = _myprocs.ListToValue() #always a lst, unless we takefirst
    default_output_processor = _myprocs.ListToValue()

    txt_in = _myprocs.HTML2Txt()
    txt_out = _myprocs.ListToValue()

    published_date_in = _myprocs.PostDateAsISO(date_fmt='%d-%m-%Y %H:%M %p') #06-12-2018, 01:05 AM
    published_date_out = _myprocs.ListToValue()

    who_in = _myprocs.Encode64()
    who_out = _myprocs.ListToValue()
    title_in = _myprocs.Clean2Ascii()
    title_out = _myprocs.ListToValue()


class Ports(_Item):
    '''ports'''
    name = _Field()
    latitude = _Field()
    longitude = _Field()
    country = _Field()





#Fox Stuff
class ldrMPDetails(_loader.ItemLoader):
    '''itemloader for item
    '''
    default_input_processor = _processors.Identity()
    default_output_processor = _processors.Identity()

    constituency_in = _processors.TakeFirst()
    party_in = _processors.TakeFirst()

    surname_in = _Clean_xa0()
    firstname_in = _Clean_xa0()


class policy_vote_ldr(_loader.ItemLoader):
    '''policy vote loader'''
    default_input_processor = _processors.Identity()
    default_output_processor = _processors.Identity()

    policy_in = _CleanStrict()
    stance_in = _VoteForOrAgainst()


class policy_vote(_Item):
    '''policy vote, should handle all policy stances'''
    name = _Field() #this is effectively the key
    policy = _Field()
    stance = _Field()


class itmMPDetails(_Item):
    '''details'''
    surname = _Field()
    firstname = _Field()
    party = _Field()
    constituency = _Field()
