#pylint: disable=C0302, too-many-branches, dangerous-default-value, line-too-long, no-member, expression-not-assigned, locally-disabled, not-context-manager, unused-import
'''routines to manipulate array like objects like lists, tuples etc'''
import numpy as np
import numpy.ma as ma
import numpy.random
import scipy.ndimage as ndimage
import xlwings

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


#region NUMPY
def np_permute_2d(a):
    '''(ndarray) -> ndarray
    Takes a numpy array and permutes the values ignoring NaNs
    i.e. the array can contain NaNs but a permuted value
    cannot be permuted into a cell of value NaN
    '''
    assert isinstance(a, np.ndarray)

    #get a numpy flattened array of all values which are a number (ie exclude NaNs)
    mask = np.isfinite(a) #create a boolean mask

    np_val_list = a.copy()
    np_val_list = np_val_list[mask]
    np_val_list = np.random.permutation(np_val_list)

    #now we need to reassign our original array for the permuted list where there are non NaNs
    #First get indexes of non NaN values in passed array
    npInds = np.nonzero(mask) #mask is still a array of booleans with True values corresponding to non NaNs and Infs
    npInds = np.transpose(npInds)
    cnt = 0
    npout = a.copy()
    assert isinstance(npout, np.ndarray)
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
    if np.isnan(arg[4]):
        return np.NaN
    else:
        return np.nanmean(arg)


def np_focal_mean(a, pad=True):
    '''(ndarray of 2 dimensions, bool) -> ndarray
    If pad is true, adds a NaN border all around the input array
    Calculates focal mean on elements of numpy array which are not NaN
    Radius is currently all adjacent cells

    May get unexpected results if ndarray is not of type float
    '''
    assert isinstance(a, np.ndarray)
    x = a.astype(float)
    
    if pad:
        #surround with nans so we can ignore edge effects
        x = np.pad(x, pad_width=1, mode='constant', constant_values=np.NaN)

    kernel = np.ones((3, 3))
    
    #create means by kernel
    out = ndimage.filters.generic_filter(x, _focal_mean_filter, footprint=kernel, mode='constant', cval=np.NaN)

    return out


def np_paired_zeros_to_nan(a, b):
    '''(ndarray, ndarray) -> dictionary
    returns  'a':a, 'b':b
    replaces matched zero value pairs with nans, retaining
    the shape of the array
    '''
    assert isinstance(a, np.ndarray)
    assert isinstance(b, np.ndarray)
    if a.dtype != 'float':
        raise ValueError('ndarray a is not of dtype float')
    if b.dtype != 'float':
        raise ValueError('ndarray b is not of dtype float')

    if a.shape != b.shape:
        raise ValueError('Arrays must be the same shape')
    nponebool = np.array(a, dtype=bool)
    nptwobool = np.array(b, dtype=bool)

    #mask now has False where both 'in' arrays have matching zeros
    #we the invert so matched zero positions are set to True
    #checked and nan is converted to True during above casting
    mask = np.invert(np.logical_or(nponebool, nptwobool))
    
    #npInds now contains indexes of all 'cells' which had zeros 
    npInds = np.nonzero(mask)
    assert isinstance(npInds, tuple)
    
    npInds = np.transpose(npInds)
    
    for val in npInds:
        x, y = val
        a[x][y] = np.NaN
        b[x][y] = np.NaN
    
    return {'a':a, 'b':b}


def np_pad_nan(a):
    '''(ndarray) -> ndarray
    pads nd with nans'''
    if a.dtype != 'float':
        raise ValueError('ndarray is not of dtype float')
    return np.pad(a, pad_width=1, mode='constant', constant_values=np.NaN)


def np_delete_paired_nans_flattened(a, b):
    '''(ndarray, ndarray) -> ndarray
    Array types are float
    This must first flatten both arrays and both outputs
    are FLATTENED (but retain matches at a given index)
    {'a':a, 'b':b}
    '''
    assert isinstance(a, np.ndarray)
    assert isinstance(b, np.ndarray)
    if a.shape != b.shape:
        raise ValueError('arrays are of different shape')

    a = a.flatten()
    b = b.flatten()

    #set mask values to false where there are nans
    #then use mask for both a and b to filter out all matching
    #nans
    a = a.astype(float)
    b = b.astype(float)

    amask = np.invert(np.isnan(a))
    bmask = np.invert(np.isnan(b))
    mask = np.logical_or(amask, bmask)
    a = a[mask]
    b = b[mask]

    return {'a':a, 'b':b}


def np_unmatched_nans_to_zero(a, b):
    '''(ndarray, ndarray) -> dict
    Where there are unmatched nans by position in ndarrays
    a and b, zero will be substituted.
    a and b will be converted to dtype=float
    returns {'a':a,'b':b}
    '''
    assert isinstance(a, np.ndarray)
    assert isinstance(b, np.ndarray)
    if a.shape != b.shape:
        raise ValueError('Arrays must be same shape')
    
    a = a.astype(float)
    b = b.astype(float)
    mask = np_unmatched_nans(a, b)

    #this gets the indexes of cells with unmatched nans
    inds = np.nonzero(mask)   
    #inds looks like [(11,1),(5,4) ...] 
    inds = zip(inds[0], inds[1])
    for ind in inds:
        if np.isnan(a[ind[0]][ind[1]]):
            a[ind[0]][ind[1]] = 0
        else:
            b[ind[0]][ind[1]] = 0

    return {'a':a, 'b':b}


def np_unmatched_nans(a, b):
    '''(ndarray, ndarray) -> ndarray
    Creates a new array where nans do not match position in each array
     
    nan<->nan = False
    nan<->1.2 = True
    1.2<->1.2 = False

    Arrays must be of the dimensions

    Returned ndarray has True where nans are unmatched
    '''
    assert isinstance(a, np.ndarray)
    assert isinstance(b, np.ndarray)
    if a.shape != b.shape:
        raise ValueError('Arrays must be same shape')

    a = a.astype(float)
    b = b.astype(float)

    amask = np.isnan(a)
    bmask = np.isnan(b)
    mask = np.logical_xor(amask, bmask)
    return mask


def np_delete_paired_zeros_flattened(a, b):
    '''(ndarray, ndarray) -> dictionary
    'dic is 'a':aOut, 'b':bOut
    This must first flatten both arrays and both outputs
    are flattened (but retain matches at a given index
    '''
    assert isinstance(a, np.ndarray)
    assert isinstance(b, np.ndarray)
    a = a.flatten()
    b = b.flatten()

    #set mask values to false where there are zeros
    #then use mask for both a and b to filter out all matching
    #zeros
    amask = np.invert(a == 0)
    bmask = np.invert(b == 0)
    mask = np.logical_or(amask, bmask)
    return {'a':a[mask], 'b':b[mask]}


def np_delete_zeros(a):
    '''(arraylike) -> ndarray
    delete zeros from an array.
    **Note that this will reshape the array**
    '''
    aa = np.array(a).astype(float)
    np.place(aa, aa == 0, np.nan)
    return np_delete_nans(aa)


def np_delete_nans(a):
    '''(arraylike) -> ndarray

    Takes an array like and removes all nans.

    **Note that this will change the location of values in the array**
    '''
    nd = np.array(a).astype(float)
    return nd[np.invert(np.isnan(nd))]


def np_contains_nan(nd):
    '''(ndarray) -> bool
    Global check if array contains np.nan anywhere
    '''
    return np.isnan(np.sum(nd))


def np_pickled_in_excel(pickle_name):
    '''(str, bool) -> void
    opens the pickled nd array as a new excel spreadsheet

    If silent_save is true, then the file is saved as an excel file
    to the same directory (and name) as the pickled nd array

    Currently assumes a 1D or 2D array. Unknown behaviour with >2 axis.
    '''
    arr = np.load(pickle_name)
    xlwings.view(arr)


def np_frequencies(a):
    '''(ndarray)->ndarray
    return array with frequency values of items in array
    a = [1,2,3,3,4,4,4]
    np_frequencies(a) returns
    [[1 1],
    [2,1],
    [3,2],
    [4,3]]
    '''
    unq, cnt = np.unique(a, return_counts=True)
    return np.asarray((unq, cnt)).T

#endregion
    