# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable,anomalous-backslash-in-string,no-self-use
'''spiders'''
import scrapy

from scrapy.spiders import Spider
from scrapy.linkextractors import LinkExtractor
import imgscrape.items as _items
from imgscrape.pipelines import check_for_dup
import imgscrape.ini as _ini
import imgscrape.settings as settings

LAST_PAGE = 24

class TotalFishingReportsSpider(Spider):
    '''scrape reports from angling addicts forum
    '''
    name = "total-fishing"
    source = 'www.total-fishing.com/forums'
    allowed_domains = ['www.total-fishing.com']
    start_urls = _ini.TotalFishingReportsIni.START_URLS
    base_url = _ini.TotalFishingReportsIni.BASE_URL


    def parse(self, response):
        '''generate links to pages in a board
        yields:
        https://www.total-fishing.com/forums/forum/fishing/sea-fishing/page/24/
        '''
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        curboard = ['Sea Fishing']

        urls = [response.url] #first page is just the base post url
        for x in range(2, LAST_PAGE +  1):
            urls.append('%spage/%s' % (urls[0], x))

        #get last page nr
        for url in urls:
            yield scrapy.Request(url, callback=self.crawl_board_threads, dont_filter=False, meta={'curboard':curboard})


    def crawl_board_threads(self, response):
        '''crawl'''
        curboard = response.meta.get('curboard')
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        links = LinkExtractor(restrict_xpaths='//a[contains(@class, "bbp-topic-permalink")]').extract_links(response)
        for link in links:
            s = response.urljoin(link.url)
            if 'new-forum' in s: #cludge
                pass
            else:
                if settings.ITEM_PIPELINES.get('imgscrape.pipelines.UGCWriter'): #if we arnt using sql server, we dont lookup
                    if not check_for_dup(s):
                        yield scrapy.Request(s, callback=self.parse_thread, dont_filter=False, meta={'curboard':curboard})
                else:
                    yield scrapy.Request(s, callback=self.parse_thread, dont_filter=False, meta={'curboard':curboard})


    def parse_thread(self, response):
        '''open a report thread and parse first post only
        Input response:https://www.total-fishing.com/forums/topic/new-zealand-bushcraft-hunting-and-fishing-videos/ ...
        '''
        #see sunny rhyl for an example where we also loop over multipage threads, here we only bother with the first post
        curboard = response.meta.get('curboard')
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        #use our own item loaders, which inherits from the base.
        #worldseafishingMMOLdr specifies input and output handlers
        l = _items.TotalFishingLdr(item=_items.ForumUGC(), response=response)
        l.add_value('board', curboard)
        l.add_value('content_identifier', '')
        l.add_value('source', TotalFishingReportsSpider.source)
        l.add_value('url', response.url)

        l.add_xpath('title', '//h1[@class="entry-title"]/text()')
        l.add_xpath('published_date', '(//span[@class = "bbp-reply-post-date"])[1]/text()') #note the brackets around the expression, this gets the first instance https://stackoverflow.com/questions/14294997/what-is-the-xpath-expression-to-find-only-the-first-occurrence

        txt = response.selector.xpath('(//div[contains(@class, "status-publish")]/div[@class = "bbp-reply-content"])[1]').extract()
        l.add_value('txt', txt)

        author = response.selector.xpath('(//a[@class = "bbp-author-name"])[1]/text()').extract()
        l.add_value('who', author)

        I = l.load_item()
        return I
