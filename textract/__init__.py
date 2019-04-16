# pylint: skip-file
'''main init for dblib package'''
from pysimplelog import Logger as _Logger

import textract.ini as ini
import funclib.iolib as _iolib


__all__ = ['ini', 'samag', 'tesseractlib']


_iolib.files_delete2(ini.textract.log_file)
Log = _Logger(name='tesseract', logToStdout=False, logToFile=True, logFileMaxSize=2)
Log.set_log_file(ini.textract.log_file)
Log.info('test')
