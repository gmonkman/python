# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import
'''View images
'''
import argparse
import os.path as path


import opencvlib.imgpipes.generators as G
from opencvlib.imgpipes import transforms
from opencvlib.view import show
from opencvlib import features
import funclib.iolib as iolib

#Bass
#view_sift.py -part head -spp bass "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/vgg.json"

#Lobsters
#view_sift.py -part cephalothorax -spp lobster "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/lobster"

def main():
    '''
    Copies files matching the tags kwargs to
    the subfolder where the image has no set.

    The -r flag will only copy images without any ROIs defined in the VGG JSON file.

    Example:
    view_sift.py -part head "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/vgg.json"
    '''

    cmdline = argparse.ArgumentParser(description='View keypoints in a vgg.json file'
                                      'Space advances to the next region, pressing n will be recorded '
                                      'in an output text file.\n\n'
                                      'Example:\n'
                                      'view_sift -part head -spp bass "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/vgg.json"'
                                      )
    cmdline.add_argument('-part', '--part', help='The region part eg. head.', required=True)
    cmdline.add_argument('-spp', '--spp', help='The species.', required=True)
    cmdline.add_argument('vggfolder', help='VGG JSON file to manipulate')
    args = cmdline.parse_args()


    T = None
    F = None

    fld = path.normpath(args.vggfolder)
    fld = path.normpath(fld)
    vggsp = G.VGGSearchParams(fld, parts=[args.part], species=[args.spp])

    #t1 = transforms.Transform(transforms.togreyscale)
    t2 = transforms.Transform(transforms.equalize_adapthist)
    T = transforms.Transforms(None, t2)


    out = []
    reg = G.VGGRegions(None, vggsp, transforms=T, filters=F)
    
    for img, imgpath, dummy in reg.generate():
        features.SILENT = True
        #D = features.skHOGDetector()
        
        D = features.OpenCV_SIFT()
        #D = features.OpenCV_ORB()
        D(img, imgpath, extract_now=True)
        D.view(show=True)
    
    iolib.write_to_file(out)



if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
