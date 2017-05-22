# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''
Load configs for script_objdetect scripts.

These will be the main scripts to perform object detection
related tasks
'''
import os.path as _path
from inspect import getsourcefile as _getsourcefile

from funclib import inifilelib as _ini
import funclib.iolib as _iolib

_MODPATH = _iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
 

#Detector options, eg HOG and SIFT
_detCFG = _ini.ConfigFile(_path.join(_MODPATH, 'detectors.cfg'))

#MakeLobsterDescriptors, make_lobster_descriptors.py
_MLD = _ini.ConfigFile(_path.join(_MODPATH, 'make_lobster_descriptors.ini'))


class HOGConfig():
    '''read and load HOG params from detectors.cfg'''
    kwargs = _detCFG.tryread('HOG', 'kwargs', force_create=False, asType=_ini.eReadAs.ersDict)
    min_wdw_sz = _detCFG.tryread('HOG', 'min_wdw_sz', force_create=False, asType=_ini.eReadAs.ersTuple)
    step_size = _detCFG.tryread('HOG', 'kwargs', force_create=False, asType=_ini.eReadAs.ersTuple)
    nms_threshold = float(_detCFG.tryread('HOG', 'nms_threshold', force_create=False))
    downscale = float(_detCFG.tryread('HOG', 'downscale', force_create=False, value_on_create=1))


class MakeLobsterDescriptors():
    '''read and load config info for the
    make_lobster_descriptors.ini file'''
    output_dir = _MLD.tryread('PATHS', 'output_dir')
    vgg_dir = _MLD.tryread('PATHS', 'vgg_dir')
