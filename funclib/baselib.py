# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable
'''base classes and misc functions for manipulatin other base classes
Stick list/tuple/dic functions in here
'''

from sys import version_info
from sys import platform

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
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False

def dic_merge_two(x, y):
    '''Given two dicts, merge them into a new dict as a shallow copy.'''
    z = x.copy()
    z.update(y)
    return z

def list_append_unique(list_in, val):
    '''(list, type)->void
    Appends val to list_in if it isnt already in the list
    List is by ref
    '''
    if not val in list_in:
        list_in.append(val)


#region lists

def list_flatten(items, seqtypes=(list, tuple)):
    '''flatten a list'''
    for i, x in enumerate(items):
        while i < len(items) and isinstance(items[i], seqtypes):
            items[i:i+1] = items[i]
    return items
#endregion


#base python stuff
def isPython3():
    '''->bool
    '''
    return version_info.major == 3

def isPython2():
    '''->bool
    '''
    return version_info.major == 2

#also implemented in iolib
def get_platform():
    '''-> str
    returns windows, mac, linux
    '''
    s = platform.lower()
    if s == "linux" or s == "linux2":
        return 'linux'
    elif s == "darwin":
        return 'mac'
    elif s == "win32" or s == "windows":
        return 'windows'
