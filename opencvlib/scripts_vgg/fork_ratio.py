# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import
'''Estimate total length and fork length ratio from
vgg file where 3 points have been labelled.

The vgg file must be called fltl.json, and should contain
point regions labelled with an attribute named forkpts.

Results saved to a csv file fltl.csv

Example:
fork_ratio.py "C:/temp/fshpics"
'''
#First Point Added in VGG: Tip of the nose
#Second point added: Fork
#3rd point added: Tail tip
#Optional 4th point added: Other tail tip - use if the midpoint between the tail tips will give better ratio.

import argparse
import os.path as path
from shutil import copyfile

import opencvlib.imgpipes.vgg as vgg
from funclib.iolib import get_file_parts2
import funclib.iolib as iolib
from funclib.iolib import print_progress
from sympy.geometry import Point2D, Line2D
from opencvlib.view import draw_points
from opencvlib.view import show


VGGFILE = 'fltl.json'
CSVOUT = 'fltl.csv'


def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__)
    cmdline.add_argument('folder', help='Folder containing the images and vgg file fltl.json')
    args = cmdline.parse_args()

    vgg.SILENT = True
    folder = path.normpath(args.folder)
    assert iolib.folder_exists(folder), 'Folder %s not found' % folder
    vgg_file = path.normpath(path.join(folder, VGGFILE))
    out_file = path.normpath(path.join(folder, CSVOUT))

    Pts = [] #store all the points
    outdata = [['fname', 'pts_used', 'total_length_px', 'fork_length_px']]
    print('\nProcessing ...')

    for Img in vgg.imagesGenerator(json_file=vgg_file):
        Pts = [None, None, None, None]
        assert isinstance(Img, vgg.Image)
        for vggReg in Img.roi_generator(shape_type='point'):
            assert isinstance(vggReg, vgg.Region)
            lbl = int(vggReg.region_json_key) + 1 if vggReg.region_attr.get('forkpts', '') == '' else int(vggReg.region_attr['forkpts'])
            Pts[lbl - 1] = Point2D(vggReg.x, vggReg.y)

        if not Pts or None in Pts[0:3]:
            continue

        C = Pts[0]; B = Pts[1]; A = Pts[2]; D = Pts[3]
        #C: First Point Added in VGG: Tip of the nose, forkpts:1
        #B: Second point added: Fork. forkpts:2
        #A: 3rd point added: Tail tip. forkpts:3
        #D: Optional 4th point added: Other tail tip - use if the midpoint between. forkpts:4
        #the tail tips will give better ratio.

        fork_length_px = C.distance(B).evalf()
        if Pts[3] is None:
            pts_used = 3
            fork_to_tip_len = abs((A.distance(C).evalf()**2 - A.distance(B).evalf()**2 - B.distance(C).evalf()**2) / abs(2*B.distance(C).evalf()))
        elif len(Pts) == 4:
            pts_used = 4
            fork_to_tip_len = abs(B.distance(A.midpoint(D)).evalf())

        total_length_px = fork_to_tip_len + fork_length_px
        outdata.append([Img.filename, pts_used, total_length_px, fork_length_px])
        Pts = []

    iolib.writecsv(out_file, outdata, inner_as_rows=False)
    iolib.folder_open(path.normpath(folder))



if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
