# pylint: disable=C0302, line-too-long, too-few-public-methods, too-many-branches, too-many-statements, no-member
'''Has config file settings read from EAST.ini

ini.server: server name
ini.security: integrated else <anything else assumed as sqlserver>
ini.user: sql server user name
ini.password: sql server password for ini.user
'''


from inspect import getsourcefile as _getsourcefile
import os.path as _path

import funclib.iolib as _iolib
import funclib.inifilelib as _inifilelib


NMS_MODES = ['none', 'simple', 'pylanms', 'cpplanms']

_PTH = _iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
_INIPATH = _path.normpath(_path.join(_PTH, 'EAST.ini'))
_ConfigFile = _inifilelib.ConfigFile(_INIPATH)


class Db():
    '''db settings'''
    server = _ConfigFile.tryread('db', 'server')
    security = _ConfigFile.tryread('db', 'security')
    user = _ConfigFile.tryread('db', 'user')
    password = _ConfigFile.tryread('db', 'password')
    dbname = _ConfigFile.tryread('db', 'dbname')
    is_integrated = _ConfigFile.tryread('db', 'security').lower() == 'integrated'


class Regions_py():
    '''regions.py settings'''
    MASK_MERGE_KERNEL_RATIO = _ConfigFile.tryread('regions.py', 'MASK_MERGE_KERNEL_RATIO', value_on_create='0.01', astype=float)
    MASK_JOIN_ITER = _ConfigFile.tryread('regions.py', 'MASK_JOIN_ITER', value_on_create='20', astype=int)
    PROGRESS_STATUS_FILE = _ConfigFile.tryread('regions.py', 'PROGRESS_STATUS_FILE')
    RETRY_FAILED = _ConfigFile.tryread('regions.py', 'RETRY_FAILED', astype=int) #0 = dont retry, 1=retry
    CHECKPOINT_PATH = _path.normpath(_ConfigFile.tryread('regions.py', 'CHECKPOINT_PATH'))
    COSINE_DISTANCE_THRESH = _ConfigFile.tryread('regions.py', 'COSINE_DISTANCE_THRESH', astype=float)
    MIN_OUTLIER_DISTANCE_THRESH = _ConfigFile.tryread('regions.py', 'MIN_OUTLIER_DISTANCE_THRESH', astype=float)

    NMS_MODE = _ConfigFile.tryread('regions.py', 'NMS_MODE', astype=str, value_on_create='none').lower()
    assert NMS_MODE in NMS_MODES, 'Invalid nms_mode %s. nms_mode in %s' % (NMS_MODE, NMS_MODES)

    TEXT_SCALE = _ConfigFile.tryread('regions.py', 'TEXT_SCALE', astype=int, value_on_create=512)
    GPU_LIST = _ConfigFile.tryread('regions.py', 'GPU_LIST', astype=int, value_on_create=0)
    PAD_CONTOURS = _ConfigFile.tryread('regions.py', 'PAD_CONTOURS', astype=int, value_on_create=20, force_create=True)
