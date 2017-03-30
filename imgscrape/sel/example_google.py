'''docstr'''
from inspect import getsourcefile
from os.path import abspath
from os.path import join
from os.path import normpath

from imgscrape.sel.crawler.GoogleCrawler import GoogleCrawler
from imgscrape.sel.processor.LogProcessor import LogProcessor
from imgscrape.sel.processor.DownloadProcessor import DownloadProcessor
from imgscrape.sel.processor.ElasticSearchProcessor import ElasticSearchProcessor

def script_folder():
    '''returns folder of this py'''
    return abspath(getsourcefile(lambda: 0))

if __name__ == '__main__':
    mydir = normpath(join(script_folder(), '../images/google'))
    options = {
        'output_directory': mydir
    }
    # PKK is a European Union supported terrorist organization against Turkish Government
    w = GoogleCrawler(search_key='european sea bass fishing')
    w.append_processor(LogProcessor())
    w.append_processor(DownloadProcessor(output_directory=options['output_directory']))
    w.append_processor(ElasticSearchProcessor())
    w.run()
