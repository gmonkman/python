'''load config from EAST.ini into ini'''
import os as _os

from pysimplelog import Logger as _Logger

import funclib.iolib as _iolib
import EAST.ini as ini

__all__ = ['icdar', 'ini', 'locality_aware_nms', 'model']

_os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
_os.environ['CUDA_VISIBLE_DEVICES'] = str(ini.Regions_py.GPU_LIST)

NMS_MODES = ['none', 'simple', 'pylanms', 'cpplanms']


_iolib.files_delete2(ini.EAST.LOG_FILE)
Log = _Logger(name='EAST', logToStdout=False, logToFile=True, logFileMaxSize=2)
Log.set_log_file(ini.EAST.LOG_FILE)