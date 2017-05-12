# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable,too-many-ancestors
'''items'''
from scrapy import Field as _Field
from scrapy import Item as _Item
import scrapy.loader as _loader
import scrapy.loader.processors as _processors


from imgscrape.processors import Clean_xa0 as _Clean_xa0
from imgscrape.processors import CleanStrict as _CleanStrict
from imgscrape.processors import VoteForOrAgainst as _VoteForOrAgainst


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
