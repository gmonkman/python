# pylint: disable=C0302, line-too-long, too-few-public-methods, too-many-branches, too-many-statements, no-member
'''Has config file settings read from mmodb.ini

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
_INIPATH = _path.normpath(_path.join(_PTH, 'gazetteerdb.ini'))
_ConfigFile = _inifilelib.ConfigFile(_INIPATH)


server = _ConfigFile.tryread('db', 'server')
security = _ConfigFile.tryread('db', 'security')
user = _ConfigFile.tryread('db', 'user')
password = _ConfigFile.tryread('db', 'password')
dbname = _ConfigFile.tryread('db', 'dbname')
is_integrated = _ConfigFile.tryread('db', 'security').lower() == 'integrated'
