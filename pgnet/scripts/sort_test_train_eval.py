# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''randomly assign positive and negative images to
test and validation, move them out of the training folder
and create the csv files used to stuff the
tensorflow queue

Assumes all images start out in:
C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/all/bass
and
C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/all/not_bass'''

_ALL_POS = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/all/bass'
_ALL_NEG = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/all/not_bass'

_TRAIN_POS = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/train/bass'
_TRAIN_NEG = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/train/not_bass'

_EVAL_POS = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/eval/bass'
_EVAL_NEG = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/eval/not_bass'

_TEST_POS = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/test/bass'
_TEST_NEG = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/test/not_bass'

from shutil import copy2
import os.path as path
import random

import funclib.iolib as iolib
W = 514; H = 120
RATIO_TVT = (0.6, 0.2, 0.2) #order is train, validation, test
assert sum(RATIO_TVT) == 1, 'RATIO_TVT must add up to 1'




def chkexists(dirs):
    '''check output dirs exist'''
    for d in dirs:
        d = path.normpath(d)
        assert path.isdir(d), '\nDir %s not found.' % d

def chkempty(dirs):
    '''check output dirs are empty'''
    for d in dirs:
        assert not iolib.folder_has_files(path.normpath(d)), '\nDir %s must be empty.' % path.normpath(d)

def gen_csv_file(dirs, out_fname, is_test=False):
    '''(str|list, str) -> void
    Save csv file to out_fname, from the
    .jpg files in dirs.

    Use this after images have been assigned to test, train and
    eval folders.
    '''
    print('Creating csv file %s' % out_fname)

    all_ = []
    fcnt = iolib.file_count(dirs, '*.jpg', False)
    PP = iolib.PrintProgress(fcnt)
    for f in iolib.file_list_generator1(dirs, '*.jpg'):
        is_pos = 0 if 'not_bass' in f else 1
        if is_test:
            all_.append([path.normpath(f)]) #if it is test, we dont need the dimensions etc
        else:
            all_.append([path.normpath(f), is_pos, W, H])
        PP.increment()

    iolib.writecsv(path.normpath(out_fname), all_, inner_as_rows=False)
    print('\nCSV written to %s.' %  out_fname)


def assign():
    '''() -> void
    Assign images to be test, train or evaluation and
    move them to the respective folders.

    Split of files determined by RATIO_TVT
    '''
    print('\nAssigning and moving files to train, eval and test sets.')

    chkexists([_TRAIN_POS, _TRAIN_NEG, _EVAL_POS, _EVAL_NEG, _TEST_POS, _TEST_NEG, _ALL_NEG, _ALL_POS]) #assert dirs are dirs
    chkempty([_TRAIN_POS, _TRAIN_NEG, _EVAL_POS, _EVAL_NEG, _TEST_POS, _TEST_NEG]) #assert all empty

    fpos = [path.normpath(f) for f in iolib.file_list_generator1(_ALL_POS, '*.jpg')]
    fneg = [path.normpath(f) for f in iolib.file_list_generator1(_ALL_NEG, '*.jpg')]

    nr_fpos = [int(len(fpos)*x) for x in RATIO_TVT] #RATIO_TVT order is train, validation, test
    nr_fpos[0] = nr_fpos[0] + len(fpos) - sum(nr_fpos) #fix if rounding has meant we havent got all the elements

    nr_fneg = [int(len(fneg)*x) for x in RATIO_TVT]
    nr_fneg[0] = nr_fneg[0] + len(fneg) - sum(nr_fneg) #fix if rounding has meant we havent got all the elements


    random.shuffle(fpos)
    random.shuffle(fneg)
    PP = iolib.PrintProgress(len(fpos) + len(fneg))

    for i, f in enumerate(fpos):
        PP.increment()
        if i <= nr_fpos[0] - 1:
            copy2(f, _TRAIN_POS)
        elif nr_fpos[0] < i < nr_fpos[0] + nr_fpos[1] - 1:
            copy2(f, _EVAL_POS)
        else:
            copy2(f, _TEST_POS)

    for i, f in enumerate(fneg):
        PP.increment()
        if i <= nr_fneg[0] - 1:
            copy2(f, _TRAIN_NEG)
        elif nr_fneg[0] < i < nr_fneg[0] + nr_fneg[1] - 1:
            copy2(f, _EVAL_NEG)
        else:
            copy2(f, _TEST_NEG)



def main():
    '''main entry'''
    #assign()
    gen_csv_file([_TRAIN_POS, _TRAIN_NEG],
                 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/train.csv'
                 )

    gen_csv_file([_EVAL_POS, _EVAL_NEG],
                 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/eval.csv'
                 )

    gen_csv_file([_TEST_POS, _TEST_NEG],
                'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/test.csv',
                is_test=True
                )

if __name__ == "__main__":
    main()
