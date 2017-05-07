# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''filters to be consumed in generators.

All functions should return a boolean and receive an ndarray (image) as the first argument.

A return boolean of True, would keep the image, false indicated it should not be
yielded from the generator

Filters
'''

from opencvlib.common import ImageInfo as _ImageInfo


is_higher_res = _ImageInfo.is_higher_res
is_lower_res = _ImageInfo.is_lower_res
