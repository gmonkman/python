# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''
View image regions in a vgg.json file
Space advances to the next region, pressing n will be recorded
in an output text file.

Example:
view_images.py part:head "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/bass-angler.json"
'''

import argparse
import os.path as path


import opencvlib.imgpipes.generators as G
import opencvlib.transforms as transforms
from opencvlib.view import show
import funclib.iolib as iolib
from opencvlib.display_utils import KeyBoardInput, eSpecialKeys

def main():
    print('KEYS\nn: Save filename to a text file.\nq: Quit.')
    cmdline = argparse.ArgumentParser(description=__doc__)
    cmdline.add_argument('folder', help='Folder containing the images')
    args = cmdline.parse_args()

    fld = path.normpath(args.folder)
    t1 = transforms.Transform(transforms.denoise, sigma=10)
    t2 = transforms.Transform(transforms.histeq_color)
    t3 = transforms.Transform(transforms.togreyscale)

    ts = transforms.Transforms(t1, t2, t3)
    FP = G.FromPaths(fld, '*.jpg', transforms=ts)
    for img, f, dummy in  FP.generate():
        k, dummy1 = show(img)
        if KeyBoardInput.check_pressed_key('n', k):
            out.append(f)
        elif  KeyBoardInput.check_pressed_key('q', k):
            return

    iolib.write_to_file(out)



if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
