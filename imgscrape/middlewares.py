#pylint: skip-file
import json as _json
from datetime import datetime as _dt

from scrapy import Request
from scrapy.http import Response
from scrapy.exceptions import IgnoreRequest



class UnhandledIgnoreRequest(IgnoreRequest):
    pass


class WaybackMachine:
    cdx_url_template = ('http://web.archive.org/cdx/search/cdx?url={url}&output=json&fl=timestamp,original,statuscode,digest')
    snapshot_url_template = 'http://web.archive.org/web/{timestamp}id_/{original}'

    def __init__(self, crawler):
        self.crawler = crawler
        # read the settings
        self.time_range = crawler.settings.get('WAYBACK_MACHINE_TIME_RANGE')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)