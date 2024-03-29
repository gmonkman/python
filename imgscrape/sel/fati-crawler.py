'''fati-crawler'''
import pandas as pd
from imgscrape.sel.crawler.GoogleCrawler import GoogleCrawler
from imgscrape.sel.processor.LogProcessor import LogProcessor
from imgscrape.sel.processor.DownloadProcessor import DownloadProcessor

if __name__ == '__main__':

    options = {
        'output_directory': './fati',
        'max_image_count': 3
    }

    df = pd.read_csv("fati-test-products.csv")
    descriptions = df["description"].values
    for description in descriptions:
        print(description)
        w = GoogleCrawler(search_key=description, **options)
        w.append_processor(LogProcessor())
        w.append_processor(DownloadProcessor(output_directory=options['output_directory'], process_count=3))
        w.run()
