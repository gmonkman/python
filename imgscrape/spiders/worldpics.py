# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable, anomalous-backslash-in-string, no-self-use
'''worldseafishing spiders'''
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from imgscrape.items import PostedImages

class WorldSeaFishingImageSpider(CrawlSpider):
    '''scrape images from wirralseafishing forum'''
    #http://www.wirralseafishing.co.uk/forum/phpBB2/viewforum.php?f=57&start=90

    name = "world-pics"
    allowed_domains = ['wirralseafishing.co.uk']

    last_link = 4740
    posts_per_page = 30
    urls = ['http://www.wirralseafishing.co.uk/forum/phpBB2/viewforum.php?f=57',]

    for x in range(posts_per_page, last_link+30, posts_per_page):
        urls.append(urls[0] + "&start=%s" % x)

    # returns request objects
    def start_requests(self):
        '''handle requests'''
        for url in self.urls:
            yield scrapy.Request(url, self.parse)

    rules = (
        Rule(LinkExtractor(allow=('viewtopic\.php', )), callback='parse_images'),
    )

    def parse_images(self, response):
        '''parse'''
        img = PostedImages()
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        #self.logger.info('thread link %s', response.url)
        img['image_urls'] = list(response.xpath('//img[contains(@class, "postimage")]/@src').extract())
        return img
