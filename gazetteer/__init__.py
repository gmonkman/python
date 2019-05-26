'''main init for nlp package'''

__all__ = ['gazlib']


def totextfile(s, fname):
    '''to text'''
    with open(fname, "w") as text_file:
        text_file.write(s)
