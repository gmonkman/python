# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
from time import sleep
import random

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
import selenium.webdriver.support.expected_conditions as EC

import funclib.baselib as baselib
import funclib.iolib as iolib
import funclib.baselib as baselib
from sea_angler_scrape.config import Settings


_LOG_FILE = 'c:/temp/get_lemon64.log'
_ERR_FILE = 'c:/temp/get_lemon64.log'
_GAMES_PKL = 'c:/temp/get_lemon64.pkl'




_LOG_LIST = []
_ERR_LIST = []
_STALE_CNT = 0

URLS = ['https://www.lemon64.com/?mainurl=https%3A//www.lemon64.com/games/details.php%3FID%3D' + ('000%s' % x)[-4:] for x in range(Settings.start, Settings.stop)]



class Game():
    '''game cls'''
    def __init__(self, url, full_title, score=0, votes=0, year_released=None):
        if not isinstance(full_title, str): raise ValueError('Full title was not a string')
        if full_title is None: raise ValueError('Full title was None')
        

        self.full_title = full_title.lower()
        self.year_released = year_released
        self.score = score
        self.votes = votes
        self.url = url



def unpkl_links():
    '''doc'''
    if iolib.file_exists(_GAMES_PKL):
        lst = baselib.unpickle(_GAMES_PKL)
        return lst
    else:
        return []





#region ENTRY
def main():

    '''execute if script was entry point'''
    browser = webdriver.Firefox()
    wait = WebDriverWait(browser, 10)


    class ElementHasChanged():
        SCRAPED_LINKS = []

        def __init__(self, locator):
            self.locator = locator

        def __call__(self, browser):
            s = '//a[contains(@href, "emapwww?Page=DoPageSearch&Action=EditionPages&EditionURN=")]'
            try:
                elements = browser.find_elements_by_xpath(s)
            except Exception as e:
                was_err = True

            if elements:
                lnks = get_links(elements)
                was_err = all([s in ElementHasChanged.SCRAPED_LINKS for s in lnks])
            else:
                was_err = True

            if was_err:
                return False
            else:
                return elements


    def wait_name(s):
        '''doc'''
        return wait.until(EC.presence_of_element_located((By.NAME, s)))


    def wait_class_name(s):
        '''doc'''
        return wait.until(EC.presence_of_element_located((By.CLASS_NAME, s)))


    def wait_link(s):
        '''doc'''
        return wait.until(EC.presence_of_element_located((By.LINK_TEXT, s)))


    def wait_xpath(s):
        '''doc'''
        return wait.until(EC.presence_of_element_located((By.XPATH, s)))



    
    PP = iolib.PrintProgress(URLS)
    try:
        games = unpkl_links()
    except:
        pass

    processed_urls = [x.url for x in games]
    unprocessed_urls = [url for url in URLS if url not in processed_urls]
    PP = iolib.PrintProgress(unprocessed_urls)
    for url in unprocessed_urls:
        try:
            sleep(random.uniform(1, 3) + 1)
            browser.get(url)
        
            #wait = WebDriverWait(browser, 2)
            browser.switch_to.default_content()
            browser.switch_to.frame('content')
            
            score_element = wait_xpath('//img[contains(@src, "score.gif")]')
            score = score_element.get_attribute('title')

            full_name_element = wait_xpath('//td[@class="normalheadblank"]/div[@style="float: left"]')
            full_name = full_name_element.text
    
            year_element = wait_xpath('//td[@class="normalheadblank"]/div[@style="float: right"]/a/b')
            year = year_element.text

            vote_element = wait_xpath('(//form[@id="games"]/table)[1]//strong')
            vote = vote_element.text
        
            year = int(year)
            score = float(score)
            votes = int(vote)
            if full_name_element:
                games.append(Game(url, full_name, score, votes, year))
        except Exception as e:
            print(e)


        PP.increment()

        
    baselib.pickle(games, _GAMES_PKL)
    print('Saved games to %s' % _GAMES_PKL)



#This only executes if this script was the entry point
if __name__ == '__main__':
    #execute my code
    main()
#endregion

