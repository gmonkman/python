# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# no-self-use, unused-argument
'''edge detection and skeletonization
'''


def get_perspective_correction(bg_dist, object_depth, length):
    '''(float, float)->float|None
    Return the length corrected for the depth of the object
    considering the backplane of the object to be the best
    representative of the length
    *NOTE* The length of the object has been accurately measured
    '''
    if bg_dist is None or object_depth is None or length is None:
        return None
    elif bg_dist == 0 or 1 - (object_depth / bg_dist) == 0:
        return None
    else:
        return length / (1 - (object_depth / bg_dist))


def get_perspective_correction_iter_linear(coeff,
                                           const,
                                           bg_dist,
                                           length,
                                           last_length=0,
                                           stop_below_proportion=0.01):
    '''(float, float, float, float,float)->float|None
    Return the length corrected for the depth of the object
    considering the backplane of the object to be the best
    representative of the length.
    *NOTE* The length of the object was itself estimated from the foreground standard measure

    Coeff and constant are used to calculate an objects depth from its length
    The object depth is used to create a iterative series sum which add to the length
    to return the sum of lengths once the last length added was less then stop_below

    stop_below_proportion is the stopping criteria, once the last
    calculated length to add is is less than last_length*stop_below_proportion
    we return the result and stop the iteration
    '''
    if last_length == 0:
        object_depth = length * coeff + const
    else:
        object_depth = last_length * coeff + const

    if object_depth == 0:
        return length
    elif length == 0:
        return 0
    elif (last_length / length < stop_below_proportion) and last_length > 0:
        return length

    if last_length == 0:  # first call
        l = get_perspective_correction(bg_dist, object_depth, length) - length
    else:
        l = get_perspective_correction(
            bg_dist, object_depth, last_length) - last_length

    if l is None:
        return None

    return get_perspective_correction_iter_linear(coeff, const, bg_dist, length + l, l, stop_below_proportion)
