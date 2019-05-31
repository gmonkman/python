# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable,anomalous-backslash-in-string,no-self-use
#This contains an example of
#looping ove a selector to extract all thread posts
'''spiders'''
import scrapy

from scrapy.spiders import Spider
from scrapy.linkextractors import LinkExtractor
import imgscrape.items as _items




class SouthWestSeaFishingSpider(Spider):
    '''scrape reports from angling addicts forum
    '''
    name = "southwestseafishing"
    source = 'www.southwestseafishing.co.uk'
    allowed_domains = ['southwestseafishing.co.uk']
    start_urls = ['https://www.southwestseafishing.co.uk/forum/shore-fishing'] #just a place holder to kick stuff off
    base_url = 'https://www.southwestseafishing.co.uk'

    custom_settings = {'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter'}

    def parse(self, response):
        '''generate links to pages in a board        '''
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        BOARDS = ['Devon Fishing', 'Cornwall Fishing', 'Dorset Fishing', 'Somerset Fishing']
        URLS = ['https://www.southwestseafishing.co.uk/forum/shore-fishing/devon-fishing', 'https://www.southwestseafishing.co.uk/forum/shore-fishing/cornwall-fishing', 'https://www.southwestseafishing.co.uk/forum/shore-fishing/dorset-fishing', 'https://www.southwestseafishing.co.uk/forum/shore-fishing/somerset-fishing']

        PAGES = [122, 127, 7, 5]
        assert len(BOARDS) == len(URLS) == len(PAGES), 'Setup list lengths DO NOT match'

        for i, root_url in enumerate(URLS):
            curboard = BOARDS[i]
            urls = [root_url] #first page is just the base post url
            for x in range(2, PAGES[i] + 1):
                urls.append('%s/page%s' % (urls[0], x))

            for url in urls:
                yield scrapy.Request(url, callback=self.crawl_board_threads, dont_filter=True, meta={'curboard':curboard})


    def crawl_board_threads(self, response):
        '''crawl'''
        curboard = response.meta.get('curboard')
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        links = LinkExtractor(restrict_xpaths='//a[@class = "topic-title js-topic-title"]').extract_links(response)

        for link in links:
            title = link.text
            s = response.urljoin(link.url)
            #don't check for dups this time, we are scraping multiple posts per thread
            yield scrapy.Request(s, callback=self.parse_thread, dont_filter=True, meta={'curboard':curboard, 'title':title})


    def parse_thread(self, response):
        '''open a report thread and parse first post only'''
        curboard = response.meta.get('curboard')
        title = response.meta.get('title')
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        posts = response.selector.xpath('//li[contains(@class, "b-post js-post")]')
        for i, post in enumerate(posts):

            l = _items.SouthWestSeaFishingLdr(item=_items.ForumUGC(), response=response)
            l.add_value('board', curboard)
            l.add_value('content_identifier', str(i))
            l.add_value('source', SouthWestSeaFishingSpider.source)
            l.add_value('url', response.url)
            l.add_value('title', title)

            pub_date = post.xpath('.//time/@datetime').extract() #'2016-04-12T14:40:52'
            pub_date = [pub_date[0].replace('-', '').replace('T', ' ')]
            l.add_value('published_date', pub_date)

            txt = post.xpath('.//div[contains(@class, "js-post__content-text")]/text()').extract()
            txt = ['\n'.join(txt)]
            l.add_value('txt', txt)

            author = post.xpath('.//div[contains(@class, "author")]/strong/a/text()').extract()
            l.add_value('who', author)

            I = l.load_item()
            yield I
