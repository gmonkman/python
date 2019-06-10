# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''search, find, extract from text'''

from datetime import datetime as _dt
from dateparser.search import search_dates as _search_dates

import mmo.name_entities as _ne

def get_dates(s, fmt='%Y%m%d %H:%M'):
    '''(str, str) -> list|None
    extracts dates found in text as list or none

    default format is ISO - ready for SQL Server
    '''
    D = _search_dates(s, languages=['en'], settings={'DATE_ORDER': 'DMY', 'languages':['en'], 'locales':['en-GB']})
    return [_dt.strftime(d[1], fmt) for d in D]
    #for dstr, dt in D:
     #   for mth in _ne.DateTimeMonth.nouns_dict:
      #      if mth in dstr:
       #         return _dt.strftime(dt, fmt)
    return None
