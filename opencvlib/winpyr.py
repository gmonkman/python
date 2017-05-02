# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# no-self-use, unused-argument
'''sliding windows and pyramids'''
# DEBUG Module requires debugging
#import numpy as np

# this decorators handles func taking an image (ndarray) or imagepath as
# the first arg

from opencvlib.processing import resize
from opencvlib.decs import decgetimg

#from skimage.transform import resize

@decgetimg
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
    for y in range(0, image.shape[0], step_sz[1]):
        for x in range(0, image.shape[1], step_sz[0]):
            window = image[y:y + win_sz[1], x:x + win_sz[0]]
            if discard_partial:
                if window.shape[0] != win_sz[1] or window.shape[1] != win_sz[0]:
                    continue
            else:
                yield (x, y, window)


#@decgetimg
#def slide_win_prop(image, prop_sz, step_sz, discard_partial=True):
#    '''(str|ndarray, float, (int,int), bool)->yield (int,int,ndarray)
#    Sliding window of defined absolute pixel size.

#    Returns a region of the input image `image with the window size used
#    calculated from prop_sz. This is to handle images of different resolutions.

#    The first image returned top-left co-ordinates (0, 0)
#    and are increment in both x and y directions by the `step_size` supplied.
#    So, the input parameters are -
#    * `image` - Input Image
#    * `window_size` - Size of Sliding Window
#    * `step_size` - Incremented Size of Window

#    The function returns a tuple -
#    (x, y, im_window)
#    where
#    * x is the top-left x co-ordinate
#    * y is the top-left y co-ordinate
#    * im_window is the sliding window image
#    '''
#    w, h = ImageInfo.getsize(image)

#    # TODO finish coding this by calculating appropriate w and h
#    return slide_win_abs(image, (w, h), step_sz, discard_partial)


# DEBUG debug decorator used for pyramid
@decgetimg
def pyramid(image, scale=1.5, min_pyr_sz=(30, 30)):
    '''(ndarray|str, float, (int,int))->yield ndarray
    Yields suceesively downsampled images (ndarrays)
    until the minsize in either width or height is reached.
    '''
    #Note that
    # yield the original image
    yield image

    # keep looping over the pyramid
    while True:
        # compute the new dimensions of the image and resize it
        w = int(image.shape[1] / scale)
        image = resize(image, width=w)

        # if the resized image does not meet the supplied minimum
        # size, then stop constructing the pyramid
        if image.shape[0] < min_pyr_sz[1] or image.shape[1] < min_pyr_sz[0]:
            break

        # yield the next image in the pyramid
        yield image


@decgetimg
def pyrwin(image, scale=1.5, min_pyr_size=(100, 100), win_func=slide_win_abs, **win_func_args):
    '''(str|ndarray, float, (int,int), bool, function, function kwargs)->yield (int, int, ndarray)
    combines pyramid and a sliding window function (win_func) to yield window regions
    Yields:(x, y, window)

    min_pyr_size: stop when row or cols below respective pixel size
    discard_partial: discard windows below a size passed to the sliding window func win_func

    Supported windows functions:
    slide_win_abs(image, win_sz, step_sz)
    '''
    for resized in pyramid(image, scale=scale, min_pyr_sz=min_pyr_size):  # loop over the image pyramid
            # loop over the sliding window for each layer of the pyramid
        for x, y, window in win_func(resized, **win_func_args):
            yield (x, y, window)
