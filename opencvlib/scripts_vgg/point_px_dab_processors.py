# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import
'''Get the pixel distances for bg, fg and lasers from
the processors bass pictures.

Uses a vgg file with the region annotation "fids".

The vgg file must be called vgg_px_distance.json.

Results saved to a csv file called vgg_px_distance.csv.

Example:
point_px_dab_processors.py "C:/temp/fshpics"
'''
#Source images were in C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\dab\sos\fiducal_length\undistorted

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
CSVOUT = 'vgg_px_distance.csv'

MEASURE_TYPES = ['bg', 'laser', 'fg', 'obj']


#Fix to read in dab laser distances

def getkey(fname):
    '''(str) -> str
    Get key
    '''
    assert isinstance(fname, str)
    s = fname.replace('_UND', '')
    s = s.replace('.png', '')
    return s


class DabSamplesProcessors():
    '''some hard coded stuff to help write to excel sheet
    fish_image_data_sheet.xlsm!SQLsample_length
    '''
    #indexes match for these two
    keys = ['dabQVCbackground checker', 'dabQVCforeground checker', 'dabQVClaser lines', 'dabHICbackground checker', 'dabHICforeground checker', 'dabHIClaser lines', 'dab9JCbackground checker', 'dab9JCforeground checker', 'dab9JClaser lines', 'dabMH6background checker', 'dabMH6foreground checker', 'dabMH6laser lines', 'dabF2Ubackground checker', 'dabF2Uforeground checker', 'dabB81background checker', 'dabB81foreground checker', 'dabB5Ubackground checker', 'dabB5Uforeground checker', 'dabF1Rbackground checker', 'dabF1Rforeground checker', 'dab6XTbackground checker', 'dab6XTforeground checker', 'dabBHQbackground checker', 'dabBHQforeground checker', 'dabBHQlaser lines', 'dabQ9Abackground checker', 'dabQ9Aforeground checker', 'dabQ9Alaser lines', 'dab63Abackground checker', 'dab63Aforeground checker', 'dab63Alaser lines', 'dabMDGbackground checker', 'dabMDGforeground checker', 'dabMDGlaser lines', 'dabI8Vbackground checker', 'dabI8Vforeground checker', 'dabI8Vlaser lines', 'dab6EIbackground checker', 'dab6EIforeground checker', 'dab5KSbackground checker', 'dab5KSforeground checker', 'dab5KSlaser lines', 'dabTGHbackground checker', 'dabTGHforeground checker', 'dabTGHlaser lines', 'dabJUMbackground checker', 'dabJUMforeground checker', 'dabJUMlaser lines', 'dab7A4background checker', 'dab7A4foreground checker', 'dab7A4laser lines', 'dabL2Tbackground checker', 'dabL2Tforeground checker', 'dabL2Tlaser lines', 'dabQNKbackground checker', 'dabQNKforeground checker', 'dabQNKlaser lines', 'dab6ZPbackground checker', 'dab6ZPforeground checker', 'dab6ZPlaser lines', 'dabG4Xbackground checker', 'dabG4Xforeground checker', 'dabG4Xlaser lines', 'dabAUVbackground checker', 'dabAUVforeground checker', 'dabAUVlaser lines', 'dabKIFbackground checker', 'dabKIFforeground checker', 'dabKIFlaser lines', 'dabQK7background checker', 'dabQK7foreground checker', 'dabQK7laser lines', 'dabQ3Qbackground checker', 'dabQ3Qforeground checker', 'dabQ3Qlaser lines', 'dabZUVbackground checker', 'dabZUVforeground checker', 'dabZUVlaser lines', 'dabK89background checker', 'dabK89foreground checker', 'dabK89laser lines', 'dabA6Pbackground checker', 'dabA6Pforeground checker', 'dabA6Plaser lines', 'dabKZYbackground checker', 'dabKZYforeground checker', 'dabKZYlaser lines', 'dabQLXbackground checker', 'dabQLXforeground checker', 'dabQLXlaser lines']

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
            if it[0] == 'obj':
                continue

            if not valid:
                if it[0] == 'bg':
                    ref_length_type = DabSamplesProcessors.ref_length_type_bg
                elif it[0] == 'laser':
                    ref_length_type = DabSamplesProcessors.ref_length_type_laser
                elif it[0] == 'fg':
                    ref_length_type = DabSamplesProcessors.ref_length_type_fg
                else:
                    ref_length_type = 'UNKNOWN'
                key_tmp = 'dab%s%s' % (key, ref_length_type)
                outdata.append([key_tmp, 'ERROR OCCURED FOR THIS SAMPLE'])
                continue



        for it in lengths.items():
            assert isinstance(it, tuple)
            if it[0] == 'bg':
                ref_length_type = DabSamplesProcessors.ref_length_type_bg
            elif it[0] == 'laser':
                ref_length_type = DabSamplesProcessors.ref_length_type_laser
            elif it[0] == 'fg':
                ref_length_type = DabSamplesProcessors.ref_length_type_fg
            elif it[0] == 'obj':
                continue
            else:
                raise ValueError('Unknown label "%s" for image %s' % (it[0], Img.filename))
            key_tmp = 'dab%s%s' % (key, ref_length_type)
            assert key_tmp in DabSamplesProcessors.keys, 'Unknown key %s' % key_tmp

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
