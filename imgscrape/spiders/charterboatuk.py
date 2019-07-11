# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable,anomalous-backslash-in-string,no-self-use
#This contains an example of
#looping ove a selector to extract all thread posts
'''spiders'''
import scrapy
from scrapy.spiders import Spider

import imgscrape.items as _items
from gazetteerdb.model import Gazetteer
import gazetteerdb
from funclib import stringslib



class CharterBoatUKReportsSpider(Spider):
    '''scrape reports from charterboat UK reports
    '''
    name = "charterboatukreports"
    source = 'www.charterboats-uk.co.uk'
    allowed_domains = ['www.charterboats-uk.co.uk']
    start_urls = ['https://www.charterboats-uk.co.uk/fishingreports/?locationid=688'] #just a place holder to kick stuff off
    base_url = 'https://www.charterboats-uk.co.uk'

    custom_settings = {'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter', 'ITEM_PIPELINES': {'imgscrape.pipelines.UGCWriter': 10}}

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
            l.add_value('source', CharterBoatUKReportsSpider.source)
            l.add_value('url', response.url)
            l.add_value('title', '')
            l.add_value('platform_hint', 'charter')

            pub_date, where = post.xpath('./a[@class="title"]/span/text()').extract() #'2016-04-12T14:40:52'
            assert pub_date.count('/') in (1, 2), 'Expected pub_date to contain 1 or 2 forward slashes. pub_date=%s' % pub_date
            if pub_date.count('/') == 1:
                pub_date = '01/' + pub_date #31/12/2019
            l.add_value('published_date', pub_date)

            charter_port = where.replace('(', '').replace(')', '').split(',')[0].lstrip().rstrip()
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



class CharterBoatUKBoatDetailsSpider(Spider):
    '''scrape specific boat details and add/edit to cb table.
    THIS USES A DIFFERENT PIPELINE. IT DOESNT GO INTO ugc
    '''
    name = "charterboatukdetails"
    source = 'www.charterboats-uk.co.uk'
    allowed_domains = ['www.charterboats-uk.co.uk']
    start_urls = ['http://www.charterboats-uk.co.uk/england/'] #just a place holder to kick stuff off
    base_url = 'https://www.charterboats-uk.co.uk'

    custom_settings = {'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter', 'ITEM_PIPELINES': {'imgscrape.pipelines.CBWriter': 10}}

    def parse(self, response):
        '''generate links to pages in a board        '''
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        BOARDS = ['charterboatuk boats']
        URLS = ['http://www.charterboats-uk.co.uk/england']
        #page18 http://www.charterboats-uk.co.uk/england?page=18
        PAGES = [18]
        assert len(BOARDS) == len(URLS) == len(PAGES), 'Setup list lengths DO NOT match'

        for i, root_url in enumerate(URLS):
            curboard = BOARDS[i]
            urls = [root_url] #first page is just the base post url
            for x in range(2, PAGES[i] + 1):
                urls.append('%s?page=%s' % (urls[0], x))  #&page=2

            for url in urls:
                yield scrapy.Request(url, callback=self.crawl_boats, dont_filter=True, meta={'curboard':curboard})



    def crawl_boats(self, response):
        '''each page with links to 10 boats details
        '''
        curboard = response.meta.get('curboard')
        boats = response.selector.xpath('//div[@id="boat_list"]/table/tbody/tr')
        for boat in boats:
            url = boat.xpath('./td[@class="first"]/a/@href').extract()
            url = response.urljoin(url[0])
            boat_name = boat.xpath('./td[@class="first"]/a/text()').extract()[0]
            location = boat.xpath('(.//div[@class="port_and_location"]/a)[1]/text()').extract()[0]
            location = get_port_name(location)
            yield scrapy.Request(url, callback=self.boat_details, dont_filter=True, meta={'curboard':curboard, 'boat_name':boat_name, 'location':location})


    def boat_details(self, response):
        '''crawl'''
        curboard = response.meta.get('curboard')
        location = response.meta.get('location')
        location = get_port_name(location)
        boat_name = response.meta.get('boat_name')
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        
        l = _items.CBUKBoatLdr(item=_items.CBUKBoat(), response=response)

        l.add_value('harbour', location)
        l.add_value('boat', boat_name)

        distance = response.selector.xpath('(//div[@id="boat_additional_info"]/div)[2]/text()').extract()[0]
        ns = stringslib.numbers_in_str(distance, int) #this will be nautical miles, a nautical mile of 1852 metres
        if ns:
            if ns[0] > 2: #3 is smallest
                ns = ns[0]
            else:
                ns = None
        else:
            ns = None
        l.add_value('distance', ns)

        passengers = response.selector.xpath('(//div[@id="boat_additional_info"]/div)[1]/text()').extract()[0]
        if 'passengers' in passengers:
            ns = stringslib.numbers_in_str(passengers, int)
            passengers = ns[0] if ns else None
        else:
            passengers = None
        l.add_value('passengers', passengers)


        I = l.load_item()
        yield I



def get_port_name(port_):
    '''try and get the port name'''
    ext = ['harbour', 'marina', 'moorings']
    port = port_.lower()
    
    if port == 'bournemouth': return 'Poole Harbour'
    if port == 'eastbourne': return 'sovereign harbour'
    if port == 'harwich harbour': return 'felixstowe'
    if port == 'southend-on-sea': return 'Two Tree Island Slipway'

    G = gazetteerdb.SESSION.query(Gazetteer).filter_by(name=port).first()
    assert isinstance
    if not G:
        for h in ext:
            p = '%s %s' % (port.lstrip().rstrip(), h)
            G = gazetteerdb.SESSION.query(Gazetteer).filter_by(name=p).first()
            if G: continue
    if G:
        return G.name
    return port_


class CharterBoatUKBoatTextSpider(Spider):
    '''scrape all the text in on the boat details tab to write to ugc
    '''
    name = "charterboatukboattext"
    source = 'www.charterboats-uk.co.uk'
    allowed_domains = ['www.charterboats-uk.co.uk']
    start_urls = ['http://www.charterboats-uk.co.uk/england/'] #just a place holder to kick stuff off
    base_url = 'https://www.charterboats-uk.co.uk'

    custom_settings = {'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter', 'ITEM_PIPELINES': {'imgscrape.pipelines.UGCWriter': 10}}

    def parse(self, response):
        '''generate links to pages in a board        '''
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        BOARDS = ['charterboatuk boats']
        URLS = ['http://www.charterboats-uk.co.uk/england/']
        #page18 http://www.charterboats-uk.co.uk/england?page=18
        PAGES = [18]
        assert len(BOARDS) == len(URLS) == len(PAGES), 'Setup list lengths DO NOT match'

        for i, root_url in enumerate(URLS):
            curboard = BOARDS[i]
            urls = [root_url] #first page is just the base post url
            for x in range(2, PAGES[i] + 1):
                urls.append('%s?page=%s' % (urls[0], x))  #&page=2

            for url in urls:
                yield scrapy.Request(url, callback=self.crawl_boats, dont_filter=True, meta={'curboard':curboard})



    def crawl_boats(self, response):
        '''each page with links to 10 boats details
        '''
        curboard = response.meta.get('curboard')
        boats = response.selector.xpath('//div[@id="boat_list"]/table/tbody/tr')
        for boat in boats:
            url = boat.selector.xpath('./td[@class="first"]/a/@href').extract()
            url = response.urljoin(url[0])
            boat_name = boat.xpath('./td[@class="first"]/a/text()').extract()[0]
            location = boat.xpath('(.//div[@class="port_and_location"]/a)[1]/text()').extract()[0]
            location = get_port_name(location)
            yield scrapy.Request(url, callback=self.boat_details, dont_filter=True, meta={'curboard':curboard, 'boat_name':boat_name, 'location':location})


    def boat_details(self, response):
        '''crawl'''
        location = response.meta.get('location')
        
        l = _items.CharterBoatUKLdr(item=_items.ForumUGC(), response=response)

        boat_name = response.meta.get('boat_name')
        l.add_value('boat', boat_name)
        
        curboard = response.meta.get('curboard')
        l.add_value('board', curboard)

        l.add_value('source', CharterBoatUKBoatTextSpider.source)
        l.add_value('url', response.url)
        l.add_value('title', '')
        l.add_value('platform_hint', 'charter')

        pub_date = '01/01/1900'
        l.add_value('published_date', pub_date)

        l.add_value('charter_port', location)

        txt = response.selector.xpath('//section[@id="details-tab"]//text()').extract()
        txt = ['\n'.join(txt)]
        l.add_value('txt', txt)

        author = 'charterboatuk'
        l.add_value('who', author)
        l.add_value('source_platform', '["charter"]')

        I = l.load_item()
        yield I
