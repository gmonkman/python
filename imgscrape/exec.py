import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import imgscrape.spiders.wirralpics as wp

#process = CrawlerProcess({'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'})
process = CrawlerProcess(get_project_settings())

#c = wp.TestSpider()
c = wp.wirral_pic_spider()

process.crawl(c)
process.start()