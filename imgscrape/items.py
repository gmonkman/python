# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable,too-many-ancestors
'''items'''
import scrapy

class PostedImages(scrapy.Item):
    '''postedimages item'''
    image_urls = scrapy.Field()
    images = scrapy.Field()
