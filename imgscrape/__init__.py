#pylint: skip-file

'''main init for imgscrape
but says similiar lines in 2 files'''

__all__ = ['exec', 'helpers', 'items', 'pipelines', 'settings']

GOOGLE_CACHE_ROOT = "http://webcache.googleusercontent.com/search?q=cache:"

def totextfile(s, fname):
    '''to text'''
    with open(fname, "w") as text_file:
        text_file.write(s)