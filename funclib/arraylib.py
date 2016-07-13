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
    '''
    assert isinstance(np, numpy.ndarray)

    #get a numpy flattened array of all values which are a number (ie exclude NaNs)
    mask = numpy.isfinite(np) #create a boolean mask
    assert isinstance(mask, numpy.ndarray)
    np_val_list = np.copy()
    np_val_list =  nptmp[mask]
    np_val_list = numpy.random.permutation(np_val_list)

    #now we need to reassign our original array for the permuted list where there are non NaNs
    #First get indexes of non NaN values in passed array
    npInds = numpy.nonzero(mask) #mask is still a array of booleans with True values corresponding to non NaNs and Infs
    assert len(npInds) == len(np_val_list)
    npInds = numpy.transpose(npInds)
    cnt = 0
    npout = np.copy()
    assert isinstance(npout, numpy.ndarray)
    for val in npInds:
        x,y = val
        npout[x][y] = np_val_list[cnt]

    return npout


def np_focal_mean(np, pad=True):
    '''(ndarray of 2 dimensions, bool) -> ndarray
    If pad is true, adds a NaN border all around the input array
    Calculates focal mean on elements of numpy array which are not NaN
    Radius is currently all adjacent cells
    '''
    assert isinstance(np, numpy.ndarray)
    
    nptmp = np.copy()
    nptmp = numpy.pad(nptmp, pad_width=1, mode='constant', constant_values=numpy.NaN) #surround with nans so we can ignore edge effects
    assert isinstance(nptmp, numpy.ndarray)

    kernel = numpy.ones((3,3))
    assert isinstance(kernel, numpy.ndarray)
    
    out = ndimage.filters.generic_filter(nptmp, numpy.nanmean, kernel, mode='constant') #create means by kernel
    
    return out
