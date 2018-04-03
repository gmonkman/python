# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import
'''Read pgnet.ini settings'''
from os import path as _path
import funclib.inifilelib as _ini
import dliblib as _dliblib
from funclib.inifilelib import eReadAs #unused, but exposed here for convieniance

_MODULE_ROOT = _path.normpath(_dliblib.__path__[0]) #root of opencvlib
Cfg = _ini.ConfigFile(_path.normpath(_path.join(_MODULE_ROOT, 'dliblib.ini')))
