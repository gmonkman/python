# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable,too-many-ancestors
'''items'''
from scrapy import Field as _Field
from scrapy import Item as _Item
import scrapy.loader as _loader
import scrapy.loader.processors as _processors


from imgscrape.processors import Clean_xa0 as _Clean_xa0
from imgscrape.processors import CleanStrict as _CleanStrict
from imgscrape.processors import VoteForOrAgainst as _VoteForOrAgainst
import imgscrape.processors as _myprocs

# TakeFirst, MapCompose, Join

class PostedImages(_Item):
    '''postedimages item'''
    image_urls = _Field()
    images = _Field()



class itmMPDetails(_Item):
    '''details'''
    surname = _Field()
    firstname = _Field()
    party = _Field()
    constituency = _Field()




#MMO Work
class ForumUGC(_Item):
    '''item for mmo user generated content database entity
    '''
    source = _Field()
    published_date = _Field()
    board = _Field()
    content_identifier = _Field()
    who = _Field()
    txt = _Field()
    url = _Field()
    title = _Field()

class AnglingAddictsMMOLdr(_loader.ItemLoader):
    '''item loader
    '''
    default_input_processor = _myprocs.ListToValue() #always a lst, unless we takefirst
    default_output_processor = _myprocs.ListToValue()

    txt_in = _myprocs.HTML2Txt()
    txt_out = _myprocs.ListToValue()

    _myprocs.PostDateAsISO.DATE_FMT = '%d %b %Y, %H:%M' #see http://strftime.org/
    published_date_in = _myprocs.PostDateAsISO() #get as iso format for sql server
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

    _myprocs.PostDateAsISO.DATE_FMT = '%a %b %d, %Y %H:%M %p'  #'Sat Jan 12, 2019 06:54 PM' see http://strftime.org/
    published_date_in = _myprocs.PostDateAsISO() #get as iso format for sql server
    published_date_out = _myprocs.ListToValue()

    who_in = _myprocs.Encode64()
    who_out = _myprocs.ListToValue()
    title_in = _myprocs.Clean2Ascii()
    title_out = _myprocs.ListToValue()



class TotalFishingLdr(_loader.ItemLoader):
    '''item loader
    '''
    default_input_processor = _myprocs.ListToValue() #always a lst, unless we takefirst
    default_output_processor = _myprocs.ListToValue()

    txt_in = _myprocs.HTML2Txt()
    txt_out = _myprocs.ListToValue()

    _myprocs.PostDateAsISO.DATE_FMT = '%d/%m/%Y at %H:%M %p'  #18/03/2016 at 9:55 pm see http://strftime.org/
    published_date_in = _myprocs.PostDateAsISO() #get as iso format for sql server
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

    _myprocs.PostDateAsISO.DATE_FMT = '%b %d, %Y at %H:%M %p'  #'Mar 18, 2012 at 9:53 AM' see http://strftime.org/
    published_date_in = _myprocs.PostDateAsISO() #get as iso format for sql server
    published_date_out = _myprocs.ListToValue()

    who_in = _myprocs.Encode64()
    who_out = _myprocs.ListToValue()
    title_in = _myprocs.Clean2Ascii()
    title_out = _myprocs.ListToValue()

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
