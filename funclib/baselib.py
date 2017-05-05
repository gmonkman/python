# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# unused-variable
'''base classes and misc functions for manipulatin other base classes
Stick list/tuple/dic functions in here
'''
import collections as _collections
import sys as _sys

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
        else:
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
        keys = [k for k in self.keys() if partial_key in k]
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
        keys = [k for k in self.keys() if partial_key in k]
        if keys:
            if len(keys) > 1:
                raise KeyError('Partial key matched more than 1 element')

            key = keys[0] if keys else None
            if key is None:
                return d
            else:
                return self.get(key)
        else:
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


# region lists
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


def list_append_unique(list_in, val):
    '''(list, type)->void
    Appends val to list_in if it isnt already in the list
    List is by ref
    '''
    if val not in list_in:
        list_in.append(val)


def list_flatten(items, seqtypes=(list, tuple)):
    '''flatten a list'''
    for i, dummy in enumerate(items):
        while i < len(items) and isinstance(items[i], seqtypes):
            items[i:i + 1] = items[i]
    return items
# endregion


# region base python stuff
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
