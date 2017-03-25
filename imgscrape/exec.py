#pylint: skip-file
'''execute scrapers to debug'''
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import imgscrape.spiders.angling_addicts as aa
import imgscrape.spiders.sunnyrhyl as sr
import imgscrape.spiders.seaanglingireland as sai
import imgscrape.spiders.seaanglingreports as sar
import imgscrape.spiders.goangling as go
#process = CrawlerProcess({'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'})
process = CrawlerProcess(get_project_settings())

#c = sai.SeaAnglingIrelandArchives()
#c = sai.SeaAnglingIrelandArchives()
#c = sar.SeaAnglingReportsGallery()
c = go.GoAnglingGallery()
process.crawl(c)
process.start()
