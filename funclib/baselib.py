# pylint: disable=C0103, too-few-public-methods, locally-disabled

'''base classes and misc functions'''

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

def list_flatten(test_list):
    '''(list) -> list
    returns flattened list
    '''
    if isinstance(test_list, list):
        if len(test_list) == 0:
            return []
        first, rest = test_list[0], test_list[1:]
        return flatten(first) + flatten(rest)
    else:
        raise ValueError("Couldn't flatten object. Expected a list, but object not a list")