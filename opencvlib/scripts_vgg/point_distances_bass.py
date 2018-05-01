# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import, unused-variable
'''Estimate total distances between  paired points,
optionally calculate pixel length per mm.

Uses a landmarks vgg file where numerical landmarks
have been configured.

Uses the snout landmark 20 and the tail for landmark 14
combined with the aruco marker.

The vgg file must be called vgg_landmarks.json.

Results saved to a csv file called vgg_landmark_distances.csv.

Example:
point_distances_bass.py -p Shore -c GoPro "C:/temp/fshpics"
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
from opencvlib import aruco
from opencvlib import getimg
import statistics

VGGFILE = 'vgg_landmarks.json'
CSVOUT = 'vgg_landmark_distances.csv'
ERROUT = 'vgg_landmark_distances_errors.csv'
#Fix to read in dab laser distances

class BassSamples():
    '''some hard coded stuff to help write to excel sheet
    fish_image_data_sheet.xlsm!SQLsample_length
    '''
    #indexes match for these two
    fork_to_total_ratio = 0.94424
    measured_resolution = '1280x768'
    camera = ['GoPro', 'XP30', 's5690'] #valid cameras
    platform = ['Shore', 'Charter'] #valid platforms
    pts = [20, 14] #snout and fork
    #these next 4 lists match by index. They are taken from the excel sheet fish_image_data_sheet.xlsm
    fidkey = ['CharterXP30497a', 'CharterXP30472', 'CharterXP30501', 'CharterXP30551', 'CharterXP30527', 'CharterXP30572', 'CharterXP30520', 'CharterXP30409', 'CharterXP30458', 'ShoreGoPro316', 'CharterXP30469', 'CharterXP30583', 'CharterXP30542', 'CharterXP30533', 'CharterXP30497', 'CharterXP30509', 'CharterXP30510', 'CharterXP30519', 'CharterXP30482', 'CharterXP30454', 'CharterXP30427', 'CharterXP30374', 'CharterXP30375', 'CharterXP30441', 'ShoreGoPro330', 'CharterXP30394', 'CharterXP30361', 'ShoreXP30364', 'CharterXP30409a', 'CharterXP30405', 'CharterXP30358', 'CharterXP30595', 'CharterXP30424', 'CharterXP30421', 'CharterXP30468a', 'CharterXP30482a', 'CharterXP30468', 'CharterXP30433', 'CharterXP30565', 'CharterXP30459', 'CharterXP30481', 'CharterXP30478', 'CharterXP30444', 'CharterXP30510a', 'CharterXP30430', 'Charters5690509', 'Charters5690510', 'Charters5690510a', 'Charters5690510b', 'Charters5690523', 'Charters5690527', 'Charters5690533', 'Charters5690542', 'Charters5690551', 'Charters5690565', 'Charters5690572', 'Charters5690573', 'Charters5690583', 'Charters5690588', 'Charters5690591', 'Charters5690595', 'Charters5690598', 'Charters5690358', 'Charters5690361', 'ShoreXP30370', 'Charters5690375', 'Charters5690394', 'Charters5690405', 'Charters5690409', 'Charters5690409a', 'Charters5690421', 'Charters5690424', 'Charters5690425', 'Charters5690430a', 'Charters5690433', 'Charters5690441', 'Charters5690442', 'Charters5690444', 'Charters5690448', 'Charters5690454', 'Charters5690374', 'Charters5690459', 'Charters5690468', 'Charters5690468a', 'ShoreGoPro381', 'Charters5690472', 'Charters5690478', 'Charters5690481', 'Charters5690482', 'Charters5690483', 'Charters5690496', 'Charters5690497', 'Charters5690498', 'Charters5690501', 'CharterGoPro482', 'CharterGoPro523', 'CharterGoPro523a', 'CharterGoPro526', 'CharterGoPro527', 'CharterXP30425', 'CharterGoPro551', 'CharterGoPro565', 'CharterGoPro572', 'CharterGoPro583', 'CharterGoPro591', 'CharterGoPro595', 'CharterGoPro598', 'CharterGoPro358', 'CharterGoPro361', 'CharterGoPro374', 'CharterGoPro427', 'CharterGoPro375', 'CharterGoPro394', 'CharterGoPro405', 'CharterGoPro409', 'CharterGoPro409a', 'CharterGoPro421', 'CharterGoPro424', 'CharterGoPro425', 'CharterGoPro430', 'CharterGoPro433', 'CharterGoPro441', 'CharterGoPro441a', 'CharterGoPro442', 'CharterGoPro444', 'CharterGoPro448', 'CharterGoPro454', 'CharterGoPro458', 'ShoreXP30434', 'CharterGoPro468', 'Shores5690448', 'CharterGoPro472', 'CharterGoPro478', 'Charters5690458', 'CharterGoPro482a', 'CharterGoPro496', 'CharterGoPro497', 'CharterGoPro497a', 'CharterGoPro501', 'CharterGoPro459', 'CharterGoPro510', 'CharterGoPro510a', 'CharterGoPro510b', 'CharterGoPro519', 'ShoreXP30298', 'ShoreXP30279', 'ShoreXP30404', 'ShoreXP30432', 'ShoreXP30354', 'ShoreXP30292', 'ShoreXP30295', 'ShoreXP30411', 'ShoreXP30382', 'ShoreXP30413', 'ShoreXP30406', 'ShoreXP30311', 'ShoreXP30296', 'ShoreXP30303', 'ShoreXP30548', 'ShoreXP30420', 'ShoreXP30258', 'ShoreXP30341_2', 'ShoreXP30308', 'ShoreXP30325', 'ShoreXP30363', 'ShoreXP30322_2', 'ShoreXP30330', 'ShoreXP30285', 'ShoreXP30319', 'ShoreXP30294', 'ShoreXP30279_2', 'ShoreXP30316', 'ShoreXP30295_2', 'ShoreXP30341', 'ShoreXP30346', 'ShoreXP30344', 'ShoreXP30338', 'ShoreXP30_422', 'ShoreXP30343', 'ShoreXP30322', 'ShoreXP30381', 'ShoreXP30329_2', 'ShoreXP30309', 'ShoreXP30419', 'Charters5690469', 'ShoreXP30403', 'ShoreXP30301', 'ShoreXP30329', 'ShoreXP30448', 'ShoreXP30537', 'ShoreXP30339', 'ShoreXP30326', 'CharterGoPro481', 'CharterGoPro509', 'ShoreXP30520', 'ShoreXP30353', 'ShoreXP30582', 'ShoreXP30589', 'ShoreXP30555', 'ShoreXP30503', 'ShoreXP30234', 'ShoreXP30498', 'ShoreXP30248', 'ShoreXP30331', 'ShoreXP30290', 'ShoreXP30276', 'ShoreXP30618', 'ShoreGoPro292', 'ShoreGoPro295', 'ShoreGoPro411', 'ShoreGoPro382', 'ShoreGoPro413', 'ShoreGoPro406', 'ShoreGoPro311', 'ShoreGoPro296', 'ShoreGoPro303', 'ShoreGoPro548', 'ShoreGoPro420', 'ShoreGoPro409', 'ShoreGoPro298', 'ShoreGoPro404', 'ShoreGoPro432', 'ShoreGoPro354', 'ShoreGoPro448', 'ShoreGoPro498', 'ShoreGoPro503', 'ShoreGoPro520', 'ShoreGoPro537', 'ShoreGoPro555', 'ShoreGoPro582', 'ShoreGoPro588', 'ShoreGoPro589', 'CharterGoPro542', 'ShoreGoPro600', 'ShoreGoPro602', 'ShoreGoPro234', 'ShoreGoPro279_2', 'ShoreGoPro285', 'ShoreGoPro294', 'ShoreGoPro295_2', 'ShoreGoPro301', 'ShoreGoPro308', 'ShoreGoPro309', 'CharterXP30573', 'ShoreGoPro319', 'ShoreGoPro322', 'ShoreGoPro322_2', 'ShoreGoPro325', 'ShoreGoPro326', 'ShoreGoPro329', 'ShoreGoPro329_2', 'ShoreGoPro591', 'ShoreGoPro338', 'ShoreGoPro339', 'ShoreGoPro341', 'ShoreGoPro341_2', 'ShoreGoPro343', 'ShoreGoPro344', 'ShoreGoPro346', 'ShoreGoPro353', 'ShoreGoPro363', 'ShoreGoPro364', 'ShoreGoPro370', 'CharterXP30598', 'ShoreGoPro403', 'ShoreGoPro419', 'ShoreGoPro434', 'Shores5690292', 'Shores5690295', 'Shores5690411', 'Shores5690413', 'Shores5690406', 'Shores5690311', 'Shores5690296', 'Shores5690303', 'Shores5690341_2', 'Shores5690308', 'Shores5690325', 'Shores5690363', 'Shores5690322_2', 'Shores5690330', 'Shores5690285', 'Shores5690319', 'Shores5690294', 'Shores5690279_2', 'Shores5690316', 'Shores5690295_2', 'Shores5690341', 'Shores5690346', 'Shores5690344', 'Shores5690338', 'Shores5690343', 'Shores5690322', 'Shores5690381', 'Shores5690329_2', 'Shores5690309', 'Shores5690419', 'Shores5690434', 'Shores5690403', 'Shores5690301', 'Shores5690329', 'CharterGoPro468a', 'Shores5690537', 'Shores5690339', 'Shores5690326', 'Shores5690364', 'Shores5690370', 'Shores5690520', 'Shores5690353', 'Shores5690591', 'Shores5690582', 'Shores5690602', 'Shores5690600', 'Shores5690555', 'Shores5690503', 'Shores5690234', 'Shores5690498', 'Shores5690276', 'Shores5690618', 'Shores5690262', 'Shores5690432', 'Shores5690354', 'ShoreGoPro262', 'ShoreGoPro279', 'Shores5690279', 'Shores5690298', 'Shores5690404']
    sampleid = [88, 89, 90, 91, 92, 93, 94, 95, 96, 335, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 343, 113, 114, 281, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 282, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 152, 169, 170, 171, 355, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 112, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 273, 217, 395, 219, 220, 168, 222, 223, 224, 225, 226, 216, 228, 229, 230, 231, 232, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 172, 274, 275, 276, 277, 278, 279, 280, 221, 227, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 187, 324, 325, 327, 328, 329, 330, 331, 332, 333, 334, 97, 336, 337, 338, 339, 340, 341, 342, 323, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 115, 356, 357, 358, 359, 360, 361, 363, 364, 365, 366, 367, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 218, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 407, 408, 409, 410, 411, 413, 414, 416, 419, 420, 421, 422, 423, 424, 425]
    uniquekey = ['497a', 472, 501, 551, 527, 572, 520, 409, 458, 316, 469, 583, 542, 533, 497, 509, 510, 519, 482, 454, 427, 374, 375, 441, 330, 394, 361, 364, '409a', 405, 358, 595, 424, 421, '468a', '482a', 468, 433, 565, 459, 481, 478, 444, '510a', 430, 509, 510, '510a', '510b', 523, 527, 533, 542, 551, 565, 572, 573, 583, 588, 591, 595, 598, 358, 361, 370, 375, 394, 405, 409, '409a', 421, 424, 425, '430a', 433, 441, 442, 444, 448, 454, 374, 459, 468, '468a', 381, 472, 478, 481, 482, 483, 496, 497, 498, 501, 482, 523, '523a', 526, 527, 425, 551, 565, 572, 583, 591, 595, 598, 358, 361, 374, 427, 375, 394, 405, 409, '409a', 421, 424, 425, 430, 433, 441, '441a', 442, 444, 448, 454, 458, 434, 468, 448, 472, 478, 458, '482a', 496, 497, '497a', 501, 459, 510, '510a', '510b', 519, 298, 279, 404, 432, 354, 292, 295, 411, 382, 413, 406, 311, 296, 303, 548, 420, 258, '341_2', 308, 325, 363, '322_2', 330, 285, 319, 294, '279_2', 316, '295_2', 341, 346, 344, 338, '_422', 343, 322, 381, '329_2', 309, 419, 469, 403, 301, 329, 448, 537, 339, 326, 481, 509, 520, 353, 582, 589, 555, 503, 234, 498, 248, 331, 290, 276, 618, 292, 295, 411, 382, 413, 406, 311, 296, 303, 548, 420, 409, 298, 404, 432, 354, 448, 498, 503, 520, 537, 555, 582, 588, 589, 542, 600, 602, 234, '279_2', 285, 294, '295_2', 301, 308, 309, 573, 319, 322, '322_2', 325, 326, 329, '329_2', 591, 338, 339, 341, '341_2', 343, 344, 346, 353, 363, 364, 370, 598, 403, 419, 434, 292, 295, 411, 413, 406, 311, 296, 303, '341_2', 308, 325, 363, '322_2', 330, 285, 319, 294, '279_2', 316, '295_2', 341, 346, 344, 338, 343, 322, 381, '329_2', 309, 419, 434, 403, 301, 329, '468a', 537, 339, 326, 364, 370, 520, 353, 591, 582, 602, 600, 555, 503, 234, 498, 276, 618, 262, 432, 354, 262, 279, 279, 298, 404]
    uniquekey = [str(s) for s in uniquekey]
    measured_resolution = ['1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1440x1080', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1440x1080', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1440x1080', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1280x960', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1280x960', '1440x1080', '1280x960', '1440x1080', '1440x1080', '1280x960', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x736', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1440x1080', '1440x1080', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1280x960', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1440x1080', '1280x960', '1440x1080', '1440x1080', '1440x1080', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1440x1080', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960', '1280x960']
    total_lengths = [497, 472, 501, 551, 527, 572, 520, 409, 458, 316, 469, 583, 542, 533, 497, 509, 510, 519, 482, 454, 427, 374, 375, 441, 330, 394, 361, 364, 409, 405, 358, 595, 424, 421, 468, 482, 468, 433, 565, 459, 481, 478, 444, 510, 430, 509, 510, 510, 510, 523, 527, 533, 542, 551, 565, 572, 573, 583, 588, 591, 595, 598, 358, 361, 370, 375, 394, 405, 409, 409, 421, 424, 425, 430, 433, 441, 442, 444, 448, 454, 374, 459, 468, 468, 381, 472, 478, 481, 482, 483, 496, 497, 498, 501, 482, 523, 523, 526, 527, 425, 551, 565, 572, 583, 591, 595, 598, 358, 361, 374, 427, 375, 394, 405, 409, 409, 421, 424, 425, 430, 433, 441, 441, 442, 444, 448, 454, 458, 434, 468, 448, 472, 478, 458, 482, 496, 497, 497, 501, 459, 510, 510, 510, 519, 298, 279, 404, 432, 354, 292, 295, 411, 382, 413, 406, 311, 296, 303, 548, 420, 258, 341, 308, 325, 363, 322, 330, 285, 319, 294, 279, 316, 295, 341, 346, 344, 338, 422, 343, 322, 381, 329, 309, 419, 469, 403, 301, 329, 448, 537, 339, 326, 481, 509, 520, 353, 582, 589, 555, 503, 234, 498, 248, 331, 290, 276, 618, 292, 295, 411, 382, 413, 406, 311, 296, 303, 548, 420, 409, 298, 404, 432, 354, 448, 498, 503, 520, 537, 555, 582, 588, 589, 542, 600, 602, 234, 279, 285, 294, 295, 301, 308, 309, 573, 319, 322, 322, 325, 326, 329, 329, 591, 338, 339, 341, 341, 343, 344, 346, 353, 363, 364, 370, 598, 403, 419, 434, 292, 295, 411, 413, 406, 311, 296, 303, 341, 308, 325, 363, 322, 330, 285, 319, 294, 279, 316, 295, 341, 346, 344, 338, 343, 322, 381, 329, 309, 419, 434, 403, 301, 329, 468, 537, 339, 326, 364, 370, 520, 353, 591, 582, 602, 600, 555, 503, 234, 498, 276, 618, 262, 432, 354, 262, 279, 279, 298, 404] #manually measured length
    assert len(fidkey) == len(sampleid) == len(uniquekey) == len(total_lengths), 'key length lists did not match'


def tl_from_fl(fl):
    '''(float)->float
    Get total length from
    fork length
    '''
    return fl / BassSamples.fork_to_total_ratio


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
        return 'Measure "%s" [%s,%s] mm=%s' % (
                            self.name,
                            str(tuple(self._pt1) if isinstance(self._pt1, Point2D) else ''),
                            str(tuple(self._pt2) if isinstance(self._pt2, Point2D) else ''),
                            str(self.real_length)
                        )

    @property
    def lengths_mm(self):
        '''() -> float, float
        Return the fork length and tail length (in
        that order) in mm.
        '''
        return self._length_px * self._px_len_mm, tl_from_fl(self._length_px * self._px_len_mm)


def getlookups(fname, platform, camera):
    '''(str, str, str) -> str, str, str, int
    Get some lookup values to create
    an SQLsample_length record.

    Returns:
        sampleid, uniquekey, measured_resolution, total length (mm)
    '''
    assert platform in BassSamples.platform, 'platform %s not valid' % platform
    assert camera in BassSamples.camera, 'camera %s invald' % camera
    assert isinstance(fname, str)

    s = fname.replace('r', '')
    s = s.replace('_FISHUND', '')
    s = s.replace('_UND', '')
    s = s.replace('.jpg', '')

    assert s in BassSamples.uniquekey, 'The key "%s" extracted from the filename not valid' % s

    fidkey = '%s%s%s' % (platform, camera, s)

    sampleid = BassSamples.sampleid[BassSamples.fidkey.index(fidkey)]
    uniquekey = BassSamples.uniquekey[BassSamples.fidkey.index(fidkey)]
    measured_resolution = BassSamples.measured_resolution[BassSamples.fidkey.index(fidkey)]
    total_length = BassSamples.total_lengths[BassSamples.fidkey.index(fidkey)]
    return sampleid, uniquekey, measured_resolution, total_length



def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__)
    cmdline.add_argument('-p', '--platform', help='Platform, must be in [Shore, Charter]')
    cmdline.add_argument('-c', '--camera', help='Camera, must be in [GoPro, s5690, XP30]')
    cmdline.add_argument('folder', help='Folder containing the images and vgg file vgg_landmarks.json')
    args = cmdline.parse_args()
    print('Folder: %s\nCamera: "%s"\nPlatform: "%s"' % (args.folder, args.camera, args.platform))
    vgg.SILENT = True
    assert args.platform in BassSamples.platform, 'Invalid platform "%s"' % args.platform
    assert args.camera in BassSamples.camera, 'Invalid camera "%s"' % args.camera

    folder = path.normpath(args.folder)
    assert iolib.folder_exists(folder), 'Folder %s not found' % folder
    vgg_file = path.normpath(path.join(folder, VGGFILE))
    print('Opened vgg file %s' % vgg_file)
    out_file = path.normpath(path.join(folder, CSVOUT))
    out_errs_file = path.normpath(path.join(folder, ERROUT))

    outdata = [['sample_lengthid', 'sampleid', 'estimate_mm', 'ref_length_type', 'ref_length_mm', 'measured_resolution', 'lens_correction_mm', 'comment', 'unique_code']]

    vgg.load_json(vgg_file)
    PP = PrintProgress(sum([1 for x in vgg.imagesGenerator()]), init_msg='\nProcessing...')

    missing_points = []
    multi_markers = []
    no_markers = []
    big_error = []
    errors = []
    for Img in vgg.imagesGenerator(skip_imghdr_check=True):
        PP.increment()
        assert isinstance(Img, vgg.Image)

        img = getimg(Img.filepath)
        if img is None:
            raise ValueError('Could not read image %s' % Img.filepath)

        _, fname, _ = get_file_parts(Img.filepath)
        sampleid, unique_code, measured_resolution, total_length = getlookups(fname, args.platform, args.camera)

        D = aruco.Detected(img)
        using_expected = False
        if Img.filename in ['r405_FISHUND.jpg', 'r409a_FISHUND.jpg', 'r510a_FISHUND.jpg', 'r420_UND.jpg', 'r482_UND.jpg', 'r405_UND.jpg', 'r413_FISHUND.jpg', 'r432_FISHUND.jpg', 'r406_FISHUND.jpg']:
            D.detect(expected=aruco.eMarkerID.Sz30)
            using_expected = True
        elif Img.filename in ['r582_UND.jpg', 'r548_FISHUND.jpg', 'r582_FISHUND.jpg']:
            D.detect(expected=aruco.eMarkerID.Sz30_flip)
            using_expected = True
        elif Img.filename in ['r618_UND.jpg']:
            D.detect(expected=aruco.eMarkerID.Sz50)
            using_expected = True
        elif Img.filename in ['r258_UND.jpg', 'r370_FISHUND.jpg', 'r370_UND.jpg']:
            D.detect(expected=aruco.eMarkerID.Sz25)
            using_expected = True
        else:
            D.detect()

        if D.Markers:
            if len(D.Markers) > 1:
                multi_markers.append(['%s [sampleid:%s] had multiple markers' % (Img.filename, sampleid)])
                continue
            Marker = D.Markers[0]
            assert isinstance(Marker, aruco.Marker)
            ref_length_type = Marker.markerid.name
            ref_length_mm = Marker.side_length_mm
        else:
            if using_expected:
                no_markers.append(['%s [sampleid:%s], Expected Aruco marker not found' % (Img.filename, sampleid)])
            else:
                no_markers.append(['%s [sampleid:%s], found no Aruco markers' % (Img.filename, sampleid)])
            continue

        pt20 = None; pt14 = None
        for vggReg in Img.roi_generator(shape_type='point'):
            assert isinstance(vggReg, vgg.Region)
            lbl = int(vggReg.region_json_key) + 1 if vggReg.region_attr.get('pts', '') == '' else int(vggReg.region_attr['pts'])
            if lbl == 20:
                pt20 = Point2D(vggReg.x, vggReg.y)
            elif lbl == 14:
                pt14 = Point2D(vggReg.x, vggReg.y)

        if pt20 is None or pt14 is None:
            missing_points.append(['%s [sampleid:%s] no point 20 or point 14' % (Img.filename, sampleid)])
            continue

        BM = BassMeasure('fork length', pt20, pt14, Marker.px_length_mm)

        estimate_mm = '' #undistored image length - not relevant for FIDs
        fl, tl = BM.lengths_mm
        lens_correction_mm = tl #relevant, this is the only measure we care about for Bass FID

        err = 100 * (lens_correction_mm - total_length)/total_length
        errors.append(err)
        if not -18 < err < 1: #we expect it to be an underestimate
            big_error.append(['%s [sampleid:%s] large error %.2f (Estimated TL:%.2f)' % (Img.filename, sampleid, err, lens_correction_mm)])

        outdata.append(['',
            sampleid,
            estimate_mm,
            ref_length_type,
            ref_length_mm,
            measured_resolution,
            lens_correction_mm,
            'Autocalculated in point_distances_bass.py. Tail length estimated from fork length.',
            unique_code]
            )


    print('Saving CSV data ...')
    iolib.writecsv(out_file, outdata, inner_as_rows=False)
    iolib.folder_open(path.normpath(folder))

    all_errs = []
    all_errs.extend(missing_points)
    all_errs.extend(multi_markers)
    all_errs.extend(no_markers)
    all_errs.extend(big_error)
    _ = [print(x[0]) for x in all_errs]

    if all_errs:
        print('Errors written to %s' % out_errs_file)
        iolib.writecsv(out_errs_file, all_errs, inner_as_rows=False)
    print('\nMean error: %.2f' % (sum(errors)/len(errors)))


if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
