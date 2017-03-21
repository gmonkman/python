#pylint: skip-file
'''execute scrapers to debug'''
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import imgscrape.spiders.angling_addicts as aa

#process = CrawlerProcess({'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'})
process = CrawlerProcess(get_project_settings())

#c = wp.TestSpider()
c = aa.AnglingAddictsImageSpider()

process.crawl(c)
process.start()
