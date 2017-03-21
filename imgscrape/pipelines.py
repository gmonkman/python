# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable, no-self-use, unused-argument
'''pipelines'''
from scrapy.http import Request

class WSFImagesPipeline(object):
    '''pipeline'''
    def process_item(self, item, spider):
        '''process'''
        return item

    def get_media_requests(self, item, info):
        '''get'''
        for image_url in item['image_urls']:
            yield Request(image_url)
