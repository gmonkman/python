# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''helper functions for processing various mags'''


class SeaAngler():
    '''Routines specific to Sea Angler Magazine'''
    NAME = 'Sea Angler'

    def __init__(self):
        pass

    @staticmethod
    def get_issue(s):
        '''str -> str
        gets issue'''
        return s.split('_')[1:2][0]
