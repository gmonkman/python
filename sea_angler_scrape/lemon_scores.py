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

_LOG_FILE = 'c:/temp/jupyter/sa_scrape.log'
_ERR_FILE = 'c:/temp/jupyter/sa_errs.log'
_LINKS_PKL = 'c:/temp/jupyter/sa_links.pkl'

_LOG_LIST = []
_ERR_LIST = []
_STALE_CNT = 0


class Game():
    score

URLS = ['https://www.lemon64.com/?mainurl=https%3A//www.lemon64.com/games/details.php%3FID%3D' + ('000%s' % x)[-4:] for x in range(6, 4198)]
def get_links(elements):
    '''get the four page links'''
    out = []
    for el in elements:
        try:
            out.append(el.get_attribute('href'))
        except selenium.common.exceptions.StaleElementReferenceException:
            global _STALE_CNT
            _STALE_CNT += 1
    return out

def unpkl_n():
    '''doc'''
    if  iolib.file_exists(N_PKL):
        n = baselib.unpickle(N_PKL)
        return n
    else:
        return 1


def unpkl_links():
    '''doc'''
    if iolib.file_exists(_LINKS_PKL):
        lst = baselib.unpickle(_LINKS_PKL)
        return lst
    else:
        return []





#region ENTRY
def main():
    '''execute if script was entry point'''
    browser = webdriver.Firefox()
    url = 'https://www.actionlibrary.com/cgi-bin/emapwww'
    browser.get(url)
    wait = WebDriverWait(browser, 15)



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



    #main work
    #Login Page
    usr = wait_name('_LGIN_Username')
    pw = wait_name('_LGIN_Password')

    usr.send_keys('patricia')

    pw.send_keys('patricia1')
    sleep(0.5)
    login_button = wait_class_name('buttonstandard')
    login_button.click()
    #sleep(5)

    #Switch to Feature Search For Sea Angler
    browser.switch_to.default_content()
    browser.switch_to.frame('emapwww_Navigation')
    sleep(1)
    a_search = wait_link('Feature Search')
    a_search.click()
    sleep(1)
    browser.switch_to.default_content()
    browser.switch_to.frame("emapwww_MainSection")
    print('waiting for [editionsinfo]publicationText...')
    tb_sa = wait_name('[editionsinfo]publicationText')
    print(tb_sa)
    tb_sa.send_keys('Sea Angler')
    sleep(1)
    btn_search = wait_xpath('//input[@value="Search"]')
    btn_search.click()
    sleep(1) #bug
    btn_search = wait_xpath('//input[@value="Search"]')
    btn_search.click()

    n = unpkl_n()
    if n > 1:
        n += 4 #if we have saved n, it will be the last good link scrape
    ElementHasChanged.SCRAPED_LINKS = unpkl_links()


    #Generate the links, save as pickle
    PP = iolib.PrintProgress(maximum=sum([1 for x in range(n, 17026, 4)]), init_msg='Getting all page links ...')


    for x in range(n, 17026, 4):
        s = "DoScroll('%s', 'PageHitList', '');" % x
        sleep(random.uniform(0, 1) + 0.1)
        suffix = 'Errs:%s  Stale:%s   ' % (len(_ERR_LIST), _STALE_CNT)

        try:
            browser.execute_script(s)
            elements = WebDriverWait(browser, 10).until(ElementHasChanged(browser))
        except Exception as e:
            _ERR_LIST.append('Getting link for n=%s failed. The error was %s' % (n, e))
            PP.increment(suffix=suffix)
            continue

        links = get_links(elements)
        if links:
            ElementHasChanged.SCRAPED_LINKS.extend(links)
        baselib.pickle(x, N_PKL)
        baselib.pickle(ElementHasChanged.SCRAPED_LINKS, _LINKS_PKL)
        PP.increment(suffix=suffix)

    all_links = set(ElementHasChanged.SCRAPED_LINKS)
    if links:
        baselib.pickle(ElementHasChanged.SCRAPED_LINKS, _LINKS_PKL)
        print('Saved links to %s' % _LINKS_PKL)
    else:
        print('No links!!')

    if _ERR_LIST:
        iolib.writecsv(_ERR_FILE, _ERR_LIST, inner_as_rows=True)
        print('Errors written to %s' % _ERR_FILE)




#This only executes if this script was the entry point
if __name__ == '__main__':
    #execute my code
    main()
#endregion

