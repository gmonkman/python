# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable, no-self-use, unused-argument
'''pipelines'''
from warnings import warn as _warn
from scrapy.http import Request
from scrapy.exceptions import DropItem as _DropItem
import imgscrape.settings as _settings

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
    def open_spider(self, spider):
        '''open'''
        pass

    def close_spider(self, spider):
        '''close'''
        _mmodb.close_engine()

    def process_item(self, item, spider):
        '''process'''

        if _settings.MSSQL_DUPLICATE_CHECK:
            if item.get('url'):
                if check_for_dup(item['url']):
                    raise _DropItem('Custom UGCWriter Pipeline: Duplicate item found for url "%s"' % item['url'])
            else:
                _warn('UGCWriter Warning: URL was empty')

        if not item.get('txt'):
            raise _DropItem('UGCWriter Warning: No body text for url "%s"' % item['url'][0])

        if len(item['txt']) < _settings.MIN_BODY_LENGTH:
            raise _DropItem('UGCWriter Pipeline: Dropped item, body length < %s' % _settings.MIN_BODY_LENGTH)

        UGC = _Ugc(**dict(item))
        _mmodb.SESSION.add(UGC)
        try:
            _mmodb.SESSION.commit()
        except Exception as e:
            try:
                _warn(e)
                _mmodb.SESSION.rollback()
                _mmodb.SESSION.expunge_all()
            except:
                pass
        return item



def check_for_dup(url):
    '''check for dup records by url'''
    return _mmodb.SESSION.query(_Ugc).filter(_Ugc.url == url).first()
