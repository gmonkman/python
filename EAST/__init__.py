'''load config from EAST.ini into ini'''
import os as _os
import EAST.ini as ini

__all__ = ['icdar', 'ini', 'locality_aware_nms', 'model']

_os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
_os.environ['CUDA_VISIBLE_DEVICES'] = str(ini.Regions_py.GPU_LIST)

NMS_MODES = ['none', 'simple', 'pylanms', 'cpplanms']
