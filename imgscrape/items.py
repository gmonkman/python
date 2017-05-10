# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable,too-many-ancestors
'''items'''
from scrapy import Field as _Field
from scrapy import Item as _Item
import scrapy.loader as _loader
import scrapy.loader.processors as _processors


from imgscrape.processors import Clean_xa0 as _Clean_xa0

import funclib.stringslib as _stringslib
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
    foxvote = _Field()


class ldrMPDetails(_loader.ItemLoader):
    '''itemloader for item
    '''
    default_input_processor = _processors.Identity()
    default_output_processor = _processors.Identity()

    constituency_in = _processors.TakeFirst()
    party_in = _processors.TakeFirst()

    surname_in = _Clean_xa0()
    firstname_in = _Clean_xa0()
