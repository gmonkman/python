import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.spiders import Spider
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from imgscrape.items import PostedImages

class wirral_pic_spider(CrawlSpider):
    '''scrape images from wirralseafishing forum'''
    #http://www.wirralseafishing.co.uk/forum/phpBB2/viewforum.php?f=57&start=90

    name = "wsf_pics"
    allowed_domains = ['wirralseafishing.co.uk']

    #last_link = 4740
    last_link = 60
    posts_per_page = 30
    urls = ['http://www.wirralseafishing.co.uk/forum/phpBB2/viewforum.php?f=57',]

 #   for x in range(posts_per_page,last_link+30,posts_per_page):
#        urls.append(urls[0] + "&start=%s" % x)

    # returns request objects
    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url, self.parse)

    rules = (
        Rule(LinkExtractor(allow=('viewtopic\.php', )), callback='parse_images'),
    )

    def parse_images(self, response):
        img = PostedImages()
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        #self.logger.info('thread link %s', response.url)
        img['image_urls'] = list(response.xpath('//img[contains(@class, "postimage")]/@src').extract())
        return img

class TestSpider(Spider):
    name = 'wirral-test'
    start_urls = ['http://www.wirralseafishing.co.uk/forum/phpBB2/viewtopic.php?f=57&t=30564&p=255306#p255306']

    def parse(self, response):
        return {'image_urls':list(response.xpath('//img[contains(@class, "postimage")]/@src').extract())}
