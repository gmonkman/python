'''basic number related helper functions'''

def is_float(test):
    '''(any) -> bool
    Return true of false if s is a float
    '''
    try:
        float(test)
        return True
    except ValueError:
        return False
