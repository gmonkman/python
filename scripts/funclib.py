# pylint: disable=C0103, too-few-public-methods, locally-disabled
'''My general library of misc functions'''
import numbers
import sys

def is_float(test):
    '''(any) -> bool
    Return true of false if s is a float
    '''
    try:
        float(test)
        return True
    except ValueError:
        return False

def read_number(test, default=0):
    '''(any,number) -> number
    Return test if test is a number, or default if s is not a number
    '''
    if isinstance(test, str):
        if is_float(test):
            return float(test)
        else:
            return default
    elif isinstance(test, numbers.Number):
        return test
    else:   #not a string or not a number
        return default

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

# Print iterations progress
def printProgress(iteration, total, prefix='', suffix='', decimals=2, barLength=50):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : number of decimals in percent complete (Int)
        barLength   - Optional  : character length of progbar (Int)
    """
    filledLength = int(round(barLength * iteration / float(total)))
    if iteration / float(total) > 1:
        total = iteration
    percents = round(100.00 * (iteration / float(total)), decimals)
    if barLength > 0:
        progbar = '#' * filledLength + '-' * (barLength - filledLength)
    else:
        progbar = ''

    sys.stdout.write('%s [%s] %s%s %s\r' % (prefix, progbar, percents, '%', suffix)), sys.stdout.flush()
    if iteration == total:
        print "\n"


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
