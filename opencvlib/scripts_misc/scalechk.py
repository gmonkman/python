# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import
'''This loops through images and outputs the scales
which would be produced for each image

This is a one off piece of work for the mv paper.
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
from opencvlib import transforms
from opencvlib import roi
from opencvlib import winpyr

CSVOUT = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/Fiducial_machine_vision_estimates/imgscales.csv'
CSVPATH = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/Fiducial_machine_vision_estimates'


FLDS = ['C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/gopro_all_undistorted/rotated',
'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/s5690/rotated',
'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/fujifilm/rotated',
'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/gopro_all_undistorted/rotated',
'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/s5690/rotated',
'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/fujifilm/rotated']


def getkey(fldname):
    '''get key'''
    plat = 'Afloat' if 'charter' in fldname else 'Shore'
    if 's5690' in fldname:
        cam = 's5690'
    elif 'fujifilm' in fldname:
        cam = 'XP30'
    elif 'gopro' in fldname:
        cam = 'GoPro'
    else:
        raise ValueError('Camera not found')
    return plat, cam



def main():
    '''main'''

    FP = FromPaths(FLDS)
    tot = sum([1 for x in FP.generate(pathonly=True)])


    PP = PrintProgress(tot, init_msg='/nProcessing...')
    pts = [[0, 0], [0, 0], [0, 0], [0, 0]]

    results = [['platform', 'camera', 'imgname', 'orig_x', 'orig_y', 'w', 'h', 'scale', 'status', 'marker_side_px']]

    #this will use images not in the data, but these will be filtered out on the join
    for img, fname, _ in FP.generate():
        PP.increment()
        orig_y, orig_x, _ = img.shape
        #detect when flipped:
        _, ffname, _ = get_file_parts2(fname)
        plat, cam = getkey(fname)
        for img_scaled, _, scale in winpyr.pyramid_pts(img, pts, 1.5, yield_original=True):
            status = ''
            scale_str = '%0.3f' % scale
           # xform = 'scale_%s' % scale_str
            h, w, _ = img_scaled.shape
            try:
                D = aruco.Detected(img_scaled)
                if D.Markers:
                    status = 'marker detected'
                    m = D.Markers[0]
                    assert isinstance(m, aruco.Marker)
                    px = m.side_px
                else:
                    status = 'marker not detected'
                    px = ''
            except Exception as dummy:
                status = 'Unexpected error'
            res = [plat, cam, ffname, orig_x, orig_y, w, h, scale_str, status, px]
            assert len(res) == len(results[0]), 'header col number doesnt match results col number'
            results.append(res)


    iolib.writecsv(CSVOUT, results, inner_as_rows=False)
    iolib.folder_open(CSVPATH)



if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
