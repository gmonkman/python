# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable, no-self-use, unused-argument
'''pipelines'''
from warnings import warn as _warn
from scrapy.http import Request
from scrapy.exceptions import DropItem as _DropItem

import mmodb as _mmodb
from mmodb.model import Ugc as _Ugc


class WSFImagesPipeline():
    '''pipeline'''
    def process_item(self, item, spider):
        '''process'''
        return item

    def get_media_requests(self, item, info):
        '''get'''
        for image_url in item['image_urls']:
            yield Request(image_url)



class UGCWriter():
    '''ugc writer'''

    def __init__(self, check_for_dups=True):
        '''init'''
        self.check_for_dups = check_for_dups
        pass

    def open_spider(self, spider):
        '''open'''
        pass

    def close_spider(self, spider):
        '''close'''
        _mmodb.close_engine()

    def process_item(self, item, spider):
        '''process'''

        if check_for_dup(item['url']):
            raise _DropItem('Duplicate item found for url "%s"' % item['url'][0])

        if not item['txt']:
            raise _DropItem('No body text for url "%s"' % item['url'][0])

        UGC = _Ugc(**dict(item))
        _mmodb.SESSION.add(UGC)
        try:
            _mmodb.SESSION.commit()
        except Exception as e:
            _warn(e)
            _mmodb.SESSION.expunge_all()

        return item


def check_for_dup(url):
    '''check for dup records by url'''
    return _mmodb.SESSION.query(_Ugc).filter(_Ugc.url == url).first()
