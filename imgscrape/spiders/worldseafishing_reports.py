# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable,anomalous-backslash-in-string,no-self-use
'''angling addicts spiders'''
import scrapy

from scrapy.spiders import Spider
from scrapy.linkextractors import LinkExtractor
import imgscrape.items as _items
from imgscrape.pipelines import check_for_dup
import imgscrape.ini as _ini

MAX_PAGE = {'south east catch reports':1966, 'south coast & ci catch reports':2212, 'south west catch reports':1212,
            'north west & the isle of man catch reports':766, 'north east catch reports':757,
            'whitby, holderness & the humber catch reports':22, 'east coast catch reports':1074
            }

class worldseafishingReportsSpider(Spider):
    '''scrape reports from angling addicts forum
    '''
    name = "worldseafishing-reports-forum"
    source = 'worldseafishing.com/forum'
    allowed_domains = ['worldseafishing.com']
    start_urls = _ini.WorldSeaFishingReportsIni.START_URLS
    base_url = _ini.WorldSeaFishingReportsIni.BASE_URL


    def parse(self, response):
        '''generate links to pages in a board
        yields:
        https://www.worldseafishing.com/forums/forums/south-east-catch-reports.39/, ...
        '''
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        curboard = response.selector.xpath('//div[contains(@class, "titleBar")]/h1/text()').extract()
        last_page = MAX_PAGE[curboard[0].lower()]

        #working, but quite a lot of variation on format here, still not caught all variations
        #so replaced with hard lookup based on the board name
        '''try:
            last_page = int(response.selector.xpath('//nav/a[@class="PageNavNext"]/following::a/text()').extract()[0])
        except Exception as _:
            last_page = int(response.selector.xpath('//nav/a[@class="gt999 "]/text()').extract()[0])

        if not last_page:
            raise ValueError('**Failed to get last_page with xpath')'''

        posts_per_page = 20
        urls = [response.url] #first page is just the base post url
        for x in range(2, last_page +  1):
            urls.append('%spage-%s' % (urls[0], x))

        #get last page nr
        for url in urls:
            yield scrapy.Request(url, callback=self.crawl_board_threads, dont_filter=False, meta={'curboard':curboard})


    def crawl_board_threads(self, response):
        '''crawl'''
        curboard = response.meta.get('curboard')
        '''response in https://www.worldseafishing.com/forums/forums/east-coast-catch-reports.28/ ....
        yields individual thread links: e.g. http://www.worldseafishing.co.uk/forum/heysham-today-t22893.html'''
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        links = LinkExtractor(restrict_xpaths='//li[contains(@id, "thread-") and not(contains(@class, "sticky"))]//h3[@class="title"]').extract_links(response)
        for link in links:
            s = response.urljoin(link.url)
            if not check_for_dup(s):
                yield scrapy.Request(s, callback=self.parse_thread, dont_filter=False, meta={'curboard':curboard})


    def parse_thread(self, response):
        '''open a report thread and parse first post only
        Input response:https://www.worldseafishing.com/forums/threads/norfolk-bass-alive-and-kicking.37655183/
        '''
        #see sunny rhyl for an example where we also loop over multipage threads, here we only bother with the first post
        curboard = response.meta.get('curboard')
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        #use our own item loaders, which inherits from the base.
        #worldseafishingMMOLdr specifies input and output handlers
        l = _items.WorldSeaFishingMMOLdr(item=_items.AnglingAddictsMMO(), response=response)
        l.add_value('board', curboard)
        l.add_value('content_identifier', '')
        l.add_xpath('title', '//div[contains(@class, "titleBar")]/h1/text()')
        l.add_xpath('published_date', '//p[@id = "pageDescription"]//span[@class="DateTime"]/@title') #note the brackets around the expression, this gets the first instance https://stackoverflow.com/questions/14294997/what-is-the-xpath-expression-to-find-only-the-first-occurrence
        l.add_value('source', worldseafishingReportsSpider.source)

        #test
        #txt = response.selector.xpath('(//div[contains(@class, "messageContent")]/article/blockquote)[1]').extract()
        l.add_xpath('txt', '(//div[contains(@class, "messageContent")]/article/blockquote)[1]') #all html below node - beautful soup is used to strip html
        l.add_value('url', response.url)
        l.add_xpath('who', '(//p[@id = "pageDescription"]/a[@class = "username"]/text())')
        return l.load_item()
