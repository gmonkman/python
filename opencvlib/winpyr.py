# pylint: disable=C0103, too-few-public-methods, locally-disabled,
'''sliding windows and pyramids'''

import opencvlib.transforms as _transforms
import opencvlib.geom as _geom
from opencvlib.common import _getimg


#from skimage.transform import _transforms.resize


def slide_win_abs(image, win_sz, step_sz, discard_partial=True):
    # http://www.pyimagesearch.com/2015/03/23/sliding-windows-for-object-detection-with-python-and-opencv/
    '''(str|ndarray, (int,int), int)-> yield (int, int, ndarray)
    Sliding window of defined absolute pixel size.

    Returns a region of the input image `image` of size equal
    to `window_size`. The first image returned top-left co-ordinates (0, 0)
    and are increment in both x and y directions by the `step_size` supplied.
    So, the input parameters are -
    * `image` - Input Image
    * `window_size` - Size of Sliding Window
    * `step_size` - Incremented Size of Window

    The function returns a tuple -
    (x, y, im_window)
    where
    * x is the top-left x co-ordinate
    * y is the top-left y co-ordinate
    * im_window is the sliding window image
    '''
    image = _getimg(image)
    for y in range(0, image.shape[0], step_sz[1]):
        for x in range(0, image.shape[1], step_sz[0]):
            window = image[y:y + win_sz[1], x:x + win_sz[0]]
            if discard_partial:
                if window.shape[0] != win_sz[1] or window.shape[1] != win_sz[0]:
                    continue
            else:
                yield (x, y, window)


def pyramid(image, scale=1.5, min_pyr_sz=(50, 50), yield_original=True):
    '''(ndarray|str, float, (int,int), bool)->ndarray, floatt
    Yields suceesively downsampled images (ndarrays)
    until the minsize in either width or height is reached.

    image:image or path to image
    scale:downsampling factor - width = width/1.5
    min_py_sz:  stop yielding when last image resolute below this tuple (X,Y)
    yield_original: yield the unresized image if true, else yields first resized.

    Yields: downsampled image, the downsample amount
    '''
    image = _getimg(image)
    #Note that
    # yield the original image
    downsample = 1
    if yield_original:
        yield image, downsample

    while True:
        downsample = 1 / scale
        w = int(image.shape[1] / scale)
        image = _transforms.resize(image, width=w)

        # if the resized image does not meet the supplied minimum
        # size, then stop constructing the pyramid
        if image.shape[0] < min_pyr_sz[1] or image.shape[1] < min_pyr_sz[0]:
            break

        # yield the next image in the pyramid
        yield image, downsample



def pyramid_pts(image, pts, scale=1.5, min_pyr_sz=(50, 50), yield_original=True):
    '''(ndarray|str, n,2-list, float, (int,int), bool)->ndarray, floatt
    Yields suceesively downsampled images (ndarrays)
    until the minsize in either width or height is reached.

    Also takes points and rescales them according to scale

    image:image or path to image
    pts:    points defining an roi to be scaled appropropriately, format is CVXY
            [[1,1],[10,10] ... ]
    scale:downsampling factor - width = width/1.5
    min_py_sz:  stop yielding when last image resolute below this tuple (X,Y)
    yield_original: yield the unresized image if true, else yields first resized.

    Yields: downsampled image, the downsample amount
    '''
    pts_scaled = list(pts)
    image = _getimg(image)
    #Note that
    # yield the original image
    downsample = 1
    if yield_original:
        yield image, pts_scaled, downsample

    while True:
        downsample = downsample / scale
        pts_scaled = _geom.rescale_points(pts_scaled, scale)
        w = int(image.shape[1] / scale)
        image = _transforms.resize(image, width=w)

        # if the resized image does not meet the supplied minimum
        # size, then stop constructing the pyramid
        if image.shape[0] < min_pyr_sz[1] or image.shape[1] < min_pyr_sz[0]:
            break

        # yield the next image in the pyramid
        yield image, pts_scaled, downsample



def pyrwin(image, scale=1.5, min_pyr_size=(100, 100), win_func=slide_win_abs, **win_func_args):
    '''(str|ndarray, float, (int,int), bool, function, function kwargs)->yield (int, int, ndarray)
    combines pyramid and a sliding window function (win_func) to yield window regions
    Yields:(x, y, window)

    min_pyr_size: stop when row or cols below respective pixel size
    discard_partial: discard windows below a size passed to the sliding window func win_func

    Supported windows functions:
    slide_win_abs(image, win_sz, step_sz)
    '''
    image = _getimg(image)
    for resized in pyramid(image, scale=scale, min_pyr_sz=min_pyr_size):  # loop over the image pyramid
            # loop over the sliding window for each layer of the pyramid
        for x, y, window in win_func(resized, **win_func_args):
            yield (x, y, window)
