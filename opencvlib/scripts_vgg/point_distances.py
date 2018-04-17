# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import
'''Estimate total distances between  paired points,
optionally calculate pixel length per mm.

Uses a vgg file with the region annotations of
fids and mm. i.e. the cols in vgg region attrs
are called fids and mm.

The vgg file must be called vgg_point_distances.json.

Results saved to a csv file called vgg_point_distances.csv

Example:
point_distances.py "C:/temp/fshpics"
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


VGGFILE = 'vgg_point_distances.json'
CSVOUT = 'vgg_point_distances.csv'


#Fix to read in dab laser distances

class DabSamples():
    '''some hard coded stuff to help write to excel sheet
    fish_image_data_sheet.xlsm!SQLsample_length
    '''
    sampleids = [51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87]
    unique_codes = ['RZA', 'V4Y', 'QVC', 'HIC', '9JC', 'MH6', 'F2U', 'B81', 'HSA', 'B5U', 'F1R', '6XT', 'BHQ', 'Q9A', '63A', 'MDG', 'I8V', '6EI', '5KS', 'DAD', 'TGH', 'JUM', '7A4', 'L2T', 'QNK', '6ZP', 'KW4', 'G4X', 'AUV', 'KIF', 'QK7', 'Q3Q', 'ZUV', 'K89', 'A6P', 'KZY', 'QLX']
    file_names = ['%s.jpg' for code in unique_code]
    ref_length_type_laser = 'laser lines'
    ref_length_type_bg = 'background checker'
    ref_length_type_fg = 'foreground checker'
    measured_resolution = '1280x768'


class Measure():
    def __init__(self, name='', pt1, pt2):
        self.name = name
        assert isinstance(self.pt1, Point2D)
        assert isinstance(self.pt2, Point2D)
        self.pt1 = pt1
        self.pt2 = pt2



def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__)
    cmdline.add_argument('folder', help='Folder containing the images and vgg file vgg_point_distances.json')
    args = cmdline.parse_args()

    vgg.SILENT = True
    folder = path.normpath(args.folder)
    assert iolib.folder_exists(folder), 'Folder %s not found' % folder
    vgg_file = path.normpath(path.join(folder, VGGFILE))
    out_file = path.normpath(path.join(folder, CSVOUT))

    Pts = [] #store all the points
    outdata = [['fname','pts_used', 'total_length_px', 'fork_length_px']]
    print('\nProcessing ...')

    for Img in vgg.imagesGenerator(json_file=vgg_file):
        Pts = [None, None, None, None]
        assert isinstance(Img, vgg.Image)
        for vggReg in Img.roi_generator(shape_type='point'):
            assert isinstance(vggReg, vgg.Region)
            lbl = int(vggReg.region_json_key) + 1 if vggReg.region_attr.get('forkpts', '') == '' else int(vggReg.region_attr['forkpts'])
            Pts[lbl - 1] =  Point2D(vggReg.x, vggReg.y)

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
            tail_tip_line = Line2D(C, D)
            fork_to_tip_len = abs(B.distance(A.midpoint(D)).evalf())

        total_length_px = fork_to_tip_len + fork_length_px
        outdata.append([Img.filename, pts_used,  total_length_px, fork_length_px])
        Pts = []

    iolib.writecsv(out_file, outdata, inner_as_rows=False)
    iolib.folder_open(path.normpath(folder))



if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
