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


class Eval_py():
    '''eval.py settings'''
    MASK_MERGE_KERNEL_RATIO = _ConfigFile.tryread('eval.py', 'MASK_MERGE_KERNEL_RATIO', value_on_create='0.01')
    MASK_JOIN_ITER = _ConfigFile.tryread('eval.py', 'MASK_MERGE_KERNEL_RATIO', value_on_create='20')
    PROGRESS_STATUS_FILE = _ConfigFile.tryread('eval.py', 'PROGRESS_STATUS_FILE')
    RETRY_FAILED = _ConfigFile.tryread('eval.py', 'RETRY_FAILED')
    CHECKPOINT_PATH = _path.normpath(_ConfigFile.tryread('eval.py', 'CHECKPOINT_PATH'))
