# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable,anomalous-backslash-in-string,no-self-use,unused-import,unused-argument
'''archive.org download spider for pages with multiple lnks only'''
import scrapy
from scrapy.spiders import CrawlSpider
#from scrapy.spiders import Spider

from imgscrape.items import Downloads
import funclib.iolib as iolib
from scrapy.utils.response import open_in_browser

PKL = 'C:/temp/mamelinks.pkl' #temp hack as getting links takes ages

user_ = 'Graham152'
email = 'archive@mistymountains.biz'
pass_ = 'GGM290471'

LOGIN_URL = 'https://archive.org/account/login'

class ArchiveDownloadSpider(CrawlSpider):
    '''spider'''
    name = "archive_org_mame"
    allowed_domains = ['archive.org']
    urls = ['https://ia601403.us.archive.org/11/items/mame0215_nochd']
    start_urls = ['https://archive.org/account/login']

    def parse(self, response):
        '''handler of generated urls'''
        return scrapy.FormRequest.from_response(response, formname='login-form', formdata={'username':email, 'password':pass_}, callback=self.parse_urls)

    def parse_urls(self, response):
        '''rou'''
        #could check response to see if login was successful
        for url in self.urls:
            yield scrapy.Request(url, self.parse_pages)

    def parse_pages(self, response):
        '''get links to all reports from boards
        '''
        #links = LinkExtractor(restrict_xpaths=('//a[contains(@href, "7z")]')).extract_links(response)
        links = iolib.unpickle(PKL)
        for link in links:
            dl = Downloads()
            dl['file_urls'] = [link.url]
            dl['filenames'] = [link.text]
            yield dl

        
   