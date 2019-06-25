# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable,anomalous-backslash-in-string,no-self-use
'''spiders'''
import scrapy

from scrapy.spiders import Spider
from scrapy.linkextractors import LinkExtractor
import imgscrape.items as _items
from imgscrape.pipelines import check_for_dup
from imgscrape import settings



class SeaFishingOrgReportsSpider(Spider):
    '''scrape reports from angling addicts forum
    '''
    name = "seafishingorg"
    source = 'www.sea-fishing.org'
    allowed_domains = ['sea-fishing.org']
    start_urls = ['https://sea-fishing.org/index.php'] #just a place holder
    base_url = 'https://sea-fishing.org/'


    def parse(self, response):
        '''generate links to pages in a board        '''
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        BOARDS = ['South Coast', 'East Coast', 'West Coast', 'North East Coast', 'North West Coast', 'South East Coast', 'South West Coast', 'Isle of Wight', 'Thames Estuary', 'Humber Estuary']
        URLS = ['https://sea-fishing.org/viewforum.php?f=3', 'https://sea-fishing.org/viewforum.php?f=5', 'https://sea-fishing.org/viewforum.php?f=4', 'https://sea-fishing.org/viewforum.php?f=29', 'https://sea-fishing.org/viewforum.php?f=74', 'https://sea-fishing.org/viewforum.php?f=73', 'https://sea-fishing.org/viewforum.php?f=70', 'https://sea-fishing.org/viewforum.php?f=68', 'https://sea-fishing.org/viewforum.php?f=75', 'https://sea-fishing.org/viewforum.php?f=81']
        PAGES = [122, 83, 7, 49, 22, 54, 23, 3, 32, 8]
        assert len(BOARDS) == len(URLS) == len(PAGES), 'Setup list lengths DO NOT match'
        posts_per_page = 50

        for i, root_url in enumerate(URLS):
            curboard = BOARDS[i]
            urls = [root_url] #first page is just the base post url
            for x in range(posts_per_page, PAGES[i] * posts_per_page, posts_per_page):
                urls.append('%s&start=%s' % (urls[0], x))

            for url in urls:
                yield scrapy.Request(url, callback=self.crawl_board_threads, dont_filter=False, meta={'curboard':curboard})


    def crawl_board_threads(self, response):
        '''crawl'''
        curboard = response.meta.get('curboard')
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        links = LinkExtractor(restrict_xpaths='//a[@class = "topictitle"]').extract_links(response)
        for link in links:
            title = link.text
            s = response.urljoin(link.url)

            if settings.ITEM_PIPELINES.get('imgscrape.pipelines.UGCWriter'): #if we arnt using sql server, we dont lookup
                if not check_for_dup(s):
                    yield scrapy.Request(s, callback=self.parse_thread, dont_filter=False, meta={'curboard':curboard})
            else:
                yield scrapy.Request(s, callback=self.parse_thread, dont_filter=False, meta={'curboard':curboard})


    def parse_thread(self, response):
        '''open a report thread and parse first post only'''
        curboard = response.meta.get('curboard')
        title = response.meta.get('title')
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        l = _items.SeaFishingOrgLdr(item=_items.ForumUGC(), response=response)
        l.add_value('board', curboard)
        l.add_value('content_identifier', '')
        l.add_value('source', SeaFishingOrgReportsSpider.source)
        l.add_value('url', response.url)
        l.add_value('title', title)

        l.add_xpath('published_date', '(//span[@class = "responsive-hide"])[1]/following-sibling::text()')

        txt = response.selector.xpath('(//div[@class="postbody"]/div/div[@class="content"])[1]/text()').extract()
        l.add_value('txt', txt)

        author = response.selector.xpath('(//span[@class="responsive-hide"]/strong/a[@class="username"])[1]/text()').extract()
        l.add_value('who', author)

        I = l.load_item()
        return I



class SeaFishingOrgReportsAfloatSpider(Spider):
    '''scrape reports from angling addicts forum
    '''
    name = "seafishingorg-afloat"
    source = 'www.sea-fishing.org'
    allowed_domains = ['sea-fishing.org']
    start_urls = ['https://sea-fishing.org/index.php'] #just a place holder
    base_url = 'https://sea-fishing.org/'


    def parse(self, response):
        '''generate links to pages in a board        '''
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        BOARDS = ['Boat Owners Forum', 'Kayak']
        URLS = ['https://www.sea-fishing.org/viewforum.php?f=76', 'https://www.sea-fishing.org/viewforum.php?f=71']
        PAGES = [13, 3]
        assert len(BOARDS) == len(URLS) == len(PAGES), 'Setup list lengths DO NOT match'
        posts_per_page = 50

        for i, root_url in enumerate(URLS):
            curboard = BOARDS[i]
            urls = [root_url] #first page is just the base post url
            for x in range(posts_per_page, PAGES[i] * posts_per_page, posts_per_page):
                urls.append('%s&start=%s' % (urls[0], x))

            for url in urls:
                yield scrapy.Request(url, callback=self.crawl_board_threads, dont_filter=False, meta={'curboard':curboard})


    def crawl_board_threads(self, response):
        '''crawl'''
        curboard = response.meta.get('curboard')
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        links = LinkExtractor(restrict_xpaths='//a[@class = "topictitle"]').extract_links(response)
        for link in links:
            title = link.text
            s = response.urljoin(link.url)

            if settings.ITEM_PIPELINES.get('imgscrape.pipelines.UGCWriter'): #if we arnt using sql server, we dont lookup
                if not check_for_dup(s):
                    yield scrapy.Request(s, callback=self.parse_thread, dont_filter=False, meta={'curboard':curboard})
            else:
                yield scrapy.Request(s, callback=self.parse_thread, dont_filter=False, meta={'curboard':curboard})


    def parse_thread(self, response):
        '''open a report thread and parse first post only'''
        curboard = response.meta.get('curboard')
        title = response.meta.get('title')
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        l = _items.SeaFishingOrgLdr(item=_items.ForumUGC(), response=response)
        l.add_value('board', curboard)
        l.add_value('content_identifier', '')
        l.add_value('source', SeaFishingOrgReportsSpider.source)
        l.add_value('url', response.url)
        l.add_value('title', title)

        l.add_xpath('published_date', '(//span[@class = "responsive-hide"])[1]/following-sibling::text()')

        txt = response.selector.xpath('(//div[@class="postbody"]/div/div[@class="content"])[1]/text()').extract()
        l.add_value('txt', txt)

        author = response.selector.xpath('(//span[@class="responsive-hide"]/strong/a[@class="username"])[1]/text()').extract()
        l.add_value('who', author)

        I = l.load_item()
        return I
