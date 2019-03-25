# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''This module contains various misc helper functions'''



def google_cache_url(url):
    '''(str)->str

    Takes a url and creates the google cache link
    for that URL
    '''
    # http://webcache.googleusercontent.com/search?q=cache:
    assert url[0:4].lower() == 'http', 'URL does not start with http'
    return imgscrape.GOOGLE_CACHE_ROOT + url

