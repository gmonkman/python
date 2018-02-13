# pylint: disable=C0103, too-few-public-methods, locally-disabled, consider-using-enumerate
# unused-variable
'''Decorators, base classes and misc functions
for manipulatin other base classes.

Stick list/tuple/dic functions in here.
'''
import collections as _collections
import sys as _sys
import operator
from copy import deepcopy as _deepcopy

import numpy as _np


#Decorators
class classproperty(property):
    '''class prop decorator'''
    def __get__(self, obj, objtype=None):
        return super(classproperty, self).__get__(objtype)
    def __set__(self, obj, value):
        super(classproperty, self).__set__(type(obj), value)
    def __delete__(self, obj):
        super(classproperty, self).__delete__(type(obj))


#########
#CLASSES#
#########

class switch(object):
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
        elif self.value in args:  # changed for v1.5, see below
            self.fall = True
            return True

        return False

# region dict

# region dict classes
class odict(_collections.OrderedDict):
    '''subclass OrderedDict to support item retreival by index'''
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


def dic_sort_by_val(d):
    '''(dict) -> list
    Sort a dictionary by the values,
    returning as a list

    d:
        dictionary

    returns:
        list of tuples

    Example:
        >>>dic_sort_by_val({1:1, 2:10, 3:22, 4:1.03})
        [(1, 1), (4, 1.03), (2, 10), (3, 22)]
    '''
    return sorted(d.items(), key=operator.itemgetter(1))


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
    return sorted(d.items(), key=operator.itemgetter(0))


# region lists
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
    Depth of a list or tuple
    '''
    if isinstance(l, list):
        d = lambda L: isinstance(L, list) and (max(map(depth, L)) + 1) if L else 1
    elif isinstance(l, tuple):
        d = lambda L: isinstance(L, tuple) and (max(map(depth, L)) + 1) if L else 1
    else:
        s = 'Depth takes a list or a tuple but got a %s' % (type(l))
        raise(ValueError(s))
    return d(l)


def list_not(lst, not_in_list):
    '''(list,list)->list
    return set of lst elements not in not_in_list

    **Removes duplicates'''
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
    returns windows, mac, linux
    '''
    s = _sys.platform.lower()
    if s == "linux" or s == "linux2":
        return 'linux'
    elif s == "darwin":
        return 'mac'
    elif s == "win32" or s == "windows":
        return 'windows'
# endregion


#region Other
def isIterable(i, strIsIter=False, numpyIsIter=False):
    '''(any, bool)->bool
    Tests to see if i looks like an iterable.

    To count strings a noniterable, strIsIter should be False
    '''
    if isinstance(i, str) and strIsIter is False:
        return False
    elif isinstance(i, _np.ndarray) and numpyIsIter is False:
        return False
    return isinstance(i, _collections.Iterable)


def item_from_iterable_by_type(iterable, match_type):
    '''(iterable,class type)->item
    given an iterable and a type, return the item
    which first matches type
    '''
    if isIterable(iterable):
        for i in iterable:
            if isinstance(iterable, match_type):
                return i
    else:
        return iterable if isinstance(iterable, match_type) else None


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
