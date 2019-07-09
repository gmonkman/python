# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable,anomalous-backslash-in-string,no-self-use
#This contains an example of
#looping ove a selector to extract all thread posts
'''spiders'''
import scrapy
from scrapy.spiders import Spider

import imgscrape.items as _items




class CharterBoatUKSpider(Spider):
    '''scrape reports from charterboat UK reports
    '''
    name = "charterboatuk"
    source = 'www.charterboats-uk.co.uk'
    allowed_domains = ['www.charterboats-uk.co.uk']
    start_urls = ['https://www.charterboats-uk.co.uk/fishingreports/?locationid=688'] #just a place holder to kick stuff off
    base_url = 'https://www.charterboats-uk.co.uk'

    custom_settings = {'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter'}

    def parse(self, response):
        '''generate links to pages in a board        '''
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        BOARDS = ['latest fishing reports england']
        URLS = ['https://www.charterboats-uk.co.uk/fishingreports/?locationid=688']
        #page2 https://www.charterboats-uk.co.uk/fishingreports/?locationid=688&page=2
        PAGES = [741]
        assert len(BOARDS) == len(URLS) == len(PAGES), 'Setup list lengths DO NOT match'

        for i, root_url in enumerate(URLS):
            curboard = BOARDS[i]
            urls = [root_url] #first page is just the base post url
            for x in range(2, PAGES[i] + 1):
                urls.append('%s&page=%s' % (urls[0], x))  #&page=2

            for url in urls:
                yield scrapy.Request(url, callback=self.crawl_board_threads, dont_filter=True, meta={'curboard':curboard})


    def crawl_board_threads(self, response):
        '''crawl'''
        curboard = response.meta.get('curboard')
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        posts = response.selector.xpath('//ul[@id="report_list"]/li')
        for i, post in enumerate(posts):
            l = _items.CharterBoatUKLdr(item=_items.ForumUGC(), response=response)
            l.add_value('board', curboard)
            l.add_value('content_identifier', str(i))
            l.add_value('source', CharterBoatUKSpider.source)
            l.add_value('url', response.url)
            l.add_value('title', '')
            l.add_value('platform_hint', 'charter')

            pub_date, where = post.xpath('./a[@class="title"]/span/text()').extract() #'2016-04-12T14:40:52'
            assert pub_date.count('/') in (1, 2), 'Expected pub_date to contain 1 or 2 forward slashes. pub_date=%s' % pub_date
            if pub_date.count('/') == 1:
                pub_date = '01/' + pub_date #31/12/2019
            l.add_value('published_date', pub_date)

            charter_port = where.replace('(','').replace(')','').split(',')[0].lstrip().rstrip()
            l.add_value('charter_port', charter_port)

            txt = post.xpath('.//div[contains(@class, "col-md-18")]/p/text()').extract()
            txt = ['\n'.join(txt)]
            l.add_value('txt', txt)

            author = 'charterboatuk'
            l.add_value('who', author)

            boat = post.xpath('./a[@class="title"]/text()').extract()
            assert boat, 'boat was empty'
            boat = ' '.join(boat)
            boat = boat.split(' on ')[1].lstrip().rstrip()
            assert boat, 'boat was empty after split'
            l.add_value('boat', boat)
            l.add_value('source_platform', '["charter"]')
            I = l.load_item()
            yield I
