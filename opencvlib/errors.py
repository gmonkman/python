# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''error classes'''

class FeatureErr(Exception):
    '''custom errors'''
    def __init__(self, *args, **kwargs):
        super().__init__('My error', *args, **kwargs)
