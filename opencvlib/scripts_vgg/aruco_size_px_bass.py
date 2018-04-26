# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import, unused-variable
'''Get the size of the aruco marker in pixels.

Doesn't need a vgg file

Results saved to a csv file aruco_size_px_bass.csv.

Example:
aruco_size_px_bass.py -p Shore -c GoPro "C:/temp/fshpics"
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

from funclib.iolib import get_file_parts2
from funclib.iolib import get_file_parts
import funclib.iolib as iolib
from funclib.iolib import PrintProgress
from sympy.geometry import Point2D, Line2D
from opencvlib.view import draw_points
from opencvlib.view import show
from opencvlib import aruco
from opencvlib import getimg
from opencvlib.imgpipes.generators import FromPaths
import statistics

CSVOUT = 'aruco_size_px_bass.csv'
ERROUT = 'aruco_size_px_bass_errors.csv'
#Fix to read in dab laser distances

class BassSamples():
    '''some hard coded stuff to help write to excel sheet
    fish_image_data_sheet.xlsm!SQLsample_length
    '''
    #indexes match for these two
    camera = ['GoPro', 'XP30', 's5690'] #valid cameras
    platform = ['Shore', 'Charter'] #valid platforms
    #these next 4 lists match by index. They are taken from the excel sheet fish_image_data_sheet.xlsm
    fidkey = ['MorrisonsNextGen 5121', 'MorrisonsNextGen 5121', 'MorrisonsNextGen 5122', 'MorrisonsNextGen 5122', 'MorrisonsNextGen 5124', 'MorrisonsNextGen 5124', 'MorrisonsNextGen 5125', 'MorrisonsNextGen 5125', 'MorrisonsNextGen 5126', 'MorrisonsNextGen 5126', 'MorrisonsNextGen 5127', 'MorrisonsNextGen 5127', 'MorrisonsNextGen 5128', 'MorrisonsNextGen 5128', 'MorrisonsNextGen 5129', 'MorrisonsNextGen 5129', 'MorrisonsNextGen 512419', 'MorrisonsNextGen 512419', 'MorrisonsNextGen 512419', 'MermaidNextGen 5123QH', 'MermaidNextGen 5123QH', 'MermaidNextGen 5123QH', 'MermaidNextGen 51240M', 'MermaidNextGen 51240M', 'MermaidNextGen 51240M', 'MermaidNextGen 5124TS', 'MermaidNextGen 5124TS', 'MermaidNextGen 5124TS', 'MermaidNextGen 5124UQ', 'MermaidNextGen 5124UQ', 'MermaidNextGen 5124UQ', 'MermaidNextGen 51287K', 'MermaidNextGen 51287K', 'MermaidNextGen 51287K', 'MermaidNextGen 5128CG', 'MermaidNextGen 5128CG', 'MermaidNextGen 5128CG', 'MorrisonsNextGen 5128HX', 'MorrisonsNextGen 5128HX', 'MorrisonsNextGen 5128HX', 'MermaidNextGen 512DQ5', 'MermaidNextGen 512DQ5', 'MermaidNextGen 512DQ5', 'MermaidNextGen 512EHV', 'MermaidNextGen 512EHV', 'MermaidNextGen 512EHV', 'MermaidNextGen 512EPP', 'MermaidNextGen 512EPP', 'MermaidNextGen 512EPP', 'MermaidNextGen 512FJY', 'MermaidNextGen 512FJY', 'MermaidNextGen 512FJY', 'MermaidNextGen 512H47', 'MermaidNextGen 512H47', 'MermaidNextGen 512H47', 'MermaidNextGen 512HPR', 'MermaidNextGen 512HPR', 'MermaidNextGen 512HPR', 'MermaidNextGen 512HY1', 'MermaidNextGen 512HY1', 'MermaidNextGen 512HY1', 'MermaidNextGen 512IBP', 'MermaidNextGen 512IBP', 'MermaidNextGen 512IBP', 'MorrisonsNextGen 512IKF', 'MorrisonsNextGen 512IKF', 'MorrisonsNextGen 512IKF', 'MermaidNextGen 512K4I', 'MermaidNextGen 512K4I', 'MermaidNextGen 512K4I', 'MermaidNextGen 512KID', 'MermaidNextGen 512KID', 'MermaidNextGen 512KID', 'MermaidNextGen 512LLQ', 'MermaidNextGen 512LLQ', 'MermaidNextGen 512LLQ', 'MorrisonsNextGen 512LT3', 'MorrisonsNextGen 512LT3', 'MorrisonsNextGen 512LT3', 'MermaidNextGen 512LZB', 'MermaidNextGen 512LZB', 'MermaidNextGen 512LZB', 'MermaidNextGen 512N90', 'MermaidNextGen 512N90', 'MermaidNextGen 512N90', 'MermaidNextGen 512OET', 'MermaidNextGen 512OET', 'MermaidNextGen 512OET', 'MorrisonsNextGen 512PX5', 'MorrisonsNextGen 512PX5', 'MorrisonsNextGen 512PX5', 'MermaidNextGen 512Q2Y', 'MermaidNextGen 512Q2Y', 'MermaidNextGen 512Q2Y', 'MermaidNextGen 512QE3', 'MermaidNextGen 512QE3', 'MermaidNextGen 512QE3', 'MorrisonsNextGen 512QEC', 'MorrisonsNextGen 512QEC', 'MorrisonsNextGen 512QEC', 'MermaidNextGen 512QZ5', 'MermaidNextGen 512QZ5', 'MermaidNextGen 512QZ5', 'MermaidNextGen 512T2E', 'MermaidNextGen 512T2E', 'MermaidNextGen 512T2E', 'MorrisonsNextGen 512T41', 'MorrisonsNextGen 512T41', 'MorrisonsNextGen 512T41', 'MermaidNextGen 512TD6', 'MermaidNextGen 512TD6', 'MermaidNextGen 512TD6', 'MorrisonsNextGen 512TIV', 'MorrisonsNextGen 512TIV', 'MorrisonsNextGen 512TIV', 'MermaidNextGen 512TSH', 'MermaidNextGen 512TSH', 'MermaidNextGen 512TSH', 'MermaidNextGen 512ZYL', 'MermaidNextGen 512ZYL', 'MermaidNextGen 512ZYL', 'SoSNextGen 512QVC', 'SoSNextGen 512QVC', 'SoSNextGen 512QVC', 'SoSNextGen 512HIC', 'SoSNextGen 512HIC', 'SoSNextGen 512HIC', 'SoSNextGen 5129JC', 'SoSNextGen 5129JC', 'SoSNextGen 5129JC', 'SoSNextGen 512MH6', 'SoSNextGen 512MH6', 'SoSNextGen 512MH6', 'SoSNextGen 512F2U', 'SoSNextGen 512F2U', 'SoSNextGen 512B81', 'SoSNextGen 512B81', 'SoSNextGen 512B5U', 'SoSNextGen 512B5U', 'SoSNextGen 512F1R', 'SoSNextGen 512F1R', 'SoSNextGen 5126XT', 'SoSNextGen 5126XT', 'SoSNextGen 512BHQ', 'SoSNextGen 512BHQ', 'SoSNextGen 512BHQ', 'SoSNextGen 512Q9A', 'SoSNextGen 512Q9A', 'SoSNextGen 512Q9A', 'SoSNextGen 51263A', 'SoSNextGen 51263A', 'SoSNextGen 51263A', 'SoSNextGen 512MDG', 'SoSNextGen 512MDG', 'SoSNextGen 512MDG', 'SoSNextGen 512I8V', 'SoSNextGen 512I8V', 'SoSNextGen 512I8V', 'SoSNextGen 5126EI', 'SoSNextGen 5126EI', 'SoSNextGen 5125KS', 'SoSNextGen 5125KS', 'SoSNextGen 5125KS', 'SoSNextGen 512TGH', 'SoSNextGen 512TGH', 'SoSNextGen 512TGH', 'SoSNextGen 512JUM', 'SoSNextGen 512JUM', 'SoSNextGen 512JUM', 'SoSNextGen 5127A4', 'SoSNextGen 5127A4', 'SoSNextGen 5127A4', 'SoSNextGen 512L2T', 'SoSNextGen 512L2T', 'SoSNextGen 512L2T', 'SoSNextGen 512QNK', 'SoSNextGen 512QNK', 'SoSNextGen 512QNK', 'SoSNextGen 5126ZP', 'SoSNextGen 5126ZP', 'SoSNextGen 5126ZP', 'SoSNextGen 512G4X', 'SoSNextGen 512G4X', 'SoSNextGen 512G4X', 'SoSNextGen 512AUV', 'SoSNextGen 512AUV', 'SoSNextGen 512AUV', 'SoSNextGen 512KIF', 'SoSNextGen 512KIF', 'SoSNextGen 512KIF', 'SoSNextGen 512QK7', 'SoSNextGen 512QK7', 'SoSNextGen 512QK7', 'SoSNextGen 512Q3Q', 'SoSNextGen 512Q3Q', 'SoSNextGen 512Q3Q', 'SoSNextGen 512ZUV', 'SoSNextGen 512ZUV', 'SoSNextGen 512ZUV', 'SoSNextGen 512K89', 'SoSNextGen 512K89', 'SoSNextGen 512K89', 'SoSNextGen 512A6P', 'SoSNextGen 512A6P', 'SoSNextGen 512A6P', 'SoSNextGen 512KZY', 'SoSNextGen 512KZY', 'SoSNextGen 512KZY', 'SoSNextGen 512QLX', 'SoSNextGen 512QLX', 'SoSNextGen 512QLX', 'CharterXP30444', 'CharterXP30482a', 'CharterXP30542', 'CharterXP30375', 'CharterXP30478', 'CharterXP30441', 'CharterXP30469', 'CharterXP30458', 'CharterXP30565', 'CharterXP30472', 'CharterXP30468a', 'CharterXP30497', 'CharterXP30427', 'CharterXP30433', 'CharterXP30409a', 'CharterXP30361', 'CharterXP30598', 'CharterXP30424', 'CharterXP30405', 'CharterXP30572', 'CharterXP30454', 'CharterXP30430', 'CharterXP30358', 'CharterXP30425', 'CharterXP30527', 'CharterXP30394', 'CharterXP30519', 'CharterXP30421', 'CharterXP30573', 'CharterXP30501', 'CharterXP30482', 'CharterXP30520', 'CharterXP30551', 'CharterXP30459', 'CharterXP30510', 'CharterXP30510a', 'CharterXP30533', 'CharterXP30509', 'CharterXP30583', 'CharterXP30497a', 'CharterXP30468', 'CharterXP30481', 'CharterXP30374', 'CharterXP30595', 'CharterXP30409', 'CharterGoPro472', 'CharterGoPro510a', 'CharterGoPro510', 'CharterGoPro583', 'CharterGoPro454', 'CharterGoPro510b', 'CharterGoPro551', 'CharterGoPro591', 'CharterGoPro526', 'CharterGoPro421', 'CharterGoPro496', 'CharterGoPro509', 'CharterGoPro374', 'CharterGoPro409a', 'CharterGoPro572', 'CharterGoPro358', 'CharterGoPro478', 'CharterGoPro459', 'CharterGoPro565', 'CharterGoPro433', 'CharterGoPro394', 'CharterGoPro598', 'CharterGoPro595', 'CharterGoPro375', 'CharterGoPro458', 'CharterGoPro424', 'CharterGoPro527', 'CharterGoPro444', 'CharterGoPro542', 'CharterGoPro441a', 'CharterGoPro427', 'CharterGoPro409', 'CharterGoPro482a', 'CharterGoPro441', 'CharterGoPro448', 'CharterGoPro442', 'CharterGoPro468a', 'CharterGoPro523a', 'CharterGoPro361', 'CharterGoPro519', 'CharterGoPro430', 'CharterGoPro405', 'CharterGoPro425', 'CharterGoPro523', 'CharterGoPro501', 'CharterGoPro468', 'CharterGoPro497', 'CharterGoPro481', 'CharterGoPro497a', 'Charters5690433', 'Charters5690458', 'Charters5690496', 'Charters5690459', 'Charters5690444', 'Charters5690509', 'Charters5690598', 'Charters5690573', 'Charters5690481', 'Charters5690533', 'Charters5690454', 'Charters5690588', 'Charters5690375', 'Charters5690482', 'Charters5690425', 'Charters5690591', 'Charters5690430a', 'Charters5690478', 'Charters5690572', 'Charters5690497', 'Charters5690394', 'Charters5690468a', 'Charters5690424', 'Charters5690501', 'Charters5690510', 'Charters5690472', 'Charters5690483', 'Charters5690421', 'Charters5690448', 'Charters5690374', 'Charters5690358', 'Charters5690498', 'Charters5690442', 'Charters5690542', 'Charters5690468', 'Charters5690565', 'Charters5690583', 'Charters5690409', 'Charters5690469', 'Charters5690510b', 'Charters5690409a', 'Charters5690405', 'Charters5690510a', 'Charters5690595', 'Charters5690527', 'Charters5690523', 'Charters5690361', 'Charters5690441', 'Charters5690551', 'ShoreXP30279_2', 'ShoreXP30346', 'ShoreXP30294', 'ShoreXP30325', 'ShoreXP30343', 'ShoreXP30344', 'ShoreXP30309', 'ShoreXP30301', 'ShoreXP30330', 'ShoreXP30537', 'ShoreXP30420', 'ShoreXP30498', 'ShoreXP30339', 'ShoreXP30298', 'ShoreXP30363', 'ShoreXP30319', 'ShoreXP30419', 'ShoreXP30406', 'ShoreXP30618', 'ShoreXP30413', 'ShoreXP30295_2', 'ShoreXP30308', 'ShoreXP30285', 'ShoreXP30329', 'ShoreXP30326', 'ShoreXP30520', 'ShoreXP30589', 'ShoreXP30370', 'ShoreXP30381', 'ShoreXP30234', 'ShoreXP30434', 'ShoreXP30448', 'ShoreXP30316', 'ShoreXP30353', 'ShoreXP30364', 'ShoreXP30276', 'ShoreXP30322_2', 'ShoreXP30411', 'ShoreXP30292', 'ShoreXP30341', 'ShoreXP30341_2', 'ShoreXP30311', 'ShoreXP30404', 'ShoreXP30295', 'ShoreXP30296', 'ShoreXP30503', 'ShoreXP30338', 'ShoreXP30258', 'ShoreXP30555', 'ShoreXP30403', 'ShoreXP30322', 'ShoreGoPro294', 'ShoreGoPro589', 'ShoreGoPro520', 'ShoreGoPro403', 'ShoreGoPro555', 'ShoreGoPro296', 'ShoreGoPro316', 'ShoreGoPro381', 'ShoreGoPro322_2', 'ShoreGoPro339', 'ShoreGoPro404', 'ShoreGoPro591', 'ShoreGoPro285', 'ShoreGoPro344', 'ShoreGoPro330', 'ShoreGoPro295_2', 'ShoreGoPro353', 'ShoreGoPro292', 'ShoreGoPro329_2', 'ShoreGoPro338', 'ShoreGoPro370', 'ShoreGoPro537', 'ShoreGoPro346', 'ShoreGoPro364', 'ShoreGoPro448', 'ShoreGoPro326', 'ShoreGoPro503', 'ShoreGoPro295', 'ShoreGoPro413', 'ShoreGoPro322', 'ShoreGoPro588', 'ShoreGoPro341', 'ShoreGoPro325', 'ShoreGoPro301', 'ShoreGoPro319', 'ShoreGoPro311', 'ShoreGoPro308', 'ShoreGoPro434', 'ShoreGoPro279_2', 'ShoreGoPro498', 'ShoreGoPro411', 'ShoreGoPro234', 'ShoreGoPro309', 'ShoreGoPro303', 'ShoreGoPro406', 'ShoreGoPro354', 'ShoreGoPro341_2', 'ShoreGoPro279', 'ShoreGoPro420', 'ShoreGoPro329', 'ShoreGoPro600', 'ShoreGoPro602', 'ShoreGoPro419', 'ShoreGoPro343', 'ShoreGoPro363', 'ShoreGoPro548', 'ShoreGoPro382', 'Shores5690279', 'Shores5690618', 'Shores5690498', 'Shores5690602', 'Shores5690353', 'Shores5690419', 'Shores5690296', 'Shores5690363', 'Shores5690292', 'Shores5690322', 'Shores5690413', 'Shores5690329', 'Shores5690295_2', 'Shores5690338', 'Shores5690343', 'Shores5690600', 'Shores5690339', 'Shores5690301', 'Shores5690276', 'Shores5690262', 'Shores5690370', 'Shores5690322_2', 'Shores5690329_2', 'Shores5690434', 'Shores5690354', 'Shores5690234', 'Shores5690344', 'Shores5690319', 'Shores5690411', 'Shores5690364', 'Shores5690381', 'Shores5690294', 'Shores5690448', 'Shores5690341_2', 'Shores5690309', 'Shores5690298', 'Shores5690326', 'Shores5690308', 'Shores5690346', 'Shores5690520', 'Shores5690403', 'Shores5690432', 'Shores5690537', 'Shores5690404', 'Shores5690316', 'Shores5690311', 'Shores5690295', 'Shores5690330', 'Shores5690279_2', 'Shores5690285', 'Shores5690325', 'Shores5690406', 'Shores5690303', 'Shores5690341', 'ShoreXP30303', 'ShoreXP30279', 'ShoreXP30290', 'ShoreXP30329_2', 'ShoreXP30354', 'ShoreXP30548', 'ShoreGoPro298', 'ShoreGoPro582']


class BassMeasure():
    '''A measure between the snout and the fork

    Properties:
        pixel_length: length between two points in pixels
        length_per_pixel: Length of a pixel in real units
    '''
    def __init__(self, name, pt1, pt2, px_len_mm):
        self.name = name
        self._pt1 = pt1
        self._pt2 = pt2
        self._px_len_mm = px_len_mm
        self._length_px = abs(self._pt1.distance(self._pt2).evalf())

    def __repr__(self):
        return 'Measure "%s" [%s,%s]' % (
                            self.name,
                            str(tuple(self._pt1) if isinstance(self._pt1, Point2D) else ''),
                            str(tuple(self._pt2) if isinstance(self._pt2, Point2D) else ''))



def getkey(fname, platform, camera):
    '''(str, str, str) -> str, str, str, int
    Get some lookup values to create
    an SQLsample_length record.

    Returns:
        unique key
    '''
    assert platform in BassSamples.platform, 'platform %s not valid' % platform
    assert camera in BassSamples.camera, 'camera %s invald' % camera
    assert isinstance(fname, str)

    s = fname.replace('r', '')
    s = s.replace('_FISHUND', '')
    s = s.replace('_UND', '')
    s = s.replace('.jpg', '')
    s = s.replace('.png', '')

    fidkey = '%s%s%s' % (platform, camera, s)
    return fidkey


def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__)
    cmdline.add_argument('-p', '--platform', help='Platform, must be in [Shore, Charter]')
    cmdline.add_argument('-c', '--camera', help='Camera, must be in [GoPro, s5690, XP30]')
    cmdline.add_argument('folder', help='Folder containing the images which have aruco markers')
    args = cmdline.parse_args()
    print('Folder: %s\nCamera: "%s"\nPlatform: "%s"' % (args.folder, args.camera, args.platform))

    assert args.platform in BassSamples.platform, 'Invalid platform "%s"' % args.platform
    assert args.camera in BassSamples.camera, 'Invalid camera "%s"' % args.camera

    folder = path.normpath(args.folder)
    assert iolib.folder_exists(folder), 'Folder %s not found' % folder
    out_file = path.normpath(path.join(folder, CSVOUT))
    out_errs_file = path.normpath(path.join(folder, ERROUT))

    outdata = [['key', 'pxlen']]

    multi_markers = []
    no_markers = []
    errors = []

    FP = FromPaths(folder, wildcards='*.jpg')
    PP = PrintProgress(sum([1 for x in FP.generate(pathonly=True)]), init_msg='\nProcessing...')
    for img, filepath, _ in FP.generate():
        PP.increment()

        _, fname, _ = get_file_parts2(filepath)
        key = getkey(fname, args.platform, args.camera)
        assert key in BassSamples.fidkey, 'fidkey %s not found' % key
        D = aruco.Detected(img)
        using_expected = False
        if fname in ['r405_FISHUND.jpg', 'r409a_FISHUND.jpg', 'r510a_FISHUND.jpg', 'r420_UND.jpg', 'r482_UND.jpg', 'r405_UND.jpg', 'r413_FISHUND.jpg', 'r432_FISHUND.jpg', 'r406_FISHUND.jpg']:
            D.detect(expected=aruco.eMarkerID.Sz30)
            using_expected = True
        elif fname in ['r582_UND.jpg', 'r548_FISHUND.jpg', 'r582_FISHUND.jpg']:
            D.detect(expected=aruco.eMarkerID.Sz30_flip)
            using_expected = True
        elif fname in ['r618_UND.jpg']:
            D.detect(expected=aruco.eMarkerID.Sz50)
            using_expected = True
        elif fname in ['r258_UND.jpg', 'r370_FISHUND.jpg', 'r370_UND.jpg']:
            D.detect(expected=aruco.eMarkerID.Sz25)
            using_expected = True
        else:
            D.detect()

        if D.Markers:
            if len(D.Markers) > 1:
                multi_markers.append(['%s had multiple markers' % (fname)])
                continue
            Marker = D.Markers[0]
            assert isinstance(Marker, aruco.Marker)
            ref_length_type = Marker.markerid.name
            ref_length_mm = Marker.side_length_mm
        else:
            if using_expected:
                no_markers.append(['%s, Expected Aruco marker not found' % (fname)])
            else:
                no_markers.append(['%s [sampleid:%s], found no Aruco markers' % (fname)])
            continue

        outdata.append([key, round(Marker.side_px, 3)]) #used side_px as the spreadsheet fish_image_data_sheet.xlsm recorded the side length in mm for simplicity. Should be no need to change to diagonal lengths.


    print('Saving CSV data ...')
    iolib.writecsv(out_file, outdata, inner_as_rows=False)
    iolib.folder_open(path.normpath(folder))


    all_errs = []
    all_errs.extend(multi_markers)
    all_errs.extend(no_markers)
    _ = [print(x[0]) for x in all_errs]

    if all_errs:
        print('Errors written to %s' % out_errs_file)
        iolib.writecsv(out_errs_file, all_errs, inner_as_rows=False)




if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
