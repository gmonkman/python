# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, misplaced-bare-raise

'''base crawler'''
import os
from inspect import getsourcefile
from os.path import abspath
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class BaseCrawler(ABC):
    '''docstr'''
    def __init__(self, search_key, **kwargs):
        '''(str|list, [process_count=, max_image_count=])'''
        if isinstance(search_key, str):
            self.g_search_key_list = [search_key]
        else:
            self.g_search_key_list = list(search_key)

        self.g_search_key = ''
        self.target_url_str = ''

        ## storage
        self.pic_url_list = []
        self.pic_info_list = []

        self.process_count = kwargs.get('process_count', os.cpu_count())
        self.max_image_count = kwargs.get('max_image_count', 622)

        # google search specific url parameters
        self.search_url_prefix = None
        self.search_url_postfix = None

        self.processor_list = []

    def reformat_search_for_spaces(self):
        """
            Method call immediately at the initialization stages
            get rid of the spaces and replace by the "+"
            Use in search term. Eg: "Cookie fast" to "Cookie+fast"

            steps:
            strip any lagging spaces if present
            replace the self.g_search_key
        """
        self.g_search_key = self.g_search_key.rstrip().replace(' ', '+')

    def set_max_image_count(self, num_image):
        """ Set the number of image to download. Set to self.image_dl_per_search.
            Args:
                num_image (int): num of image to download.
        """
        self.max_image_count = num_image

    def append_processor(self, processor):
        '''docstr'''
        self.processor_list.append(processor)

    def formed_search_url(self):
        ''' Form the url either one selected key phrases or multiple search items.
            Get the url from the self.g_search_key_list
            Set to self.sp_search_url_list
        '''
        self.reformat_search_for_spaces()
        self.target_url_str = self.search_url_prefix + self.g_search_key + self.search_url_postfix

    def create_selenium_driver(self):
        '''docstr'''
        # driver = webdriver.Chrome()
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"
        )
        driver = webdriver.PhantomJS(desired_capabilities=dcap)
        driver.set_window_size(1024, 768)
        return driver

    @abstractmethod
    def load_page(self, driver):
        '''docstr'''
        pass

    @abstractmethod
    def extract_pic_url(self, driver):
        '''docstr'''
        driver.quit()

    def run(self):
        '''docstr'''
        for search in self.g_search_key_list:
            self.pic_url_list = []
            self.pic_info_list = []
            self.g_search_key = search
            self.formed_search_url()
            driver = self.create_selenium_driver()
            self.load_page(driver)
            self.extract_pic_url(driver)
            self.process_all_images()

    def process_all_images(self):
        '''docstr'''
        for processor in self.processor_list:
            processor.before_process()

        search_term = self.g_search_key.rstrip()

        if self.max_image_count < len(self.pic_url_list):
            self.pic_url_list = self.pic_url_list[:self.max_image_count]

        for preview_url, original_url in self.pic_url_list:
            for processor in self.processor_list:
                processor.process(preview_url, original_url, search_term)

        for processor in self.processor_list:
            processor.after_process()

    def script_folder(self):
        '''returns folder of this py'''
        return abspath(getsourcefile(lambda: 0))

    def save_infolist_to_file(self):
        """ Save the info list to file."""
        temp_filename_full_path = os.path.join(self.script_folder(), self.g_search_key + '_info.txt')

        with open(temp_filename_full_path, 'w') as f:
            for n in self.pic_info_list:
                f.write(n)
                f.write('\n')
