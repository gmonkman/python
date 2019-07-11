# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable,anomalous-backslash-in-string,no-self-use
'''angling addicts spiders'''
import scrapy
from scrapy.spiders import Spider
from scrapy.linkextractors import LinkExtractor
import imgscrape.items as _items
from imgscrape.pipelines import check_for_dup
import imgscrape.ini as _ini



class AnglingAddictsReportsSpider(Spider):
    '''scrape reports from angling addicts forum
    '''
    name = "anglingaddicts"
    source = 'anglingaddicts.co.uk'
    allowed_domains = ['anglingaddicts.co.uk']
    start_urls = _ini.AnglingAddictsReportsIni.START_URLS
    base_url = _ini.AnglingAddictsReportsIni.BASE_URL
    custom_settings = {'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter', 'ITEM_PIPELINES': {'imgscrape.pipelines.UGCWriter': 10}}

    def parse(self, response):
        '''generate links to pages in a board
        yields:
        'http://www.anglingaddicts.co.uk/forum/north-west-fishing-reports.html',
        'http://www.anglingaddicts.co.uk/forum/north-east-sea-fishing-reports.html, ...'''

        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        urls = [response.url] #first page is just the base post url

        #get the base url so we can generate the
        #rest of the links based on the total nr.
        #of pages
        #eg. first page is http://www.anglingaddicts.co.uk/forum/north-west-fishing-reports.html
        #but there are an unknown nr. of pages on this board
        #we look on the page for the last page nr, in pagination
        #from which we can then generate all necessary page links
        parts = str(response.url.split('/')[-1])
        parts = parts.split('.', 1)
        curboard = parts[0]
        #AnglingAddictsReportsSpider.BOARD = parts[0]
        posts_per_page = 25

        #get last page nr
        pagination = response.selector.xpath('//div[contains(@class,"pagination")]//span[contains(@class, "page-dots")]/following::a/text()').extract()
        if pagination:
            pagination = pagination[0]
            last_page = int(pagination)
        else:
            pagination = response.selector.xpath('(//div[contains(@class,"pagination")]//span//a/text())[last()]').extract()
            if pagination:
                pagination = pagination[0]
                last_page = int(pagination)
            else:
                last_page = 0

        if last_page > 1:
            for v in list(range((int(last_page) - 1) * posts_per_page, 0, -1*posts_per_page)):
                s = '%s%s-%s.%s' % (self.base_url, parts[0], str(v), parts[1]) #e.g. http://www.anglingaddicts.co.uk/forum/north-west-fishing-reports-25.html
                urls.append(s)

        for url in urls:
            yield scrapy.Request(url, callback=self.crawl_board_threads, dont_filter=True, meta={'curboard':curboard})


    def crawl_board_threads(self, response):
        '''response in http://www.anglingaddicts.co.uk/forum/north-west-fishing-reports.html http://www.anglingaddicts.co.uk/forum/north-west-fishing-reports-25.html
        yields individual thread links: e.g. http://www.anglingaddicts.co.uk/forum/heysham-today-t22893.html'''

        curboard = response.meta.get('curboard')
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        links = LinkExtractor(restrict_xpaths='//div[@class="forumbg"]//a[@class="topictitle"]').extract_links(response)
        for link in links:
            #s = response.urljoin(link.url)
            title = link.text
            if not check_for_dup(link.url):
                yield scrapy.Request(link.url, callback=self.parse_thread, dont_filter=True, meta={'curboard':curboard, 'title':title})

    def parse_thread(self, response):
        '''open a report thread and parse first post only
        Input response:http://sunnyrhyl.forumotion.com/t8311-rhods-species-hunt-2017
        '''
        #see sunny rhyl for an example where we also loop over multipage threads, here we only bother with the first post
        curboard = response.meta.get('curboard')
        title = response.meta.get('title')
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        #use our own item loaders, which inherits from the base.
        #AnglingAddictsMMOLdr specifies input and output handlers
        l = _items.AnglingAddictsMMOLdr(item=_items.ForumUGC(), response=response)
        l.add_value('board', curboard)
        l.add_value('content_identifier', '')
        l.add_xpath('published_date', '(//p[contains(@class,"author")]/strong/following-sibling::text())[1]') #note the brackets around the expression, this gets the first instance https://stackoverflow.com/questions/14294997/what-is-the-xpath-expression-to-find-only-the-first-occurrence
        l.add_value('source', AnglingAddictsReportsSpider.source)
        l._add_value('title', title)
        #test
        txt = response.selector.xpath('(//div[contains(@class,"content")])[1]').extract()
        l.add_xpath('txt', '(//div[contains(@class,"content")])[1]') #all html below node - beautful soup is used to strip html
        l.add_value('url', response.url)
        l.add_xpath('who', '(//p[contains(@class,"author")]/strong/a/text())[1]')
        return l.load_item()



class AnglingAddictsBoatYakReportsSpider(Spider):
    '''scrape reports from angling addicts forum
    '''
    name = "anglingaddicts-boatyak"
    source = 'anglingaddicts.co.uk'
    allowed_domains = ['anglingaddicts.co.uk']
    start_urls = ['http://www.anglingaddicts.co.uk/forum/kayak-fishing-reports.html', 'http://www.anglingaddicts.co.uk/forum/boat-fishing-reports.html']
    base_url = _ini.AnglingAddictsReportsIni.BASE_URL
    custom_settings = {'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter', 'ITEM_PIPELINES': {'imgscrape.pipelines.UGCWriter': 10}}

    def parse(self, response):
        '''generate links to pages in a board
        yields:
        'http://www.anglingaddicts.co.uk/forum/north-west-fishing-reports.html',
        'http://www.anglingaddicts.co.uk/forum/north-east-sea-fishing-reports.html, ...'''

        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        urls = [response.url] #first page is just the base post url

        #get the base url so we can generate the
        #rest of the links based on the total nr.
        #of pages
        #eg. first page is http://www.anglingaddicts.co.uk/forum/north-west-fishing-reports.html
        #but there are an unknown nr. of pages on this board
        #we look on the page for the last page nr, in pagination
        #from which we can then generate all necessary page links
        parts = str(response.url.split('/')[-1])
        parts = parts.split('.', 1)
        curboard = parts[0]
        #AnglingAddictsReportsSpider.BOARD = parts[0]
        posts_per_page = 25

        #get last page nr
        pagination = response.selector.xpath('//div[contains(@class,"pagination")]//span[contains(@class, "page-dots")]/following::a/text()').extract()
        if pagination:
            pagination = pagination[0]
            last_page = int(pagination)
        else:
            pagination = response.selector.xpath('(//div[contains(@class,"pagination")]//span//a/text())[last()]').extract()
            if pagination:
                pagination = pagination[0]
                last_page = int(pagination)
            else:
                last_page = 0

        if last_page > 1:
            for v in list(range((int(last_page) - 1) * posts_per_page, 0, -1*posts_per_page)):
                s = '%s%s-%s.%s' % (self.base_url, parts[0], str(v), parts[1]) #e.g. http://www.anglingaddicts.co.uk/forum/north-west-fishing-reports-25.html
                urls.append(s)

        for url in urls:
            yield scrapy.Request(url, callback=self.crawl_board_threads, dont_filter=True, meta={'curboard':curboard})


    def crawl_board_threads(self, response):
        '''response in http://www.anglingaddicts.co.uk/forum/north-west-fishing-reports.html http://www.anglingaddicts.co.uk/forum/north-west-fishing-reports-25.html
        yields individual thread links: e.g. http://www.anglingaddicts.co.uk/forum/heysham-today-t22893.html'''

        curboard = response.meta.get('curboard')
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        links = LinkExtractor(restrict_xpaths='//div[@class="forumbg"]//a[@class="topictitle"]').extract_links(response)
        for link in links:
            #s = response.urljoin(link.url)
            title = link.text
            if not check_for_dup(link.url):
                yield scrapy.Request(link.url, callback=self.parse_thread, dont_filter=True, meta={'curboard':curboard, 'title':title})

    def parse_thread(self, response):
        '''open a report thread and parse first post only
        Input response:http://sunnyrhyl.forumotion.com/t8311-rhods-species-hunt-2017
        '''
        #see sunny rhyl for an example where we also loop over multipage threads, here we only bother with the first post
        curboard = response.meta.get('curboard')
        title = response.meta.get('title')
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        #use our own item loaders, which inherits from the base.
        #AnglingAddictsMMOLdr specifies input and output handlers
        l = _items.AnglingAddictsMMOLdr(item=_items.ForumUGC(), response=response)
        l.add_value('board', curboard)
        l.add_value('content_identifier', '')
        l.add_xpath('published_date', '(//p[contains(@class,"author")]/strong/following-sibling::text())[1]') #note the brackets around the expression, this gets the first instance https://stackoverflow.com/questions/14294997/what-is-the-xpath-expression-to-find-only-the-first-occurrence
        l.add_value('source', AnglingAddictsReportsSpider.source)
        l._add_value('title', title)
        #test
        txt = response.selector.xpath('(//div[contains(@class,"content")])[1]').extract()
        l.add_xpath('txt', '(//div[contains(@class,"content")])[1]') #all html below node - beautful soup is used to strip html
        l.add_value('url', response.url)
        l.add_xpath('who', '(//p[contains(@class,"author")]/strong/a/text())[1]')
        return l.load_item()
