# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import
'''transforms compatible with generators Transform framework'''


from opencvlib.transforms import adjust_gamma, adjust_log, adjust_sigmoid, BGR2RGB
from opencvlib.transforms import compute_average2, equalize_adapthist, equalize_hist
from opencvlib.transforms import histeq, histeq_adapt, histeq_color
from opencvlib.transforms import rescale_intensity, resize, RGB2BGR, togreyscale
from opencvlib.transforms import Transforms, Transform
