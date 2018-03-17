# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''Read pgnet.ini settings'''
from os import path as _path
import funclib.inifilelib as _ini
import pgnet as _pgnet
from funclib.inifilelib import eReadAs

_MODULE_ROOT = _path.normpath(_pgnet.__path__[0]) #root of opencvlib
Cfg = _ini.ConfigFile(_path.normpath(_path.join(_MODULE_ROOT, 'pgnet.ini')))
