'''routines to manipulate array like objects like lists, tuples etc'''
import numpy
import numpy.ma
import numpy.random
import scipy.ndimage as ndimage


#list stuff
def list_delete_value_pairs(list_a, list_b, match_value=0):
    '''(list,list,str|number) -> void
    Given two lists, removes matching values pairs occuring
    at same index location.

    Used primarily to remove matched zeros prior to
    correlation analysis.
    '''
    assert isinstance(list_a, list), 'list_a was not a list'
    assert isinstance(list_b, list), 'list_b was not a list'
    for ind, value in reversed(list(enumerate(list_a))):
        if value == match_value and list_b[ind] == match_value:
            del list_a[ind]
            del list_b[ind]




#NUMPY ROUTINES
def np_permute_2d(np):
    '''(ndarray) -> ndarray
    Takes a numpy array and permutes the values ignoring NaNs
    i.e. the array can contain NaNs but a permuted value
    cannot be permuted into a cell of value NaN
    '''
    assert isinstance(np, numpy.ndarray)

    #get a numpy flattened array of all values which are a number (ie exclude NaNs)
    mask = numpy.isfinite(np) #create a boolean mask
    assert isinstance(mask, numpy.ndarray)
    np_val_list = np.copy()
    assert isinstance(np_val_list, numpy.ndarray)
    np_val_list = np_val_list[mask]
    np_val_list = numpy.random.permutation(np_val_list)

    #now we need to reassign our original array for the permuted list where there are non NaNs
    #First get indexes of non NaN values in passed array
    npInds = numpy.nonzero(mask) #mask is still a array of booleans with True values corresponding to non NaNs and Infs
    npInds = numpy.transpose(npInds)
    cnt = 0
    npout = np.copy()
    assert isinstance(npout, numpy.ndarray)
    for val in npInds:
        npout[val[0]][val[1]] = np_val_list[cnt]
        cnt += 1

    return npout




def _focal_mean_filter(arg):
    '''(array) -> scalar(float)
    Function used by np_focal_mean by the ndimage.filters.generic_filter
    to calculate per element focal values.
    In particular we want to return NaN when the original element is NaN
    '''
    if numpy.isnan(arg[4]):
        return numpy.NaN
    else:
        return numpy.nanmean(arg)



def np_focal_mean(np, pad=True):
    '''(ndarray of 2 dimensions, bool) -> ndarray
    If pad is true, adds a NaN border all around the input array
    Calculates focal mean on elements of numpy array which are not NaN
    Radius is currently all adjacent cells
    '''
    assert isinstance(np, numpy.ndarray)
    if np.dtype != 'float':
        raise ValueError('ndarray is not of dtype float')
    
    if pad:
        #surround with nans so we can ignore edge effects
        np = numpy.pad(np, pad_width=1, mode='constant', constant_values=numpy.NaN)

    assert isinstance(np, numpy.ndarray)

    kernel = numpy.ones((3, 3))
    assert isinstance(kernel, numpy.ndarray)
    
    #create means by kernel
    out = ndimage.filters.generic_filter(np, _focal_mean_filter, footprint=kernel, mode='constant', cval=numpy.NaN)

    return out




def np_paired_zeros_to_nan(a, b):
    '''(ndarray, ndarray) -> dictionary
    returns  'a':a, 'b':b
    replaces matched zero value pairs with nans, retaining
    the shape of the array
    '''
    assert isinstance(a, numpy.ndarray)
    assert isinstance(b, numpy.ndarray)
    if a.dtype != 'float':
        raise ValueError('ndarray a is not of dtype float')
    if b.dtype != 'float':
        raise ValueError('ndarray b is not of dtype float')

    if a.shape != b.shape:
        raise ValueError('Arrays must be the same shape')
    nponebool = numpy.array(a, dtype=bool)
    nptwobool = numpy.array(b, dtype=bool)

    #mask now has False where both 'in' arrays have matching zeros
    mask = numpy.logical_or(nponebool, nptwobool)
    
    #npInds now contains indexes of all 'cells' which had zeros 
    npInds = (mask is False).nonzero()
    assert isinstance(npInds, numpy.ndarray)
    
    npInds = numpy.transpose(npInds)
    
    for val in npInds:
        x, y = val
        a[x][y] = numpy.NaN
        b[x][y] = numpy.NaN
    
    return {'a':a, 'b':b}



def np_pad_nan(nd):
    '''(ndarray) -> ndarray
    pads nd with nans'''
    if nd.dtype != 'float':
        raise ValueError('ndarray is not of dtype float')
    return numpy.pad(nd, pad_width=1, mode='constant', constant_values=numpy.NaN)




def np_delete_paired_nans_flattened(a, b):
    '''(ndarray, ndarray) -> dictionary
    'dic is 'a':aOut, 'b':bOut
    This must first flatten both arrays and both outputs
    are flattened (but retain matches at a given index
    '''
    assert isinstance(a, numpy.ndarray)
    assert isinstance(b, numpy.ndarray)
    a = a.flatten()
    b = b.flatten()

    #set mask values to false where there are nans
    #then use mask for both a and b to filter out all matching
    #nans
    amask = numpy.invert(numpy.isnan(a))
    bmask = numpy.invert(numpy.isnan(b))
    mask = numpy.logical_or(amask, bmask)
    return {'a':a[mask], 'b':b[mask]}
    
def np_delete_paired_zeros_flattened(a, b):
    '''(ndarray, ndarray) -> dictionary
    'dic is 'a':aOut, 'b':bOut
    This must first flatten both arrays and both outputs
    are flattened (but retain matches at a given index
    '''
    assert isinstance(a, numpy.ndarray)
    assert isinstance(b, numpy.ndarray)
    a = a.flatten()
    b = b.flatten()

    #set mask values to false where there are zeros
    #then use mask for both a and b to filter out all matching
    #zeros
    amask = numpy.invert(a == 0)
    bmask = numpy.invert(b == 0)
    mask = numpy.logical_or(amask, bmask)
    return {'a':a[mask], 'b':b[mask]}

def np_contains_nan(nd):
    return numpy.isnan(numpy.sum(nd))

