# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import
'''Calculate length-width ratio from body caudal

'''
import os.path as path
from shutil import copyfile

import numpy as np
import statsmodels.api as sm

from funclib.statslib import stddev
import opencvlib.imgpipes.vgg as vgg
from funclib.iolib import PrintProgress
from opencvlib import geom
from opencvlib import roi


PATHS = ['C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/fujifilm/rotated/vgg_body-caudal.json',
         'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/gopro_all_undistorted/rotated/vgg_body-caudal.json',
         'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/s5690/rotated/vgg_body-caudal.json',
         'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/fujifilm/rotated/vgg_body-caudal.json',
         'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/gopro_all_undistorted/rotated/vgg_body-caudal.json',
         'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/s5690/rotated/vgg_body-caudal.json'
         ]


def main():
    '''main'''
    ratios = []
    for f in PATHS:
        vgg.SILENT = True
        print('Opened vgg file %s' % f)
        vgg.load_json(f)
        PP = PrintProgress(sum([1 for x in vgg.imagesGenerator()]), init_msg='\nProcessing points...')
        for Img in vgg.imagesGenerator():
            PP.increment()
            assert isinstance(Img, vgg.Image)
            for Reg in Img.roi_generator(shape_type='rect'):
                assert isinstance(Reg, vgg.Region)
                sides = geom.rect_side_lengths(Reg.all_points)
                ratios.append(max(sides)/min(sides))
    print('\n')
    print('mean: %0.3f,   SD: %0.3f ' % (sum(ratios)/len(ratios), stddev(ratios)))




if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
