# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import
'''
Sharpen jpg images according to how blurred they are in the current set
of all images in the folder

The output folder must be empty
Example:
sharpen.py "C:/temp/image" "C:/temp/images/sharpened"
'''
import argparse
import os.path as path

import cv2

from opencvlib.view import show
import funclib.iolib as iolib
#import opencvlib.roi as roi
import opencvlib.imgpipes.generators as gen
from opencvlib.imgpipes.generators import FromPaths
import opencvlib.transforms as transforms
from opencvlib.info import ImageInfo as info

PP = iolib.PrintProgress()

def main():
    '''
    Sharpen jpg images according to the total blurriness of all
    images in the folder

    Example:
    sharpen.py "C:/temp/image" "C:/temp/images/sharpened"
    '''

    cmdline = argparse.ArgumentParser(description='Sharpen jpg images according to the total blurriness of all '
                                       'images in the folder and save them the specified folder\n\n'
                                      'Example:\n'
                                      'sharpen.py "C:/temp/image" "C:/temp/images/sharpened"'
                                      )
    cmdline.add_argument('source_folder', help='The folder containing the images to sharpen')
    cmdline.add_argument('output_folder', help='The folder to save the sharpened images to')
    args = cmdline.parse_args()



    src = path.normpath(args.source_folder)
    out = path.normpath(args.output_folder)
    assert src.lower() != out.lower(), 'The source and output folders must be different.'
    assert not iolib.folder_has_files(out), 'Folder "%s" contains files. The directory must be empty.' % out
    maxsharp = None; minsharp = None
    sharps = []
    FP = FromPaths(src, wildcards=['*.jpg'])
    for img, imgpath, _  in FP.generate():
        sharps.append(info.sharpval(img)) #high value is sharper, low value is more blury
        maxsharp = sharps[-1] if maxsharp is None or sharps[-1] > maxsharp else maxsharp
        minsharp = sharps[-1] if minsharp is None or sharps[-1] < minsharp else minsharp
        if maxsharp == sharps[-1]:
            maxsharpimg = imgpath
        if minsharp == sharps[-1]:
            minsharpimg = imgpath

    if maxsharpimg and maxsharp:
        print('Sharpest image was %s at %s\n' % (maxsharpimg, int(maxsharp)))
        print('Blurriest image was %s at %s\n' % (minsharpimg, int(minsharp)))

    PP.max = len(sharps)
    skipped = 0; processed = 0

    normalise = lambda x: 1 + ((((x - minsharp) / (maxsharp - minsharp)) - 0.5)*-1)   #scale between 0.5 and 1.5,
    vs = []
    for img, imgpath, _ in FP.generate():
        scale = normalise(info.sharpval(img))
        vs.append(scale)
        #img = transforms.equalize_adapthist(img)
        img = transforms.sharpen_unsharpmask(img, (5, 5), 5/255, scale)
        s = path.normpath(out + '/usm' + iolib.get_file_parts2(imgpath)[1])
        cv2.imwrite(s, img)
        PP.increment()
        processed += 1
    #print(vs)
    print('\n%s of %s images sharpened. %s images skipped.\n' % (processed, PP.max, skipped))



if __name__ == "__main__":
    main()
