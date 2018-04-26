# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import, unused-variable
'''Estimate subject-len distance.

Uses a vgg file with just two points added which represent
a real world distance of 50 mm.


The vgg file must be called vgg_subject_distance.json.

Example:
subject_distance.py "C:/temp/fshpics"
'''

import argparse
import os.path as path

import opencvlib.imgpipes.vgg as vgg
from funclib.iolib import get_file_parts2
from funclib.iolib import get_file_parts
import funclib.iolib as iolib
from funclib.iolib import writecsv
from funclib.iolib import PrintProgress
from sympy.geometry import Point2D, Line2D
from opencvlib.view import draw_points
from opencvlib.view import show
from opencvlib import getimg
import statistics

VGGFILE = 'vgg_subject_distance.json'
OUTFILE = 'vgg_subject_distance.csv'

EXPECTED_LENGTH = 50 #50mm
CMOS_X = 5.42

class BassSamples():
    '''some hard coded stuff to help write to excel sheet
    fish_image_data_sheet.xlsm!SQLsample_length
    '''
    focal_distance = 2. #mm
    uniquekey = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 419, '3QH', '40M', '4TS', '4UQ', '87K', '8CG', '8HX', 'DQ5', 'EHV', 'EPP', 'FJY', 'H47', 'HPR', 'HY1', 'IBP', 'IKF', 'K4I', 'KID', 'LLQ', 'LT3', 'LZB', 'N90', 'OET', 'PX5', 'Q2Y', 'QE3', 'QEC', 'QZ5', 'T2E', 'T41', 'TD6', 'TIV', 'TSH', 'ZYL', 'RZA', 'V4Y', 'QVC', 'HIC', '9JC', 'MH6', 'F2U', 'B81', 'HSA', 'B5U', 'F1R', '6XT', 'BHQ', 'Q9A', '63A', 'MDG', 'I8V', '6EI', '5KS', 'DAD', 'TGH', 'JUM', '7A4', 'L2T', 'QNK', '6ZP', 'KW4', 'G4X', 'AUV', 'KIF', 'QK7', 'Q3Q', 'ZUV', 'K89', 'A6P', 'KZY', 'QLX', '497a', 472, 501, 551, 527, 572, 520, 409, 458, 316, 469, 583, 542, 533, 497, 509, 510, 519, 482, 454, 427, 374, 375, 441, 330, 394, 361, 364, '409a', 405, 358, 595, 424, 421, '468a', '482a', 468, 433, 565, 459, 481, 478, 444, '510a', 430, 509, 510, '510a', '510b', 523, 527, 533, 542, 551, 565, 572, 573, 583, 588, 591, 595, 598, 358, 361, 370, 375, 394, 405, 409, '409a', 421, 424, 425, '430a', 433, 441, 442, 444, 448, 454, 374, 459, 468, '468a', 381, 472, 478, 481, 482, 483, 496, 497, 498, 501, 482, 523, '523a', 526, 527, 425, 551, 565, 572, 583, 591, 595, 598, 358, 361, 374, 427, 375, 394, 405, 409, '409a', 421, 424, 425, 430, 433, 441, '441a', 442, 444, 448, 454, 458, 434, 468, 448, 472, 478, 458, '482a', 496, 497, '497a', 501, 459, 510, '510a', '510b', 519, 298, 279, 404, 432, 354, 292, 295, 411, 382, 413, 406, 311, 296, 303, 548, 420, 258, '341_2', 308, 325, 363, '322_2', 330, 285, 319, 294, '279_2', 316, '295_2', 341, 346, 344, 338, '_422', 343, 322, 381, '329_2', 309, 419, 469, 403, 301, 329, 448, 537, 339, 326, 481, 509, 520, 353, 582, 589, 555, 503, 234, 498, 248, 331, 290, 276, 618, 292, 295, 411, 382, 413, 406, 311, 296, 303, 548, 420, 409, 298, 404, 354, 448, 498, 503, 520, 537, 555, 582, 588, 589, 542, 600, 602, 234, '279_2', 285, 294, '295_2', 301, 308, 309, 573, 319, 322, '322_2', 325, 326, 329, '329_2', 591, 338, 339, 341, '341_2', 343, 344, 346, 353, 363, 364, 370, 598, 403, 419, 434, 292, 295, 411, 413, 406, 311, 296, 303, '341_2', 308, 325, 363, '322_2', 330, 285, 319, 294, '279_2', 316, '295_2', 341, 346, 344, 338, 343, 322, 381, '329_2', 309, 419, 434, 403, 301, 329, '468a', 537, 339, 326, 364, 370, 520, 353, 591, 582, 602, 600, 555, 503, 234, 498, 276, 618, 262, 432, 354, 262, 279, 279, 298, 404]
    uniquekey = [str(s) for s in uniquekey]
    sampleid = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 20, 46, 42, 40, 36, 41, 45, 18, 44, 37, 31, 30, 50, 34, 26, 33, 17, 47, 24, 28, 21, 48, 29, 49, 19, 35, 39, 23, 27, 38, 22, 32, 16, 25, 43, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 335, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 343, 113, 114, 281, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 282, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 152, 169, 170, 171, 355, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 112, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 273, 217, 395, 219, 220, 168, 222, 223, 224, 225, 226, 216, 228, 229, 230, 231, 232, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 172, 274, 275, 276, 277, 278, 279, 280, 221, 227, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 311, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 187, 324, 325, 327, 328, 329, 330, 331, 332, 333, 334, 97, 336, 337, 338, 339, 340, 341, 342, 323, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 115, 356, 357, 358, 359, 360, 361, 363, 364, 365, 366, 367, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 218, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 407, 408, 409, 410, 411, 413, 414, 416, 419, 420, 421, 422, 423, 424, 425]
    board_board_length_mm = [494, 494, 494, 494, 494, 494, 494, 494, 494, 332, 332, 332, 332, 332, 332, 288, 755, 755, 587, 587, 755, 755, 288, 755, 587, 755, 755, 755, 587, 755, 359, 288, 755, 755, 755, 288, 755, 755, 755, 288, 587, 587, 288, 755, 587, 288, 359, 288, 755, 755, 335, 335, 335, 335, 335, 335, 335, 335, 335, 335, 335, 335, 325, 325, 325, 325, 325, 325, 325, 325, 325, 325, 325, 325, 325, 325, 325, 325, 325, 325, 325, 325, 325, 325, 325, 325, 325, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    assert len(sampleid) == len(uniquekey) == len(board_board_length_mm), 'key length lists did not match'



def getlookups(fname):
    '''(str, str, str) -> str, str, int
    Get some lookup values to create
    an SQLsample_length record.

    Returns:
        sampleid, uniquekey, board_board_length_mm
    '''
    assert isinstance(fname, str)

    s = fname.replace('r', '')
    s = s.replace('_FISHUND', '')
    s = s.replace('_UND', '')
    s = s.replace('.jpg', '')

    #uniquekey not unique, but should be ok just for this specific task
    if not s in BassSamples.uniquekey:
        return None, None, None

    uniquekey = BassSamples.uniquekey.index(s)
    sampleid = BassSamples.sampleid[BassSamples.uniquekey.index(s)]
    board_board_length_mm = BassSamples.board_board_length_mm[BassSamples.uniquekey.index(s)]
    return sampleid, uniquekey, board_board_length_mm


def distance_to_camera(knownWidth, focalLength, perWidth):
    '''compute and return the distance from the maker to the camera'''
    return (knownWidth * focalLength) / perWidth


def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__)
    cmdline.add_argument('folder', help='Folder containing the images and vgg file vgg_landmarks.json')
    args = cmdline.parse_args()
    vgg.SILENT = True

    folder = path.normpath(args.folder)
    assert iolib.folder_exists(folder), 'Folder %s not found' % folder
    vgg_file = path.normpath(path.join(folder, VGGFILE))
    out_file = path.normpath(path.join(folder, OUTFILE))
    print('Opened vgg file %s' % vgg_file)

    vgg.load_json(vgg_file)
    PP = PrintProgress(sum([1 for x in vgg.imagesGenerator()]), init_msg='\nProcessing...')

    results = []
    for Img in vgg.imagesGenerator(skip_imghdr_check=True):
        PP.increment()
        assert isinstance(Img, vgg.Image)

        _, fname, _ = get_file_parts(Img.filepath)
        sampleid, uniquekey, board_board_length_mm = getlookups(fname)
        if sampleid is None:
            continue

        pts = []
        for vggReg in Img.roi_generator(shape_type='point'):
            assert isinstance(vggReg, vgg.Region)
            pts.append(Point2D(vggReg.x, vggReg.y))

        if not pts or len(pts) != 2:
            continue

        img = getimg(Img.filepath)
        if img is None:
            raise ValueError('Could not read image %s' % Img.filepath)

        px_length = abs(pts[0].distance(pts[1]).evalf())

        #d_lens_sensor this is inaccurate
        d_lens_sensor = BassSamples.focal_distance * EXPECTED_LENGTH * img.shape[1] / px_length * CMOS_X

        results.append([sampleid, board_board_length_mm, d_lens_sensor])

    print('Saving CSV data ...')
    writecsv(out_file, results, inner_as_rows=False)



if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
