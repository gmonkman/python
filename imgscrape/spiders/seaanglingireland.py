# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable,anomalous-backslash-in-string,no-self-use
'''sunnyrhyl spiders'''
import scrapy
from scrapy.spiders import Spider
from scrapy.linkextractors import LinkExtractor
from imgscrape.items import PostedImages
from funclib.stringslib import read_number

class SeaAnglingIrelandArchives(Spider):
    '''scrape images from angling addicts forum'''

    name = "seaanglingireland-archives"
    allowed_domains = ['sea-angling-ireland.org']
    start_urls = ['http://www.sea-angling-ireland.org/forum/viewforum.php?f=62',
                  'http://www.sea-angling-ireland.org/forum/viewforum.php?f=63']

    #start_urls = ['http://www.sea-angling-ireland.org/forum/viewforum.php?f=62']

    base_url = 'http://www.sea-angling-ireland.org/forum/'

    #get top level links to the boards for fishing reports by area

    def parse(self, response):
        '''get links to report boards
        yields:
        http://www.sea-angling-ireland.org/forum/viewforum.php?f=62
        http://www.sea-angling-ireland.org/forum/viewforum.php?f=62&start=50
        '''
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        urls = [response.url]
        posts_per_page = 50
        last_page = response.selector.xpath('//a[contains(@title, "Click to jump to page")]/strong[2]/text()').extract_first()
        last_page = read_number(last_page)
        if last_page > 1:
            for v in list(range((int(last_page) - 1) * posts_per_page, 0, -1*posts_per_page)):
                urls.append(urls[0] + '&start=%s' % v)

        for url in urls:
            yield scrapy.Request(url, callback=self.parse_pages)

    def parse_pages(self, response):
        '''get links to all reports from boards
        Response in:
        http://www.sea-angling-ireland.org/forum/viewforum.php?f=62&start=50

        Yields thread links:
        http://www.sea-angling-ireland.org/forum/viewtopic.php?f=62&t=48703
        '''
        links = LinkExtractor(restrict_xpaths=('//div[contains(@class,"forumbg")]//a[contains(@class, "topictitle")]')).extract_links(response)
        for link in links:
            yield scrapy.Request(link.url, callback=self.parse_images)

    def parse_images(self, response):
        '''for each board page post, extract images'''
        img = PostedImages()
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        img['image_urls'] = ['http://www.sea-angling-ireland.org/forum/' + x for x in response.xpath('//dl[contains(@class, "thumbnail")]//img/@src').extract()]
        return img


class SeaAnglingIrelandSpeciesHuntImageSpider(Spider):
    '''scrape images from angling addicts forum
    '''
    name = "seaanglingireland-specieshunt-pic"
    allowed_domains = ['anglingaddicts.co.uk']
    start_urls = ['http://www.sea-angling-ireland.org/forum/viewforum.php?f=30',
                  'http://www.sea-angling-ireland.org/forum/viewforum.php?f=65',
                  'http://www.sea-angling-ireland.org/forum/viewforum.php?f=53',
                  'http://www.sea-angling-ireland.org/forum/viewforum.php?f=54',
                  'http://www.sea-angling-ireland.org/forum/viewforum.php?f=44',
                  'http://www.sea-angling-ireland.org/forum/viewforum.php?f=45',
                  'http://www.sea-angling-ireland.org/forum/viewforum.php?f=55',
                  'http://www.sea-angling-ireland.org/forum/viewforum.php?f=56'
                  ]

    def parse(self, response):
        '''get all thread links on a page
        '''
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        links = LinkExtractor(restrict_xpaths='//div[@class="forumbg"]//a[contains(@class,"topictitle")]').extract_links(response)
        for link in links:
            yield scrapy.Request(link.url, callback=self.pages_in_thread, dont_filter=True)

    def pages_in_thread(self, response):
        '''loop through a thread
        response in:
        http://www.sea-angling-ireland.org/forum/viewtopic.php?f=30&t=14430

        yields:
        http://www.sea-angling-ireland.org/forum/viewtopic.php?f=30&t=14430
        http://www.sea-angling-ireland.org/forum/viewtopic.php?f=30&t=14430&start=20
        '''

        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        urls = [response.url] #first page is just the base post url
        posts_per_page = 25

        last_page = response.selector.xpath('//a[contains(@title, "Click to jump to page")]/strong[2]/text()').extract_first()
        if last_page:
            last_page = read_number(last_page)
        else:
            last_page = 0

        if last_page > 1:
            for v in list(range((int(last_page) - 1) * posts_per_page, 0, -1*posts_per_page)):
                urls.append(urls[0] + '&start=%s' % v)

        for url in urls:
            yield scrapy.Request(url, callback=self.images_in_threads, dont_filter=True)


    def images_in_threads(self, response):
        '''now we are in the root thread and we need to yield links for long threads like:
        response in:
        http://www.sea-angling-ireland.org/forum/viewtopic.php?f=30&t=14430&start=20
        '''
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        img = PostedImages()
        img['image_urls'] = ['http://www.sea-angling-ireland.org/forum/' + x for x in response.xpath('//dl[contains(@class,"attachbox")]//img/@src').extract()]
        return img
