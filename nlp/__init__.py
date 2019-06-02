'''main init for nlp package'''

__all__ = ['baselib', 'clean', 'metrics', 're', 'spell' ]


def totextfile(s, fname):
    '''to text'''
    with open(fname, "w") as text_file:
        text_file.write(s)