'''This project is for general gis functions'''

__all__ = ['conversion']


def totextfile(s, fname):
    '''to text'''
    with open(fname, "w") as text_file:
        text_file.write(s)
