# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import
'''Estimate total distances between  paired points,
optionally calculate pixel length per mm.

Uses a vgg file with the region annotations of
fids and mm. i.e. the cols in vgg region attrs
are called fids and mm.

The vgg file must be called vgg_point_distances.json.

Results saved to a csv file called vgg_point_distances.csv.

Example:
point_distances.py "C:/temp/fshpics"
'''
#Outputs of this data was manipulated in
#C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\dab\sos\fiducal_length\vgg_point_distances_all.xlsx
#prior to merging into the main data spreadsheet

#First Point Added in VGG: Tip of the nose
#Second point added: Fork
#3rd point added: Tail tip
#Optional 4th point added: Other tail tip - use if the midpoint between the tail tips will give better ratio.

import argparse
import os.path as path
from shutil import copyfile

import opencvlib.imgpipes.vgg as vgg
from funclib.iolib import get_file_parts2
from funclib.iolib import get_file_parts
import funclib.iolib as iolib
from funclib.iolib import PrintProgress
from sympy.geometry import Point2D, Line2D
from opencvlib.view import draw_points
from opencvlib.view import show
import statistics

VGGFILE = 'vgg_point_distances.json'
CSVOUT = 'vgg_point_distances.csv'

MEASURE_TYPES = ['bg', 'laser', 'fg', 'obj']
MEASURE_TYPES.extend([str(x) for x in range(1, 21)])

#Fix to read in dab laser distances

class DabSamples():
    '''some hard coded stuff to help write to excel sheet
    fish_image_data_sheet.xlsm!SQLsample_length
    '''
    #indexes match for these two
    sampleids = [51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87]
    unique_codes = ['RZA', 'V4Y', 'QVC', 'HIC', '9JC', 'MH6', 'F2U', 'B81', 'HSA', 'B5U', 'F1R', '6XT', 'BHQ', 'Q9A', '63A', 'MDG', 'I8V', '6EI', '5KS', 'DAD', 'TGH', 'JUM', '7A4', 'L2T', 'QNK', '6ZP', 'KW4', 'G4X', 'AUV', 'KIF', 'QK7', 'Q3Q', 'ZUV', 'K89', 'A6P', 'KZY', 'QLX']

    file_names = ['%s.jpg' for code in unique_codes]
    ref_length_type_laser = 'laser lines'
    ref_length_type_bg = 'background checker'
    ref_length_type_fg = 'foreground checker'
    measured_resolution = '1280x768'


class Measure():
    '''A measure for two corresponding points

    Properties:
        pixel_length: length between two points in pixels
        length_per_pixel: Length of a pixel in real units
    '''
    def __init__(self, name='', pt1=None, pt2=None, real_length=None):
        self.name = name
        self.pt1 = pt1
        self.pt2 = pt2
        self.real_length = real_length

    def __repr__(self):
        return 'Measure "%s" [%s,%s] mm=%s' % (
                            self.name,
                            str(tuple(self.pt1) if isinstance(self.pt1, Point2D) else ''),
                            str(tuple(self.pt2) if isinstance(self.pt2, Point2D) else ''),
                            str(self.real_length)
                        )


    @property
    def pixel_length(self):
        '''length in pixels'''
        if self.pt1 is None or self.pt2 is None:
            return None
        return abs(self.pt1.distance(self.pt2).evalf())

    @property
    def length_per_pixel(self):
        '''Length of a pixel in real units'''
        if None in  (self.pt1, self.pt2, self.real_length) or self.real_length == 0:
            return None
        return self.real_length / self.pixel_length

    @property
    def pixel_per_unit_length(self):
        '''Length of a pixel in real units'''
        if None in  (self.pt1, self.pt2, self.real_length) or self.real_length == 0:
            return None
        return self.pixel_length / self.real_length


def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__)
    cmdline.add_argument('folder', help='Folder containing the images and vgg file vgg_point_distances.json')
    args = cmdline.parse_args()

    vgg.SILENT = True
    folder = path.normpath(args.folder)
    assert iolib.folder_exists(folder), 'Folder %s not found' % folder
    vgg_file = path.normpath(path.join(folder, VGGFILE))
    print('Opened vgg file %s' % vgg_file)
    out_file = path.normpath(path.join(folder, CSVOUT))

    outdata = [['sample_lengthid', 'sampleid', 'estimate_mm', 'ref_length_type', 'ref_length_mm', 'measured_resolution', 'lens_correction_mm', 'comment', 'unique_code', 'CALCULATED', 'CV']]

    problems = []
    vgg.load_json(vgg_file)
    PP = PrintProgress(sum([1 for x in vgg.imagesGenerator()]), init_msg='\nProcessing...')
    for Img in vgg.imagesGenerator():
        PP.increment()
        lengths = {} #this will contain instances of Measure classes, with the key of the 'fids' attribute
        assert isinstance(Img, vgg.Image)
        for vggReg in Img.roi_generator(shape_type='point'):
            assert isinstance(vggReg, vgg.Region)
            measure_name = vggReg.region_attr.get('fids', '')
            if measure_name != '':
                mm = vggReg.region_attr.get('mm', None)
                mm = None if mm is None else float(mm)
                if lengths.get(measure_name):
                    lengths[measure_name].pt2 = Point2D(vggReg.x, vggReg.y)
                    if lengths[measure_name].real_length is None and isinstance(mm, (float, int)):
                        lengths[measure_name].real_length = mm
                else:
                    lengths[measure_name] = Measure(name=measure_name, pt1=Point2D(vggReg.x, vggReg.y), real_length=mm)
            else:
                continue

        if not lengths:
            problems.append('%s, no suitable points found. Skipped.' % Img.filename)
            continue

        if not lengths.get('obj', None):
            problems.append('%s had points, but no "obj" attr found.' % Img.filename)
            continue

        #build csv lines
        _, fname, _ = get_file_parts(Img.filepath)
        sampleid = DabSamples.sampleids[DabSamples.unique_codes.index(fname)]
        unique_code = fname

        valid = True
        for it in lengths.items():
            if it[1].pt1 is None or it[1].pt2 is None:
                valid = False
                problems.append('%s "%s" missing a point' % (Img.filename, it[0]))
            if it[0] not in MEASURE_TYPES:
                problems.append('%s "%s" unrecognised fids region_attr label' % (Img.filename, it[0]))
                valid = False
            if not valid:
                outdata.append(['',
                            sampleid,
                            '', '', '', '', '',
                            'ERROR OCCURED FOR THIS SAMPLE',
                            unique_code,
                            '']
                           )
                continue

        objM = lengths['obj']
        assert isinstance(objM, Measure)
        calculated_estimates = []
        for it in lengths.items():
            assert isinstance(it, tuple)

            if it[0] == 'obj':
                continue

            if it[0] == 'bg':
                ref_length_type = DabSamples.ref_length_type_bg
            elif it[0] == 'laser':
                ref_length_type = DabSamples.ref_length_type_laser
            elif it[0] == 'fg':
                ref_length_type = DabSamples.ref_length_type_fg
            else:
                raise ValueError('Unknown label "%s" for image %s' % (it[0], Img.filename))
            M = it[1]
            assert isinstance(M, Measure)
            ref_length_mm = M.real_length
            estimate_mm = '' #this is the measurement from the 'raw', i.e. distorted image - Need to sort it manually
            lens_correction_mm = '' #measurement after lens distortion corrected
            CALCULATED = round(M.length_per_pixel * objM.pixel_length) #extra column, need to paste this manually as too much of a pain to fix the file up in code
            calculated_estimates.append(CALCULATED)
            if it == list(lengths.items())[-1]:
                CV = round(100*statistics.stdev(calculated_estimates) / statistics.mean(calculated_estimates))
                if CV > 10:
                    problems.append('%s. High CV %.2f' % (Img.filename, CV))
            else:
                CV = ''

            outdata.append(['',
                sampleid,
                estimate_mm,
                ref_length_type,
                ref_length_mm,
                DabSamples.measured_resolution,
                lens_correction_mm,
                'Autocalculated in point_distances.py',
                unique_code,
                CALCULATED, CV]
                )


    print('Saving CSV data ...')
    iolib.writecsv(out_file, outdata, inner_as_rows=False)
    iolib.folder_open(path.normpath(folder))
    if problems:
        print('\n'.join(problems))




if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
