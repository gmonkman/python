#!/usr/bin/python
'''scrape from google cache'''
import urllib.request as request
import re
import socket
import os
import time
import random, math



import funclib.iolib as iolib
import funclib.stringslib as stringslib


socket.setdefaulttimeout(30)

#adjust the site here
SEARCH_SITE = 'www.anglersnet.co.uk'
URL = 'https://www.google.com/search?safe=off&q=site:www.anglersnet.co.uk%2Fforums+%22sea+fishing%22'
SAVE_DIR = 'C:/Users/Graham Monkman/OneDrive/Documents/MMOMapping/data/Data sources and sites/www/googlecache/test'
search_term="site:" + SEARCH_SITE + "%2Fforums+%22sea+fishing%22"




def mkdir_p(path):
    '''doc'''
    iolib.create_folder(path)


def main():
    '''main'''
    headers = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686 (x86_64); en-US; rv:1.8.1.4) Gecko/20070515 Firefox/2.0.0.4'}
    regex_cache = re.compile(r'<a href="([^"]*)"[^>]*>Cached</a>')
    regex_next = re.compile('<a href="([^"]*)"[^>]*><span[^>]*>[^<]*</span><span[^>]*>Next</span></a>')
    regex_url = re.compile(r'search\?q=cache:[\d\w-]+:([^%]*)')
#    regex_title = re.compile('<title>([\w\W]+)</title>')
#    regex_time = re.compile('page as it appeared on ([\d\w\s:]+)')
    regex_pagenum = re.compile('<a href="([^"]*)"[^>]*><span[^>]*>[^<]*<\/span>([\d]+)')

    #this is the directory we will save files to
    mkdir_p(SAVE_DIR)
    path = os.path.dirname(os.path.abspath(__file__)) + '\\' + SEARCH_SITE
    mkdir_p(path)
    counter = 0
    pagenum = int(math.floor(len([name for name in os.listdir(path)]) / 10) + 1)
    max_goto = 0;
    more = True
    if (pagenum > 1):
        while (max_goto < pagenum):
            req = urllib.request.Request(URL, None, headers)
            page = stringslib.to_ascii(urllib.request.urlopen(req).read())
            goto = regex_pagenum.findall(page)
#            print goto
            for goto_url, goto_pagenum in goto:
                goto_pagenum = int(goto_pagenum)
                if (goto_pagenum == pagenum):
                    url = "http://www.google.com" + goto_url.replace('&amp;', '&')
                    max_goto = pagenum
                    break
                elif (goto_pagenum < pagenum and max_goto < goto_pagenum):
                    max_goto = goto_pagenum
                    url = "http://www.google.com" + goto_url.replace('&amp;', '&')
            random_interval = random.randrange(5, 20, 1)
            print("sleeping for: " + str(random_interval) + " seconds")
            print("going to page: " + str(max_goto))
            print(url)
            time.sleep(random_interval)


    while(more):
        #Send search request to google with pre-defined headers
        req = request.Request(URL, None, headers)
        #open the response page
        page = str(request.urlopen(req).read(), 'utf8')
        #find all cache in the page
        matches = regex_cache.findall(page)
        #loop through the matches
        for match in matches:
            counter+=1
            #find the url of the page cached by google
            the_url = regex_url.findall(match)
            the_url = the_url[0]
            the_url = the_url.replace('http://', '')
            the_url = the_url.strip('/')
            the_url = the_url.replace('/', '-')
            #if href doesn't start with http insert http before
            if not match.startswith("http"):
                match = "http:" + match
            if (not the_url.endswith('html')):
                the_url = the_url + ".html"

            #if filename "$url"[.html] does not exists
            if not os.path.exists(SEARCH_SITE + "/" + the_url):
                tmp_req = urllib.request.Request(match.replace('&amp;', '&'), None, headers)
                try:
                    tmp_page = urllib.request.urlopen(tmp_req).read()
                    f = open(SEARCH_SITE + "/" + the_url, 'w')
                    f.write(tmp_page)
                    f.close()
                    print(counter, ": " + the_url)
                    #comment out the code below if you expect to crawl less than 50 pages
                    random_interval = random.randrange(15, 20, 1)
                    print("sleeping for: " + str(random_interval) + " seconds")
                    time.sleep(random_interval)
                except urllib.error.HTTPError as e:
                    print('Error code: ', e.code)
                    pass
        #now check if there is more pages
        match = regex_next.search(page)
        if match == None:
            more = False
        else:
            url = "http://www.google.com"+match.group(1).replace('&amp;', '&')

if __name__=="__main__":
    main()
