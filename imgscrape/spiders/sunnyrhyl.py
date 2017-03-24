# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable,anomalous-backslash-in-string,no-self-use
'''sunnyrhyl spiders'''
import scrapy
from scrapy.spiders import Spider
from scrapy.linkextractors import LinkExtractor
from imgscrape.items import PostedImages
from funclib.stringslib import read_number

class SunnyRhylSpider(Spider):
    '''scrape images from sunnyrhyl forum'''

    name = "sunnyrhyl-pics"
    allowed_domains = ['forumotion.com']
    start_urls = ['http://sunnyrhyl.forumotion.com/f1-sea-fishing-shore-reports',
                  'http://sunnyrhyl.forumotion.com/f4-charter-boat-reports',
                  'http://sunnyrhyl.forumotion.com/f16-small-boats-section',
                  'http://sunnyrhyl.forumotion.com/f14-species-hunt']

    base_url = 'http://sunnyrhyl.forumotion.com/'

    def parse(self, response):
        '''generate links to pages in a board
        yields:
        http://sunnyrhyl.forumotion.com/f16-small-boats-section
        http://sunnyrhyl.forumotion.com/f16p50-small-boats-section'''
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        urls = [response.url] #first page is just the base post url

        parts = str(response.url.split('/')[-1])
        parts = parts.split('-', 1)
        posts_per_page = 50

        pagination = response.selector.xpath('//table[contains(@class,"forumline")]//td[contains(@colspan,"7")]/span/a/text()').extract()
        if pagination:
            last_page = int(read_number(pagination[-1]))
        else:
            last_page = 0

        if last_page > 1:
            for v in list(range((int(last_page) - 1) * posts_per_page, 0, -1*posts_per_page)):
                s = self.base_url + parts[0] + 'p' + str(v) + '-' + parts[1]
                urls.append(s)

        for url in urls:
            yield scrapy.Request(url, callback=self.crawl_board_threads, dont_filter=True)

    def crawl_board_threads(self, response):
        '''response in http://sunnyrhyl.forumotion.com/f16-small-boats-section
        yields board thread links: http://sunnyrhyl.forumotion.com/t8311-rhods-species-hunt-2017'''
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        links = LinkExtractor(restrict_xpaths='//div[@class="topictitle"]//a[@class="topictitle"]').extract_links(response)
        for link in links:
            s = response.urljoin(link.url)
            yield scrapy.Request(s, callback=self.crawl_threads)

    def crawl_threads(self, response):
        '''open a report thread and iterate report thread pages, ie if more than 25 responses to a thread
        Input response:http://sunnyrhyl.forumotion.com/t8311-rhods-species-hunt-2017

        yields:
        http://sunnyrhyl.forumotion.com/t7682-zippie-s-2016-species-hunt
        http://sunnyrhyl.forumotion.com/t7682p25-zippie-s-2016-species-hunt
        '''
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        urls = [response.url] #first page is just the base post url
        posts_per_page = 25

        lnk = urls[0]
        parts = str(response.url.split('/')[-1])
        parts = parts.split('-', 1)

        pagination = response.selector.xpath('//table[contains(@class,"forumline")]//td[contains(@class,"row1 pagination")]/span/a/text()').extract()
        if pagination:
            last_page = int(read_number(pagination[-1]))
        else:
            last_page = 0

        if last_page > 1:
            for v in list(range((int(last_page) - 1) * posts_per_page, 0, -1*posts_per_page)):
                s = self.base_url + parts[0] + 'p' + str(v) + '-' + parts[1]
                urls.append(s)

        for url in urls:
            yield scrapy.Request(url, callback=self.extract_images, dont_filter=True)

    def extract_images(self, response):
        '''get image links to all reports and their additional pages:
        '''
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        img = PostedImages()
        img['image_urls'] = response.xpath('//div[@class="postbody"]//img/@src').extract()
        return img
