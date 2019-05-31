# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable,anomalous-backslash-in-string,no-self-use
'''spiders'''
import scrapy

from scrapy.spiders import Spider
from scrapy.linkextractors import LinkExtractor
import imgscrape.items as _items
from imgscrape.pipelines import check_for_dup
from imgscrape import settings



class NESASpider(Spider):
    '''scrape reports from angling addicts forum
    '''
    name = "nesa"
    source = 'www.nesa.co.uk'
    allowed_domains = ['nesa.co.uk']
    start_urls = ['http://www.nesa.co.uk/forums/shore-catch-reports/'] #just a place holder
    base_url = 'http://www.nesa.co.uk/'


    def parse(self, response):
        '''generate links to pages in a board        '''
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        BOARDS = ['Shore Catch Reports']
        URLS = ['http://www.nesa.co.uk/forums/shore-fishing/']
        PAGES = [501]

        assert len(BOARDS) == len(URLS) == len(PAGES), 'Setup list lengths DO NOT match'
        #posts_per_page = 1

        for i, root_url in enumerate(URLS):
            curboard = BOARDS[i]
            urls = [root_url] #first page is just the base post url
            for x in range(2, PAGES[i] + 1):
                urls.append('%s/index%s.html' % (urls[0], x))

            for url in urls:
                yield scrapy.Request(url, callback=self.crawl_board_threads, dont_filter=False, meta={'curboard':curboard})


    def crawl_board_threads(self, response):
        '''crawl'''
        #stickies
        IGNORE_URLS = ['http://www.nesa.co.uk/forums/shore-fishing/15110-disabled-fishing-spots.html', 'http://www.nesa.co.uk/forums/shore-fishing/135534-how-sharpen-your-filleting-knife.html', 'http://www.nesa.co.uk/forums/shore-fishing/17732-double-sided-flounders-mods-any-chance-making-sticky.html', 'http://www.nesa.co.uk/forums/shore-fishing/236272-10-off-dickies-royal-quays-please-make-sticky.html', 'http://www.nesa.co.uk/forums/shore-fishing/238889-derek-russells-sons-just-giving-page.html', 'http://www.nesa.co.uk/forums/shore-fishing/236579-i-really-need-your-support.html']
        curboard = response.meta.get('curboard')
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        links = LinkExtractor(restrict_xpaths='//a[contains(@id, "thread_title_")]').extract_links(response)

        for link in links:
            title = link.text
            s = response.urljoin(link.url)
            if s in IGNORE_URLS:
                pass
            else:
                if settings.ITEM_PIPELINES.get('imgscrape.pipelines.UGCWriter'): #if we arnt using sql server, we dont lookup
                    if not check_for_dup(s):
                        yield scrapy.Request(s, callback=self.parse_thread, dont_filter=False, meta={'curboard':curboard, 'title':title})
                else:
                    yield scrapy.Request(s, callback=self.parse_thread, dont_filter=False, meta={'curboard':curboard, 'title':title})


    def parse_thread(self, response):
        '''open a report thread and parse first post only'''
        curboard = response.meta.get('curboard')
        title = response.meta.get('title')
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        l = _items.NESALdr(item=_items.ForumUGC(), response=response)
        l.add_value('board', curboard)
        l.add_value('content_identifier', '')
        l.add_value('source', NESASpider.source)
        l.add_value('url', response.url)
        l.add_value('title', title)


        date_ = response.selector.xpath('//div[@id="posts"]/div[1]/div/div/div/table[1]//a[contains(@name, "post")]/following-sibling::text()[1]').extract()
        l.add_value('published_date', date_) #06-12-2018, 01:05 AM

        txt = response.selector.xpath('//div[@id="posts"]/div[1]/div/div//div[contains(@id, "post_message_")]/text()').extract()
        txt = ['\n'.join(txt)]
        l.add_value('txt', txt)

        author = response.selector.xpath('//div[@id="posts"]/div[1]/div/div//a[@class="bigusername"]/text()').extract()[0]
        l.add_value('who', author)

        I = l.load_item()
        return I
