#pylint: skip-file

'''image alignment attempt'''
import argparse
import cv2
import pyelastix

import numpy as np
from opencvlib.imgpipes.generators import FromPaths
from opencvlib.view import show, eSpecialKeys, KeyBoardInput
from opencvlib.transforms import toFloat, eCvt
from opencvlib.common import draw_grid



def main():
    #cmdline = argparse.ArgumentParser(description=__doc__)
    #cmdline.add_argument('-m', '--mode', help='Action for handling file naming clashes. Valid modes are: "overwrite", "halt", "skip", "rename", "req_new_dir"', required=True)
    #cmdline.add_argument('-p', '--prefix', help='File prefix to append to the outputted filename', default='')
    #cmdline.add_argument('-g', '--grow', help='Grow/shrink roi by this factor', default='1.0')
    #cmdline.add_argument('source_folder', help='The folder containing the images and vgg file')
    #cmdline.add_argument('output_folder', help='The folder to save the ROIs to')
    #cmdline.add_argument('vgg_file_name', help='The filename of the vgg file, must be in source folder')
    #args = cmdline.parse_args()

    pth = r'C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\train\candidate_fid\resized'

    params = pyelastix.get_default_params(type='RIGID')
    assert isinstance(params, pyelastix.Parameters)
    params.MaximumNumberOfIterations = 100
    params.FinalGridSpacingInVoxels = 10
    params.NumberOfResolutions = 3
    params.ResultImageFormat = 'mhd'
    #params.ResultImagePixelType = 'short'
    #params.FixedInternalImagePixelType = "short"
    #params.MovingInternalImagePixelType = "short"
    #params.FixedImageDimension = 2
    #params.MovingImageDimension = 2

    stdImg = cv2.imread('C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/train/candidate_fid/test/standard.jpg')
    stdImg = stdImg.astype('float')

    print('Press "q" to quit.')
    FP = FromPaths(r'C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\train\candidate_fid\test', wildcards='*.jpg')
    for Img, _, _ in FP.generate():
        Img = Img.astype(np.float)

        imgout = np.zeros(stdImg.shape, dtype=np.float)

        for i in range(3):
            imgout[:, :, i], _ = pyelastix.register(Img[:, :, i], stdImg[:, :, i], params)
            imgout[:, :, i] = (255 * ((imgout[:, :, i] - imgout[:, :, i].min()) / (imgout[:, :, i].max() - imgout[:, :, i].min()))).astype('uint8')

        draw_grid(stdImg)
        draw_grid(Img)
        draw_grid(imgout)

        if KeyBoardInput.check_pressed_key('q', show([stdImg, Img, imgout])):
            return


if __name__ == "__main__":
    main()
    exit()
