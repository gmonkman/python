# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable,anomalous-backslash-in-string,no-self-use
#This contains an example of
#looping ove a selector to extract all thread posts
'''spiders'''
import scrapy
from scrapy.spiders import Spider
from scrapy.linkextractors import LinkExtractor
import imgscrape.items as _items




class AnglersNetSpider(Spider):
    '''scrape reports from angling addicts forum
    '''
    name = "anglersnet"
    source = 'www.anglersnet.co.uk'
    allowed_domains = ['anglersnet.co.uk']
    start_urls = ['http://www.anglersnet.co.uk/forums/index.php?/forum/4-sea-fishing/'] #just a place holder to kick stuff off
    base_url = 'https://www.anglersnet.co.uk'

    custom_settings = {'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter'}

    def parse(self, response):
        '''generate links to pages in a board        '''
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        BOARDS = ['Sea Fishing']
        URLS = ['http://www.anglersnet.co.uk/forums/index.php?/forum/4-sea-fishing/']
        PAGES = [400]
        assert len(BOARDS) == len(URLS) == len(PAGES), 'Setup list lengths DO NOT match'

        for i, root_url in enumerate(URLS):
            curboard = BOARDS[i]
            urls = [root_url] #first page is just the base post url
            for x in range(2, PAGES[i] + 1):
                urls.append('%s/page-%s' % (urls[0], x))  #/page-400

            for url in urls:
                yield scrapy.Request(url, callback=self.crawl_board_threads, dont_filter=True, meta={'curboard':curboard})


    def crawl_board_threads(self, response):
        '''crawl'''
        curboard = response.meta.get('curboard')
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        links = LinkExtractor(restrict_xpaths='//div[@class="ipsBox_container"]//a[@class = "topic_title"]').extract_links(response)

        for link in links:
            title = link.text
            s = response.urljoin(link.url)
            #don't check for dups this time, we are scraping multiple posts per thread
            yield scrapy.Request(s, callback=self.parse_thread, dont_filter=True, meta={'curboard':curboard, 'title':title})


    def parse_thread(self, response):
        '''open a report thread and parse all thread posts on first page'''
        curboard = response.meta.get('curboard')
        title = response.meta.get('title')
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        posts = response.selector.xpath('//div[contains(@id, "post_id_")]')
        for i, post in enumerate(posts):

            l = _items.AnglersNetLdr(item=_items.ForumUGC(), response=response)
            l.add_value('board', curboard)
            l.add_value('content_identifier', str(i))
            l.add_value('source', AnglersNetSpider.source)
            l.add_value('url', response.url)
            l.add_value('title', title)

            pub_date = post.xpath('.//abbr[@class="published"]/@title').extract() #'2016-04-12T14:40:52'
            pub_date = [pub_date[0].replace('-', '').replace('T', ' ').replace('+', ' ')] #'20160412 14:40:52'
            pub_date = [pub_date[0][0:17].lstrip().rstrip()]
            l.add_value('published_date', pub_date)

            txt = post.xpath('.//div[contains(@class, "post entry-content")]/p').extract()
            txt = ['\n'.join(txt)]
            l.add_value('txt', txt)

            author = post.xpath('.//div[@class="user_details"]/span/text()').extract()
            l.add_value('who', author)

            I = l.load_item()
            yield I
