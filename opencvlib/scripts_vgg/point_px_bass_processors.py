# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import
'''Get the pixel distances for bg, fg and lasers from
the processors bass pictures.

Uses a vgg file with the region annotation "fids".

The vgg file must be called vgg_px_distance.json.

Results saved to a csv file called vgg_px_distance.csv.

Example:
point_px_bass_processors.py "C:/temp/fshpics"
'''
#Source images in: "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/processors/undistorted"

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

VGGFILE = 'vgg_px_distance.json'
CSVOUT = 'vgg_px_distance.json.csv'

MEASURE_TYPES = ['bg', 'laser', 'fg', 'obj']
MEASURE_TYPES.extend([str(x) for x in range(1, 21)])

#Fix to read in dab laser distances

def getkey(fname):
    '''(str) -> str
    Get key
    '''
    assert isinstance(fname, str)
    s = fname.replace('_UND', '')
    s = s.replace('.png', '')
    return s


class BassSamplesProcessors():
    '''some hard coded stuff to help write to excel sheet
    fish_image_data_sheet.xlsm!SQLsample_length
    '''
    #indexes match for these two
    keys = ['1laser lines', '1background checker', '2laser lines', '2background checker', '4laser lines', '4background checker', '5laser lines', '5background checker', '6laser lines', '6background checker', '7laser lines', '7background checker', '8laser lines', '8background checker', '9laser lines', '9background checker', 'TIVlaser lines', 'TIVbackground checker', 'TIVforeground checker', 'IKFlaser lines', 'IKFbackground checker', 'IKFforeground checker', '8HXlaser lines', '8HXbackground checker', '8HXforeground checker', 'PX5laser lines', 'PX5background checker', 'PX5foreground checker', '419laser lines', '419background checker', '419foreground checker', 'LT3laser lines', 'LT3background checker', 'LT3foreground checker', 'T41laser lines', 'T41background checker', 'T41foreground checker', 'QEClaser lines', 'QECbackground checker', 'QECforeground checker', 'KIDlaser lines', 'KIDbackground checker', 'KIDforeground checker', 'TSHlaser lines', 'TSHbackground checker', 'TSHforeground checker', 'HY1laser lines', 'HY1background checker', 'HY1foreground checker', 'QZ5laser lines', 'QZ5background checker', 'QZ5foreground checker', 'LLQlaser lines', 'LLQbackground checker', 'LLQforeground checker', 'N90laser lines', 'N90background checker', 'N90foreground checker', 'FJYlaser lines', 'FJYbackground checker', 'FJYforeground checker', 'EPPlaser lines', 'EPPbackground checker', 'EPPforeground checker', 'TD6laser lines', 'TD6background checker', 'TD6foreground checker', 'IBPlaser lines', 'IBPbackground checker', 'IBPforeground checker', 'HPRlaser lines', 'HPRbackground checker', 'HPRforeground checker', 'Q2Ylaser lines', 'Q2Ybackground checker', 'Q2Yforeground checker', '4UQlaser lines', '4UQbackground checker', '4UQforeground checker', 'EHVlaser lines', 'EHVbackground checker', 'EHVforeground checker', 'T2Elaser lines', 'T2Ebackground checker', 'T2Eforeground checker', 'QE3laser lines', 'QE3background checker', 'QE3foreground checker', '4TSlaser lines', '4TSbackground checker', '4TSforeground checker', '87Klaser lines', '87Kbackground checker', '87Kforeground checker', '40Mlaser lines', '40Mbackground checker', '40Mforeground checker', 'ZYLlaser lines', 'ZYLbackground checker', 'ZYLforeground checker', 'DQ5laser lines', 'DQ5background checker', 'DQ5foreground checker', '8CGlaser lines', '8CGbackground checker', '8CGforeground checker', '3QHlaser lines', '3QHbackground checker', '3QHforeground checker', 'K4Ilaser lines', 'K4Ibackground checker', 'K4Iforeground checker', 'LZBlaser lines', 'LZBbackground checker', 'LZBforeground checker', 'OETlaser lines', 'OETbackground checker', 'OETforeground checker', 'H47laser lines', 'H47background checker', 'H47foreground checker']
    sampleids = [1, 1, 2, 2, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 16, 16, 16, 17, 17, 17, 18, 18, 18, 19, 19, 19, 20, 20, 20, 21, 21, 21, 22, 22, 22, 23, 23, 23, 24, 24, 24, 25, 25, 25, 26, 26, 26, 27, 27, 27, 28, 28, 28, 29, 29, 29, 30, 30, 30, 31, 31, 31, 32, 32, 32, 33, 33, 33, 34, 34, 34, 35, 35, 35, 36, 36, 36, 37, 37, 37, 38, 38, 38, 39, 39, 39, 40, 40, 40, 41, 41, 41, 42, 42, 42, 43, 43, 43, 44, 44, 44, 45, 45, 45, 46, 46, 46, 47, 47, 47, 48, 48, 48, 49, 49, 49, 50, 50, 50]
    sampleids = [str(s) for s in sampleids]
    unique_codes = [1, 1, 2, 2, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 'TIV', 'TIV', 'TIV', 'IKF', 'IKF', 'IKF', '8HX', '8HX', '8HX', 'PX5', 'PX5', 'PX5', 419, 419, 419, 'LT3', 'LT3', 'LT3', 'T41', 'T41', 'T41', 'QEC', 'QEC', 'QEC', 'KID', 'KID', 'KID', 'TSH', 'TSH', 'TSH', 'HY1', 'HY1', 'HY1', 'QZ5', 'QZ5', 'QZ5', 'LLQ', 'LLQ', 'LLQ', 'N90', 'N90', 'N90', 'FJY', 'FJY', 'FJY', 'EPP', 'EPP', 'EPP', 'TD6', 'TD6', 'TD6', 'IBP', 'IBP', 'IBP', 'HPR', 'HPR', 'HPR', 'Q2Y', 'Q2Y', 'Q2Y', '4UQ', '4UQ', '4UQ', 'EHV', 'EHV', 'EHV', 'T2E', 'T2E', 'T2E', 'QE3', 'QE3', 'QE3', '4TS', '4TS', '4TS', '87K', '87K', '87K', '40M', '40M', '40M', 'ZYL', 'ZYL', 'ZYL', 'DQ5', 'DQ5', 'DQ5', '8CG', '8CG', '8CG', '3QH', '3QH', '3QH', 'K4I', 'K4I', 'K4I', 'LZB', 'LZB', 'LZB', 'OET', 'OET', 'OET', 'H47', 'H47', 'H47']
    unique_codes = [str(s) for s in unique_codes]
    file_names = ['%s_UND.png' for code in unique_codes]

    ref_length_type_laser = 'laser lines'
    ref_length_type_bg = 'background checker'
    ref_length_type_fg = 'foreground checker'


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
        return 'Measure "%s" [%s,%s]' % (
                            self.name,
                            str(tuple(self.pt1) if isinstance(self.pt1, Point2D) else ''),
                            str(tuple(self.pt2) if isinstance(self.pt2, Point2D) else '')
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

    outdata = [['key', 'px_len']]

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
                if lengths.get(measure_name):
                    lengths[measure_name].pt2 = Point2D(vggReg.x, vggReg.y)
                else:
                    lengths[measure_name] = Measure(name=measure_name, pt1=Point2D(vggReg.x, vggReg.y))
            else:
                continue

        if not lengths:
            problems.append('%s, no suitable points found. Skipped.' % Img.filename)
            continue

        #build csv lines
        _, fname, _ = get_file_parts(Img.filepath)
        key = getkey(fname)

        #Check validity first
        #it[1] is the dict value, it[0] is dict key
        valid = True
        for it in lengths.items():
            if it[1].pt1 is None or it[1].pt2 is None:
                valid = False
                problems.append('%s "%s" missing a point' % (Img.filename, it[0]))
            if it[0] not in MEASURE_TYPES:
                problems.append('%s "%s" unrecognised fids region_attr label' % (Img.filename, it[0]))
                valid = False

            if not valid:
                if it[0] == 'bg':
                    ref_length_type = BassSamplesProcessors.ref_length_type_bg
                elif it[0] == 'laser':
                    ref_length_type = BassSamplesProcessors.ref_length_type_laser
                elif it[0] == 'fg':
                    ref_length_type = BassSamplesProcessors.ref_length_type_fg
                else:
                    ref_length_type = 'UNKNOWN'
                key_tmp = '%s%s' % (key, ref_length_type)
                outdata.append([key_tmp, 'ERROR OCCURED FOR THIS SAMPLE'])
                continue



        for it in lengths.items():
            assert isinstance(it, tuple)
            if it[0] == 'bg':
                ref_length_type = BassSamplesProcessors.ref_length_type_bg
            elif it[0] == 'laser':
                ref_length_type = BassSamplesProcessors.ref_length_type_laser
            elif it[0] == 'fg':
                ref_length_type = BassSamplesProcessors.ref_length_type_fg
            else:
                raise ValueError('Unknown label "%s" for image %s' % (it[0], Img.filename))
            key_tmp = '%s%s' % (key, ref_length_type)
            M = it[1]
            assert isinstance(M, Measure)
            outdata.append([key_tmp, round(M.pixel_length, 3)])


    print('Saving CSV data ...')
    iolib.writecsv(out_file, outdata, inner_as_rows=False)
    iolib.folder_open(path.normpath(folder))
    if problems:
        print('\n'.join(problems))




if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
