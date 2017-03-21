# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable,anomalous-backslash-in-string,no-self-use
'''angling addicts spiders'''
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from imgscrape.items import PostedImages

from funclib.stringslib import read_number

class AnglingAddictsImageSpider(CrawlSpider):
    '''scrape images from angling addicts forum'''
    name = "anglingaddicts-pic"
    allowed_domains = ['anglingaddicts.co.uk']
    start_urls = ['http://www.anglingaddicts.co.uk/forum/shore-fishing-reports.html']

    #get top level links to the boards for fishing reports by area
    rules = (
        Rule(LinkExtractor(allow=('reports\.html', )), callback='parse_subforums'),
    )

    def parse_subforums(self, response):
        '''get links to report boards'''
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        urls = [response.url]
        posts_per_page = 25
        last_page = response.selector.xpath('//a[contains(@title, "Click to jump to page")]/strong[2]/text()').extract_first()
        last_page = read_number(last_page)
        if last_page > 0:
            for v in list(range((int(last_page) - 1) * posts_per_page, 0, -1*posts_per_page)):
                urls.append(urls[0].replace('.html', '') + '-%s.html' % v)

            for url in urls:
                yield scrapy.Request(url, callback=self.parse_pages)

    def parse_pages(self, response):
        '''get links to all reports from boards'''
        links = LinkExtractor(restrict_xpaths=('//div[contains(@class,"forumbg")]//a[contains(@class, "topictitle")]')).extract_links(response)
        for link in links:
            yield scrapy.Request(link.url, callback=self.parse_images)

    def parse_images(self, response):
        '''for each board page post, extract images'''
        img = PostedImages()
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        img['image_urls'] = list(response.xpath('//img[contains(@alt, "Image")]/@src').extract())
        return img
