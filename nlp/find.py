# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument

'''search, find, extract from text'''
from datetime import datetime as _dt
from dateparser.search import search_dates as _search_dates



def get_dates(s, fmt='%Y%m%d %H:%M'):
    '''(str, str) -> list|None
    extracts dates found in text as list or none

    default format is ISO - ready for SQL Server
    '''
    D = _search_dates(s, settings={'DATE_ORDER': 'DMY'})
    return [_dt.strftime(d[0][1], fmt) in D]
