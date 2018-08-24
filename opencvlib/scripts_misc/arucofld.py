# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import
'''Get the resolutions of images in a folder
and export them to a csv with code and filename

Example:
resolutions_to_csv.py "C:/temp/fshpics"
'''
#Source images in: "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/processors/undistorted"

import argparse
import os.path as path

from funclib.iolib import get_file_parts2
import funclib.iolib as iolib
from funclib.iolib import PrintProgress
from opencvlib import aruco
from opencvlib.imgpipes.generators import FromPaths
from opencvlib import view

CSVOUT = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/Fiducial_machine_vision_estimates/bad_markers.csv'
CSVPATH = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/Fiducial_machine_vision_estimates'


FLDS = ['C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/gopro_all_undistorted',
'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/s5690',
'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/fujifilm',
'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/gopro_all_undistorted',
'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/s5690',
'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/fujifilm']

FLDS = ['F:/_images/bass/fiducial_28Jan/charter/fujifilm',
'F:/_images/bass/fiducial_28Jan/charter/goprohero4',
'F:/_images/bass/fiducial_28Jan/charter/goprohero5',
'F:/_images/bass/fiducial_28Jan/charter/s5690',
'F:/_images/bass/fiducial_28Jan/shore/goprohero4',
'F:/_images/bass/fiducial_28Jan/shore/goprohero5',
'F:/_images/bass/fiducial_28Jan/shore/s5690',
'F:/_images/bass/fiducial_28Jan/shore/fujifilm']


def main():
    '''main'''

    FP = FromPaths(FLDS)
    tot = sum([1 for x in FP.generate(pathonly=True)])
    mcnt = 0
    bad = []
    PP = PrintProgress(tot, init_msg='/nProcessing...')
    for img, fname, _ in FP.generate():
        PP.increment()

        D = aruco.Detected(img)
        if D.Markers:
            mcnt += 1
        else:
            bad.append(fname)
    print('Success: %s    Fail: %s    Percent: %0.2f' % (mcnt, tot-mcnt, 100*(tot-mcnt)/tot))
    iolib.writecsv(CSVOUT, bad)
    iolib.folder_open(CSVPATH)



if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
