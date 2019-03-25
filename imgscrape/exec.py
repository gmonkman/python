#pylint: skip-file


'''execute scrapers to debug'''
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import imgscrape.spiders.angling_addicts as aa
import imgscrape.spiders.sunnyrhyl as sr
import imgscrape.spiders.seaanglingireland as sai
import imgscrape.spiders.seaanglingreports as sar
import imgscrape.spiders.goangling as go
import imgscrape.spiders.fox as fox
#process = CrawlerProcess({'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'})
process = CrawlerProcess(get_project_settings())

#c = sai.SeaAnglingIrelandArchives()
#c = sar.SeaAnglingReportsGallery()
c = fox.MPVotesFox()

process.crawl(c)
process.start()
#https://www.theyworkforyou.com/search/?q=dianne+abbot
#https://www.theyworkforyou.com/mp/11148/albert_owen/ynys_mon
#https://www.theyworkforyou.com/mp/10001/diane_abbott/hackney_north_and_stoke_newington
#https://www.theyworkforyou.com/mp/10133/jeremy_corbyn/islington_north/votes