# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable,anomalous-backslash-in-string,no-self-use
'''angling addicts spiders'''
import scrapy

from scrapy.spiders import Spider
from scrapy.linkextractors import LinkExtractor
import imgscrape.items as _items
from imgscrape.pipelines import check_for_dup
import imgscrape.ini as _ini



class WirralSeaFishingReportsSpider(Spider):
    '''scrape reports from angling addicts forum
    '''
    name = "wirralseafishing-reports-forum"
    source = 'wirralseafishing.co.uk/forum'
    allowed_domains = ['wirralseafishing.co.uk']
    start_urls = _ini.WirralSeaFishingReportsIni.START_URLS
    base_url = _ini.WirralSeaFishingReportsIni.BASE_URL

    #bug fix - run if set in ini, override ini url list
    if _ini.WirralSeaFishingReportsIni.RUN_FIX:
        print('\n*RUNNING FIX CODE*\n')
        start_urls = ['https://www.wirralseafishing.co.uk/forum/phpBB2/viewforum.php?f=57']


    def parse(self, response):
        '''generate links to pages in a board
        yields:
        https://www.wirralseafishing.co.uk/forum/phpBB2/viewforum.php?f=33
        https://www.wirralseafishing.co.uk/forum/phpBB2/viewforum.php?f=33&start=30
        https://www.wirralseafishing.co.uk/forum/phpBB2/viewforum.php?f=33&start=3420

        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        '''
        curboard = response.selector.xpath('//h2[contains(@class, "forum-title")]/a/text()').extract()
        if curboard[0].lower() == 'Fishing Session Reports'.lower():
            last_link = 5430
        else:
            last_link = 3420 #this isnt right as it will generate too many requests for the 2nd set of links - will need to scrape from #5430
        posts_per_page = 30
        urls = [response.url] #first page is just the base post url

        #ug fixed last link, will need to run a fix to import the left out Fishing Session Reports
        if _ini.WirralSeaFishingReportsIni.RUN_FIX:
            print('\n*RUNNING FIX CODE*\n')
            for x in range(3420 + posts_per_page, last_link + posts_per_page, posts_per_page):
                urls.append(urls[0] + "&start=%s" % x)
        else:
            for x in range(posts_per_page, last_link+posts_per_page, posts_per_page):
                urls.append(urls[0] + "&start=%s" % x)

        #get last page nr
        for url in urls:
            yield scrapy.Request(url, callback=self.crawl_board_threads, dont_filter=False, meta={'curboard':curboard})


    def crawl_board_threads(self, response):
        '''crawl'''
        curboard = response.meta.get('curboard')
        '''response in http://www.WirralSeaFishing.co.uk/forum/north-west-fishing-reports.html http://www.WirralSeaFishing.co.uk/forum/north-west-fishing-reports-25.html
        yields individual thread links: e.g. http://www.WirralSeaFishing.co.uk/forum/heysham-today-t22893.html'''
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        links = LinkExtractor(restrict_xpaths='//div[@class="forumbg"]//a[@class="topictitle"]').extract_links(response)
        for link in links:
            s = response.urljoin(link.url)
            if not check_for_dup(s):
                yield scrapy.Request(s, callback=self.parse_thread, dont_filter=False, meta={'curboard':curboard})


    def parse_thread(self, response):
        '''open a report thread and parse first post only
        Input response:https://www.wirralseafishing.co.uk/forum/phpBB2/viewtopic.php?f=33&t=32635
        '''
        #see sunny rhyl for an example where we also loop over multipage threads, here we only bother with the first post
        curboard = response.meta.get('curboard')
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        #use our own item loaders, which inherits from the base.
        #WirralSeaFishingMMOLdr specifies input and output handlers
        l = _items.WirralSeaFishingLdr(item=_items.ForumUGC(), response=response)
        l.add_value('board', curboard)
        l.add_value('content_identifier', '')
        l.add_xpath('title', '//h3[contains(@class, "first")]/a/text()')
        l.add_xpath('published_date', '(//span[contains(@class, "responsive-hide")]/following-sibling::text())[1]') #note the brackets around the expression, this gets the first instance https://stackoverflow.com/questions/14294997/what-is-the-xpath-expression-to-find-only-the-first-occurrence
        l.add_value('source', WirralSeaFishingReportsSpider.source)

        #test
        txt = response.selector.xpath('(//div[contains(@class,"content")])[1]').extract()
        l.add_xpath('txt', '(//div[contains(@class, "content")])[1]') #all html below node - beautful soup is used to strip html
        l.add_value('url', response.url)
        l.add_xpath('who', '(//a[contains(@class, "username")]/text())[2]')
        return l.load_item()


class WirralSeaFishingVenuesSpider(Spider):
    '''scrape reports from angling addicts forum
    '''
    name = "wirralseafishingvenues"
    source = 'wirralseafishing.co.uk/forum'
    allowed_domains = ['wirralseafishing.co.uk']
    start_urls = ['https://www.wirralseafishing.co.uk/forum/phpBB2/viewforum.php?f=88', 'https://www.wirralseafishing.co.uk/forum/phpBB2/viewforum.php?f=53', 'https://www.wirralseafishing.co.uk/forum/phpBB2/viewforum.php?f=68']
    base_url = 'https://www.wirralseafishing.co.uk/forum'


    def parse(self, response):
        '''generate links to pages in a board
        yields:
        https://www.wirralseafishing.co.uk/forum/phpBB2/viewforum.php?f=33
        https://www.wirralseafishing.co.uk/forum/phpBB2/viewforum.php?f=33&start=30
        https://www.wirralseafishing.co.uk/forum/phpBB2/viewforum.php?f=33&start=3420

        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        '''
        curboard = response.selector.xpath('//h2[contains(@class, "forum-title")]/a/text()').extract()
        if curboard[0].lower() == 'Merseyside/Fylde Coast/Cumbrian Venues/Directions'.lower():
            last_link = None
        elif curboard[0].lower() == 'Easy Access Venues/Directions For All Areas'.lower():
            last_link = 30 #this isnt right as it will generate too many requests for the 2nd set of links - will need to scrape from #5430
        elif curboard[0].lower() == 'Sea Fishing and Venue Questions'.lower():
            last_link = 990
        else:
            raise ValueError('Unexpected board in my parse function')

        posts_per_page = 30
        urls = [response.url] #first page is just the base post url

        if last_link:
            for x in range(posts_per_page, last_link+posts_per_page, posts_per_page):
                urls.append(urls[0] + "&start=%s" % x)

        #get last page nr
        for url in urls:
            yield scrapy.Request(url, callback=self.crawl_board_threads, dont_filter=False, meta={'curboard':curboard})


    def crawl_board_threads(self, response):
        '''crawl'''
        curboard = response.meta.get('curboard')
        '''response in http://www.WirralSeaFishing.co.uk/forum/north-west-fishing-reports.html http://www.WirralSeaFishing.co.uk/forum/north-west-fishing-reports-25.html
        yields individual thread links: e.g. http://www.WirralSeaFishing.co.uk/forum/heysham-today-t22893.html'''
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        links = LinkExtractor(restrict_xpaths='//div[@class="forumbg"]//a[@class="topictitle"]').extract_links(response)
        for link in links:
            s = response.urljoin(link.url)
            if not check_for_dup(s):
                yield scrapy.Request(s, callback=self.parse_thread, dont_filter=False, meta={'curboard':curboard})


    def parse_thread(self, response):
        '''open a report thread and parse first post only
        Input response:https://www.wirralseafishing.co.uk/forum/phpBB2/viewtopic.php?f=33&t=32635
        '''
        #see sunny rhyl for an example where we also loop over multipage threads, here we only bother with the first post
        curboard = response.meta.get('curboard')
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        #use our own item loaders, which inherits from the base.
        #WirralSeaFishingMMOLdr specifies input and output handlers
        l = _items.WirralSeaFishingLdr(item=_items.ForumUGC(), response=response)
        l.add_value('board', curboard)
        l.add_value('content_identifier', '')
        l.add_xpath('title', '//h3[contains(@class, "first")]/a/text()')
        l.add_xpath('published_date', '(//span[contains(@class, "responsive-hide")]/following-sibling::text())[1]') #note the brackets around the expression, this gets the first instance https://stackoverflow.com/questions/14294997/what-is-the-xpath-expression-to-find-only-the-first-occurrence
        l.add_value('source', WirralSeaFishingReportsSpider.source)

        #test
        txt = response.selector.xpath('(//div[contains(@class,"content")])[1]').extract()
        l.add_xpath('txt', '(//div[contains(@class, "content")])[1]') #all html below node - beautful soup is used to strip html
        l.add_value('url', response.url)
        l.add_xpath('who', '(//a[contains(@class, "username")]/text())[2]')
        return l.load_item()
