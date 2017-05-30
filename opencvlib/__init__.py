# pylint: disable=C0103, locally-disabled

'''opencvlib'''
from opencvlib.common import getimg, show, checkwaitkey, getwaitkey, showarray
from opencvlib.common import ImageInfo, Info, mosaic, eImgType, CVColors


IMAGE_EXTENSIONS = ('.bmp',
                    '.jpg',
                    '.jpeg',
                    '.png',
                    '.tif',
                    '.tiff',
                    '.pbm',
                    '.pgm',
                    '.ppm')

IMAGE_EXTENSIONS_AS_WILDCARDS = ('*.bmp',
                                 '*.jpg',
                                 '*.jpeg',
                                 '*.png',
                                 '*.tif',
                                 '*.tiff',
                                 '*.pbm',
                                 '*.pgm',
                                 '*.ppm')

__all__ = ['classifiers', 'common',
           'decs', 'distance',
           'edges', 'errors',
           'faces', 'features',
           'hogview', 'keypoints',
           'perspective', 'roi', 'streams',
           'transforms', 'winpyr']



#Global logger
#To use:
#<package>.info("informational message")
#<package>.debug("debug message")
#<package>.critical("informational message")
try:
    import os.path as _path
    import funclib.log as _log
    _logfile = _path.join(_log.RootLogger.USER_TEMP_FOLDER, 'opencvlib.log')
    _rootlogger = _log.RootLogger(_logfile)
    Log = _rootlogger.logger
    print('Logging to', _logfile)
except Exception as e:
    print('Logger initialisation failed for file %s.\nError: %s' % (_logfile, str(e)))


def loginfo():
    '''print log file status'''
    try:
        print(_rootlogger)
    except Exception as e:
        print('Failed to get log info for file %s.\nError: %s' % (_logfile, str(e)))
