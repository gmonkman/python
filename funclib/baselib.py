# pylint: disable=C0103, too-few-public-methods, locally-disabled, consider-using-enumerate, stop-iteration-return, simplifiable-if-statement, stop-iteration-return, too-many-return-statements
# unused-variable
'''Decorators, base classes and misc functions
for manipulatin other base classes.

Stick list/tuple/dic functions in here.
'''
import itertools as _itertools
import pickle as _pickle
import collections as _collections
import sys as _sys
import operator as _operator
from copy import deepcopy as _deepcopy
from enum import Enum as _enum
import ast as _ast

import numpy as _np
import funclib.iolib as _iolib


class eDictMatch(_enum):
    '''do dictionaries match
    '''
    Exact = 0 #every element matches in both
    Subset = 1 #one dic is a subset of the other
    Superset = 2 #dic is a superset of the other
    Intersects = 3 #some elements match
    Disjoint = 4 #No match


#Decorators
class classproperty(property):
    '''class prop decorator, used
    to enable class level properties'''
    def __get__(self, obj, objtype=None):
        return super(classproperty, self).__get__(objtype)
    def __set__(self, obj, value):
        super(classproperty, self).__set__(type(obj), value)
    def __delete__(self, obj):
        super(classproperty, self).__delete__(type(obj))


#########
#CLASSES#
#########

class _switch():
    '''From http://code.activestate.com/recipes/410692/. Replicates the C switch statement
    e.g.
    v = 'ten'
    for case in switch(v):
        if case('one'):
            print 1
            break
        if case('two'):
            print 2
            break
        if case('ten'):
            print 10
            break
        if case('eleven'):
            print 11
            break
        if case(): # default, could also just omit condition or 'if True'
            print "something else!"
            # No need to break here, it'll stop anyway
    '''

    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        '''Return the match method once, then stop'''
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True

        if self.value in args:  # changed for v1.5, see below
            self.fall = True
            return True

        return False

# region dict

# region dict classes
class odict(_collections.OrderedDict):
    '''subclass OrderedDict to support item retreival by index
    d = _baselib.odict()
    d[1] = '12'
    '''
    def getbyindex(self, ind):
        '''(int)->tuple
        Retrieve dictionary key-value pair as a tuple using
        the integer index
        '''
        items = list(self.items())
        return items[ind]


class dictp(dict):
    '''allow values to be accessed with partial key match
    dic = {'abc':1}
    d = dictp(dic)
    print(d['a']) # returns 1
    '''

    def __getitem__(self, partial_key):
        keys = [k for k in self.keys() if partial_key in k and k.startswith(partial_key)]
        if keys:
            if len(keys) > 1:
                raise KeyError('Partial key matched more than 1 element')

            key = keys[0] if keys else None
        return self.get(key)

    def getp(self, partial_key, d=None):
        '''(str, any)->dict item
        Support partial key matches,
        return d if key not found
        '''
        keys = [k for k in self.keys() if partial_key in k and k.startswith(partial_key)]
        if keys:
            if len(keys) > 1:
                raise KeyError('Partial key matched more than 1 element')
            key = keys[0] if keys else None
            if key is None:
                return d
            return self.get(key)

        return d


class DictList(dict):
    '''support having a key with a list of values,
    effectively emulating a ditionary with non-unique keys
    >>> d = dictlist.Dictlist()
    >>> d['test'] = 1
    >>> d['test'] = 2
    >>> d['test'] = 3
    >>> d
    {'test': [1, 2, 3]}
    >>> d['other'] = 100
    >>> d
    {'test': [1, 2, 3], 'other': [100]}
    '''

    def __setitem__(self, key, value):
        try:
            self[key]
        except KeyError:
            super(DictList, self).__setitem__(key, [])
        self[key].append(value)
# endregion


def dic_merge_two(x, y):
    '''Given two dicts, merge them into a new dict as a shallow copy.'''
    z = x.copy()
    z.update(y)
    return z
# endregion


def dic_key_with_max_val(d):
    '''(dict)->value
    Get key with largest value

    Example:
    >>>dic_key_with_max_val({'a':12, 'b':100, 'x':-1})
    'b'
    '''
    return max(d, key=lambda key: d[key])


def dic_sort_by_val(d):
    '''(dict, bool) -> list
    Sort a dictionary by the values,
    returning as a list

    d: dictionary
    as_dict: return as dictionary rather than list

    returns:
        list of tuples

    Example:
        >>>dic_sort_by_val({1:1, 2:10, 3:22, 4:1.03})
        [(1, 1), (4, 1.03), (2, 10), (3, 22)]
    '''
    l = sorted(d.items(), key=_operator.itemgetter(1))
    return l    
    


def dic_sort_by_key(d):
    '''(dict) -> list
    Sort a dictionary by the values,
    returning as a list of tuples

    d:
        dictionary

    returns:
        lit of tuples

    Example:
    >>>dic_sort_by_key({1:1, 4:10, 3:22, 2:1.03})
    [(1,1), (2,1.03), (3,22), (4,10)]
    '''
    out = sorted(d.items(), key=_operator.itemgetter(0))
    return out


def dic_match(a, b):
    '''(dict, dict) -> Enum:eDictMatch
    Compares dictionary a to dictionary b.

    a:
        Dictionary, compared to b
    b:
        Dictionary, which a is compared to
    Returns:
        Value from the enum, baselib.eDictMatch

    Example:
        >>>dic_match({'a':1}, {'a':1, 'b':2})
        eDictMatch.Subset

        >>>dic_match({'a':1, 'b':2}}, {'a':1, 'b':2})
        eDictMatch.Exact
    '''
    if not isinstance(a, dict) or not isinstance(a, dict):
        return None

    unmatched = False
    matched = False
    b_lst = list(b.items())
    a_lst = list(a.items())

    if len(a_lst) < len(b_lst):
        for i in a_lst:
            if i in b_lst:
                matched = True
            else:
                unmatched = True

        if matched and unmatched:
            return eDictMatch.Intersects

        if not matched:
            return eDictMatch.Disjoint

        if not unmatched:
            return eDictMatch.Subset
        return None

    if len(a_lst) > len(b_lst):
        for i in b_lst:
            if i in a_lst:
                matched = True
            else:
                unmatched = True

        if matched and unmatched:
            return eDictMatch.Intersects

        if not matched:
            return eDictMatch.Disjoint

        if not unmatched:
            return eDictMatch.Superset
        return None
    #same length
    for i in b_lst:
        if i in a_lst:
            matched = True
        else:
            unmatched = True

    if matched and unmatched:
        return eDictMatch.Intersects

    if not matched:
        return eDictMatch.Disjoint

    if not unmatched:
        return eDictMatch.Exact
    return None


# region lists
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


def list_index(list_, val):
    '''(list, <anything>) -> int|None
    Safely returns the list index which
    matches val, else None

    Parameters:
        list_: a list
        val: the value to find in list

    Returns:
        None if the item not found, else the index of the item in list

    Example:
    >>>list_index([1,2,3], 2)
    1
    >>>list_index([1,2,3], 5)
    None
    '''
    return list_.index(x) if x in list_ else None


def list_get_dups(l, thresh=3):
    '''(list, int) -> dict

    Get a dictionary containing dups in list where
    the key is the duplicate value, and the value is the
    duplicate nr.

    Example:
    >>>list_get_dups(1,1,2,3,4,4,4)
    {4:3}
    '''
    my_dict = {i:l.count(i) for i in l}
    out = dict(my_dict)
    for k, v in my_dict.items():
        if v < thresh:
            del(out[k])
    return out




def list_add_elementwise(lsts):
    '''lists->list
    Add lists elementwise.

    lsts:
        a list of lists with the same nr of elements

    Returns:
        list with summed elements

    Example:
    >>>list_add_elementwise([[1, 2], [1, 2]])
    [2, 4]
    '''
    return list(map(sum, zip(*lsts)))


def list_most_common(L, force_to_string=False):
    '''(list, bool)->str|int|float
    Find most common value in list

    force_to_string:
        make everything a string, use if list
        has mixed types
    '''
    if force_to_string:
        Ll = [str(s) for s in L]
    else:
        Ll = L.copy()

    SL = sorted((x, i) for i, x in enumerate(Ll))
    groups = _itertools.groupby(SL, key=_operator.itemgetter(0))
    def _auxfun(g):
        _, iterable = g
        count = 0
        min_index = len(Ll)
        for _, where in iterable:
            count += 1
            min_index = min(min_index, where)
        return count, -min_index
    return max(groups, key=_auxfun)[0]


def lists_remove_empty_pairs(list1, list2):
    '''(list|tuple, list|tuple) -> list, list, list
       Zip through datasets (pairwise),
       make sure both are non-empty; erase if empty.

       Returns:
        list1: non-empty corresponding pairs in list1
        list2: non-empty corresponding pairs in list2
        list3: list of original indices prior to erasing of empty pairs
    '''
    xs, ys, posns = [], [], []
    for i in range(len(list1)):
        if list1[i] and list2[i]:
            xs.append(list1[i])
            ys.append(list2[i])
            posns.append(i)
    return xs, ys, posns


def depth(l):
    '''(List|Tuple) -> int
    Depth of a list or tuple.

    Returns 0 of l is and empty list or
    tuple.
    '''
    if isinstance(l, (list, tuple)):
        if l:
            d = lambda L: isinstance(L, (list, tuple)) and max(map(d, L)) + 1
        else:
            return 0
    else:
        s = 'Depth takes a list or a tuple but got a %s' % (type(l))
        raise ValueError(s)
    return d(l)



def list_from_str(s):
    '''(str) -> list
    Concert a string representation of a list
    to a list

    Example:
    >>>list_from_str('[1,2,3]')
    [1,2,3]
    '''
    return _ast.literal_eval(s)


def list_not(lst, not_in_list):
    '''(list,list)->list
    return set of lst elements not in not_in_list
    123456
        5678
    >>>1234
    **Removes duplicates
    Example:
    >>>list_not([1,2,3,4,5,6], [5,6,7,8])
    [1,2,3,4]
    '''
    return list(set(lst) - set(not_in_list))


def list_and(lst1, lst2):
    '''(list,list)->list
    Return list elements in both lists

    **Removes duplicates'''
    return set(lst1) & set(lst2)


def list_or(lst1, lst2):
    '''(list,list)->list
    return all list elements (union)

    **Removes duplicates'''
    return set(lst1) | set(lst2)


def list_symmetric_diff(lst1, lst2):
    '''(list,list)->list
    Return all list elements not common
    to both sets

    **Removes duplicates'''
    return set(lst1) ^ set(lst2)


def list_max_ind(lst):
    '''(list) -> index
    Get list items with max
    value from a list
    '''
    return lst.index(max(lst))


def list_min_ind(lst):
    '''(list) -> index
    Get list items with max
    value from a list
    '''
    return lst.index(min(lst))


def list_append_unique(list_in, val):
    '''(list, type)->void
    Appends val to list_in if it isnt already in the list
    List is by ref
    '''
    if val not in list_in:
        list_in.append(val)

def list_get_unique(list_in):
    '''(list) -> list
    Returns a new list with
    duplicates removed and
    maintains order

    If order is not important sets can be used
    #https://stackoverflow.com/questions/7961363/removing-duplicates-in-lists
    '''
    out = []
    for x in list_in:
        list_append_unique(out, x)
    return out


def list_flatten(items, seqtypes=(list, tuple)):
    '''flatten a list

    **beware, this is also by ref**
    '''
    citems = _deepcopy(items)
    for i, dummy in enumerate(citems):
        while i < len(citems) and isinstance(citems[i], seqtypes):
            citems[i:i + 1] = citems[i]
    return citems
# endregion



# region tuples
def tuple_add_elementwise(tups):
    '''lists->list
    Add tuples elementwise.

    lsts:
        a tuple of tuples with the same nr of elements

    Returns:
        tuple with summed elements

    Example:
    >>>tuple_add_elementwise(((1, 2), (1, 2)))
    (2, 4)
    '''
    return tuple(map(sum, zip(*tups)))
# endregion




# region Python Info Stuff
def isPython3():
    '''->bool
    '''
    return _sys.version_info.major == 3


def isPython2():
    '''->bool
    '''
    return _sys.version_info.major == 2
# also implemented in iolib


def get_platform():
    '''-> str
    returns windows, mac, linux or unknown
    '''
    s = _sys.platform.lower()
    if s in ("linux", "linux2"):
        return 'linux'
    if s == "darwin":
        return 'mac'
    if s in ("win32", "windows"):
        return 'windows'
    return 'unknown'

# endregion


#region Other
def isIterable(i, strIsIter=False, numpyIsIter=False):
    '''(any, bool)->bool
    Tests to see if i looks like an iterable.

    To count strings a noniterable, strIsIter should be False
    '''
    if isinstance(i, str) and strIsIter is False:
        return False

    if isinstance(i, _np.ndarray) and numpyIsIter is False:
        return False
    out = isinstance(i, _collections.Iterable)
    return out


def item_from_iterable_by_type(iterable, match_type):
    '''(iterable,class type)->item|None
    given an iterable and a type, return the item
    which first matches type
    '''
    if isIterable(iterable):
        for i in iterable:
            if isinstance(iterable, match_type):
                return i
            return None
    out = iterable if isinstance(iterable, match_type) else None
    return out


def isempty(x):
    '''(something)->bool
    Check of a variable looks empty
    '''
    try:
        if isinstance(x, _np.ndarray):
            return x.size == 0
        if x is None: return True
        if x == '': return True
        if not x: return True
    except Exception:
        assert False #how did we get here?
        return True

    return False
#endreion


def pickle(obj, fname):
    '''(Any, str)->void
    Save object to fname

    Also see unpickle
    '''
    d, _, _ = _iolib.get_file_parts2(fname)
    _iolib.create_folder(d)
    with open(fname, 'wb') as f:
        _pickle.dump(obj, f)


def unpickle(fname):
    '''(str)->obj

    fname: path to pickled object
    unpickle'''
    with open(fname, 'rb') as f:
        obj = _pickle.load(f)
    return obj

def is_int(s):
    '''is int'''
    try:
        n = int(s)
        f = float(s)
        return n == f
    except:
        return False



    

if __name__ == "__main__":
    out = list_get_dups([1,1,2,3,4,4,4], 3)
    x = 1
    