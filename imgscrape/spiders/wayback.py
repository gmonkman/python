# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable,anomalous-backslash-in-string,no-self-use
'''wayback spiders'''
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from imgscrape.items import PostedImages


class WorldSeaFishing(CrawlSpider):
    '''scrape images from goangling.co.uk'''
    name = "wayback-worldseafishing"
    allowed_domains = ['archive.org']


    start_urls = ['http://goangling.co.uk/category/photo-gallery/',
                  'http://goangling.co.uk/category/photo-gallery/page/2/'
                  'http://goangling.co.uk/category/photo-gallery/page/3/'
                  'http://goangling.co.uk/category/photo-gallery/page/4/'
                  'http://goangling.co.uk/category/photo-gallery/page/5/'
                  'http://goangling.co.uk/category/photo-gallery/page/6/'
                  ]

    rules = (
        Rule(LinkExtractor(restrict_xpaths='//h2[contains(@class,"entry-title")]/a'), callback='parse_images'),
    )

    def parse_images(self, response):
        '''extract images in posts'''
        img = PostedImages()
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        img['image_urls'] = list(response.xpath('//div[contains(@class,"entry-content clearfix")]//a/@href').extract())
        return img
