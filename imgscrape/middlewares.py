#pylint: skip-file
import json as _json
from datetime import datetime as _dt

from scrapy import Request
from scrapy.http import Response
from scrapy.exceptions import IgnoreRequest



class UnhandledIgnoreRequest(IgnoreRequest):
    pass
