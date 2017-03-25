# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable,anomalous-backslash-in-string,no-self-use
'''wirralseafishing spiders'''
import scrapy
from scrapy.spiders import CrawlSpider, Rule
#from scrapy.spiders import Spider
from scrapy.linkextractors import LinkExtractor
from imgscrape.items import PostedImages

class SeaAnglingReportsGallery(CrawlSpider):
    '''scrape images from wirralseafishing forum'''
    #http://seaanglingreports.co.uk/index.php?PHPSESSID=84c256387fc1c4196efd23d7e9cf1cd1&action=gallery;cat=1;start=0
    #http://seaanglingreports.co.uk/index.php?PHPSESSID=84c256387fc1c4196efd23d7e9cf1cd1&action=gallery;cat=1;start=20

    name = "seaanglingreports_gallery-pics"
    allowed_domains = ['seaanglingreports.co.uk']
    posts_per_page = 20

    start_urls = ['http://seaanglingreports.co.uk/index.php?PHPSESSID=84c256387fc1c4196efd23d7e9cf1cd1&action=gallery;cat=1;start=' + str(x) for x in list(range(posts_per_page, 11*posts_per_page, posts_per_page))]

    rules = (
        Rule(LinkExtractor(restrict_xpaths='//tr[contains(@class,"windowbg")]/td/a'), callback='parse_images'),
    )

    def parse_images(self, response):
        '''extract images in posts'''
        img = PostedImages()
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        img['image_urls'] = list(response.xpath('//table[contains(@class, "tborder")]//img/@src').extract())
        pass
        return img
