'''docstr'''
from imgscrape.sel.crawler.YandexCrawler import YandexCrawler
from imgscrape.sel.processor.LogProcessor import LogProcessor
from imgscrape.sel.processor.DownloadProcessor import DownloadProcessor
from inspect import getsourcefile
from os.path import abspath
from os.path import join
from os.path import normpath
if __name__ == '__main__':
    options = {
        'output_directory': normpath(join(script_folder(), '../images/yandex'))
    }
    w = YandexCrawler(search_key='PYD')
    w.append_processor(LogProcessor())
    w.append_processor(DownloadProcessor(output_directory=options['output_directory'], process_count=16))
    w.run()

def script_folder():
    '''returns folder of this py'''
    return abspath(getsourcefile(lambda: 0))
