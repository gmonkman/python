# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''helper funcs for extraction of seaangler text'''
from warnings import warn as _warn
import funclib.iolib as _iolib

MAG_NAME = 'sea angler'

def get_issue_and_page(s):
    '''str -> str, int
    gets issue from full file path

    Parameter:
        s:path name

    Returns:
        issue number

    Example:
    >>>get_issue_and_page('C:/temp/SA_111_001.jpg')
    '''
    _, f, _ = _iolib.get_file_parts(s)
    ss = f.split('_')
    try:
        pg = int(ss[-1])
    except Exception as _:
        pg = -1
        _warn('Failed to retrieve issue and page for %s' % f)
    return ss[1], pg
