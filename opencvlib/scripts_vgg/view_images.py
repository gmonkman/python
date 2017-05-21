# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''View images
'''
import argparse
import os.path as path

import opencvlib.imgpipes.generators as G
from opencvlib.common import show
import funclib.iolib as iolib


def main():
    '''
    Copies files matching the tags kwargs to
    the subfolder where the image has no set.

    The -r flag will only copy images without any ROIs defined in the VGG JSON file.

    Example:
    view_images.py part:head "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/bass-angler.json"
    '''

    cmdline = argparse.ArgumentParser(description='View image regions in a vgg.json file'
                                      'Space advances to the next region, pressing n will be recorded '
                                      'in an output text file.\n\n'
                                      'Example:\n'
                                      'view_images.py -part whole "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler"'
                                      )
    cmdline.add_argument('-part', '--part', help='The region part eg. head.', required=True)
    cmdline.add_argument('vggfolder', help='VGG JSON file to manipulate')
    args = cmdline.parse_args()


    fld = path.normpath(args.vggfolder)
    vggsp = G.VGGSearchParams(fld, parts=[args.part])

    cnt = 1     
    out = []
    for img, f, dummy in G.VGGRegions(None, vggsp):
        k, title = show(img)
        if k == 110: #n
            out.append(f)
    iolib.write_to_file(out)



if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
