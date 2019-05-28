# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable, no-self-use, unused-argument
'''pipelines'''
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

    def __init__(self, batch_sz=100, check_for_dups=True):
        '''init'''
        self.batch_sz = batch_sz
        self.add_cnt = 0
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
        if self.check_for_dups:
            if _mmodb.SESSION.query(_Ugc).filter(_Ugc.url == item['url'][0]).first():
                raise _DropItem('Duplicate item found for url "%s"' % item['url'][0])

        UGC = _Ugc(**dict(item))
        _mmodb.SESSION.add(UGC)
        self.add_cnt += 1
        if self.add_cnt % self.batch_sz == 0:
            self.add_cnt = 0
            _mmodb.SESSION.commit()
        return item
