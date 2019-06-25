# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable,anomalous-backslash-in-string,no-self-use
#This contains an example of
#looping ove a selector to extract all thread posts
'''spiders'''
import funclib.stringslib as stringslib
import scrapy
from scrapy.spiders import Spider
from scrapy.linkextractors import LinkExtractor
import imgscrape.items as _items


class SolentFishingForumsSpider(Spider):
    '''scrape reports from angling addicts forum
    '''
    name = "solentfishingforums"
    source = 'www.solent-fishing-forums.co.uk'
    allowed_domains = ['solent-fishing-forums.co.uk']
    start_urls = ['http://www.solent-fishing-forums.co.uk'] #just a place holder to kick stuff off
    base_url = 'http://www.solent-fishing-forums.co.uk'

    #custom_settings = {'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter'}

    def parse(self, response):
        '''generate links to pages in a board        '''
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        ROOT = 'http://www.solent-fishing-forums.co.uk/beach-talk_forum1_page'
        PAGES = 27
       # assert len(BOARDS) == len(URLS) == len(PAGES), 'Setup list lengths DO NOT match'

        urls = ['http://www.solent-fishing-forums.co.uk/beach-talk_forum1_page.html']
        curboard = 'Beach Talk'
        for x in range(2, PAGES + 1):
            urls.append('%s%s.html' % (ROOT, x))  #/page-400

        for url in urls:
            yield scrapy.Request(url, callback=self.crawl_board_threads, meta={'curboard':curboard})


    def crawl_board_threads(self, response):
        '''crawl'''
        curboard = response.meta.get('curboard')
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        links_even = LinkExtractor(restrict_xpaths='//body/table[5]//tr[@class="evenTableRow"]/td[2]//a[not(@class = "smLink")]', unique=True).extract_links(response)
        links_odd = LinkExtractor(restrict_xpaths='//body/table[5]//tr[@class="oddTableRow"]/td[2]//a[not(@class = "smLink")]', unique=True).extract_links(response)

        for link in links_even:
            title = link.text
            s = response.urljoin(link.url)
            #don't check for dups this time, we are scraping multiple posts per thread
            yield scrapy.Request(s, callback=self.parse_thread, dont_filter=True, meta={'curboard':curboard, 'title':title})

        for link in links_odd:
            title = link.text
            s = response.urljoin(link.url)
            #don't check for dups this time, we are scraping multiple posts per thread
            yield scrapy.Request(s, callback=self.parse_thread, dont_filter=True, meta={'curboard':curboard, 'title':title})


    def parse_thread(self, response):
        '''open a report thread and parse all thread posts on first page'''
        curboard = response.meta.get('curboard')
        title = response.meta.get('title')
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        pub_date = response.selector.xpath('./body/table[5]//td[@class="msgOddTableTop"]/a/following-sibling::text()').extract()[1] #07 February 2008 6:12pm
        assert isinstance(pub_date, str)
        pub_date = pub_date.replace('\xa0', ' ')
        pub_date = stringslib.filter_alphanumeric1(pub_date, strict=False, remove_double_quote=True, remove_single_quote=True, allow_cr=False, allow_lf=False, include=(':', ' ')).lstrip().rstrip()
        pub_date = pub_date.replace('Posted:', '').lstrip().rstrip()
        pub_date = pub_date.replace(' at ', ' ')


        posts_odd = response.selector.xpath('./body/table[5]//tr[@class="msgOddTableRow"]')
        posts_even = response.selector.xpath('./body/table[5]//tr[@class="msgEvenTableRow"]')

        for i, post in enumerate(posts_odd):
            l = _items.SolentFishingForumsLdr(item=_items.ForumUGC(), response=response)
            l.add_value('board', curboard)
            l.add_value('content_identifier', str(i))
            l.add_value('source', SolentFishingForumsSpider.source)
            l.add_value('url', response.url)
            l.add_value('title', title)

            l.add_value('published_date', pub_date)

            txt = post.xpath('.//td[@class="msgLineDevider"]').extract()
            txt = ['\n'.join(txt)]
            l.add_value('txt', txt)

            l.add_value('who', 'Unknown')

            I = l.load_item()
            yield I


        for i, post in enumerate(posts_even):
            l = _items.SolentFishingForumsLdr(item=_items.ForumUGC(), response=response)
            l.add_value('board', curboard)
            l.add_value('content_identifier', str(i))
            l.add_value('source', SolentFishingForumsSpider.source)
            l.add_value('url', response.url)
            l.add_value('title', title)

            l.add_value('published_date', pub_date)

            txt = post.xpath('.//td[@class="msgLineDevider"]').extract()
            txt = ['\n'.join(txt)]
            l.add_value('txt', txt)

            l.add_value('who', 'Unknown')

            I = l.load_item()
            yield I




class SolentFishingForumsBoatSpider(Spider):
    '''scrape reports from angling addicts forum
    '''
    name = "solentfishingforums-boat"
    source = 'www.solent-fishing-forums.co.uk'
    allowed_domains = ['solent-fishing-forums.co.uk']
    start_urls = ['http://www.solent-fishing-forums.co.uk'] #just a place holder to kick stuff off
    base_url = 'http://www.solent-fishing-forums.co.uk'

    #custom_settings = {'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter'}

    def parse(self, response):
        '''generate links to pages in a board        '''
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        ROOT = 'http://www.solent-fishing-forums.co.uk/boat-talk_forum2_page'
        PAGES = 136
       # assert len(BOARDS) == len(URLS) == len(PAGES), 'Setup list lengths DO NOT match'

        urls = ['http://www.solent-fishing-forums.co.uk/boat-talk_forum2_page1.html']
        curboard = 'Boat Talk'
        for x in range(2, PAGES + 1):
            urls.append('%s%s.html' % (ROOT, x))  #/page-400

        for url in urls:
            yield scrapy.Request(url, callback=self.crawl_board_threads, meta={'curboard':curboard})


    def crawl_board_threads(self, response):
        '''crawl'''
        curboard = response.meta.get('curboard')
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        links_even = LinkExtractor(restrict_xpaths='//body/table[5]//tr[@class="evenTableRow"]/td[2]//a[not(@class = "smLink")]', unique=True).extract_links(response)
        links_odd = LinkExtractor(restrict_xpaths='//body/table[5]//tr[@class="oddTableRow"]/td[2]//a[not(@class = "smLink")]', unique=True).extract_links(response)

        for link in links_even:
            title = link.text
            s = response.urljoin(link.url)
            #don't check for dups this time, we are scraping multiple posts per thread
            yield scrapy.Request(s, callback=self.parse_thread, dont_filter=True, meta={'curboard':curboard, 'title':title})

        for link in links_odd:
            title = link.text
            s = response.urljoin(link.url)
            #don't check for dups this time, we are scraping multiple posts per thread
            yield scrapy.Request(s, callback=self.parse_thread, dont_filter=True, meta={'curboard':curboard, 'title':title})


    def parse_thread(self, response):
        '''open a report thread and parse all thread posts on first page'''
        curboard = response.meta.get('curboard')
        title = response.meta.get('title')
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        pub_date = response.selector.xpath('./body/table[5]//td[@class="msgOddTableTop"]/a/following-sibling::text()').extract()[1] #07 February 2008 6:12pm
        assert isinstance(pub_date, str)
        pub_date = pub_date.replace('\xa0', ' ')
        pub_date = stringslib.filter_alphanumeric1(pub_date, strict=False, remove_double_quote=True, remove_single_quote=True, allow_cr=False, allow_lf=False, include=(':', ' ')).lstrip().rstrip()
        pub_date = pub_date.replace('Posted:', '').lstrip().rstrip()
        pub_date = pub_date.replace(' at ', ' ')


        posts_odd = response.selector.xpath('./body/table[5]//tr[@class="msgOddTableRow"]')
        posts_even = response.selector.xpath('./body/table[5]//tr[@class="msgEvenTableRow"]')

        for i, post in enumerate(posts_odd):
            l = _items.SolentFishingForumsLdr(item=_items.ForumUGC(), response=response)
            l.add_value('board', curboard)
            l.add_value('content_identifier', str(i))
            l.add_value('source', SolentFishingForumsSpider.source)
            l.add_value('url', response.url)
            l.add_value('title', title)

            l.add_value('published_date', pub_date)

            txt = post.xpath('.//td[@class="msgLineDevider"]').extract()
            txt = ['\n'.join(txt)]
            l.add_value('txt', txt)

            l.add_value('who', 'Unknown')

            I = l.load_item()
            yield I


        for i, post in enumerate(posts_even):
            l = _items.SolentFishingForumsLdr(item=_items.ForumUGC(), response=response)
            l.add_value('board', curboard)
            l.add_value('content_identifier', str(i))
            l.add_value('source', SolentFishingForumsSpider.source)
            l.add_value('url', response.url)
            l.add_value('title', title)

            l.add_value('published_date', pub_date)

            txt = post.xpath('.//td[@class="msgLineDevider"]').extract()
            txt = ['\n'.join(txt)]
            l.add_value('txt', txt)

            l.add_value('who', 'Unknown')

            I = l.load_item()
            yield I