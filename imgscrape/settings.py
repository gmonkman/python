# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable
'''settings'''
BOT_NAME = 'imgscrape'
SPIDER_MODULES = ['imgscrape.spiders']
NEWSPIDER_MODULE = 'imgscrape.spiders'



#Item Pipelines
#ITEM_PIPELINES = {'scrapy.pipelines.images.ImagesPipeline': 1}
#IMAGES_STORE = 'C:/development/python/imgscrape/images'
#IMAGES_MIN_HEIGHT = 300
#IMAGES_MIN_WIDTH = 300

#ITEM_PIPELINES = {'scrapy.pipelines.files.FilesPipeline': 1}
#FILES_STORE = '/path/to/valid/dir'



#FEED
FEED_FORMAT = 'csv'
FEED_URI = 'file:.c:/temp/mp_fox_straglers.csv'


#USER_AGENT = 'quotesbot (+http://www.yourdomain.com)'
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 8

#Throttling
DOWNLOAD_DELAY = 0.5
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS_PER_DOMAIN = 5
CONCURRENT_REQUESTS_PER_IP = 5

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.2
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
