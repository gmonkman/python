# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''make descriptors for lobster'''
import argparse as _ap
#import cv2

import opencvlib.script_objdetect.config as cfg
import opencvlib.transforms as transforms
import opencvlib.imgpipes.generators as G

import opencvlib.features as features


if __name__ == "__main__":
    # Parse the command line arguments
    cmdline = _ap.ArgumentParser(description='Write lobster descriptors.'
                                    'Photo path (containing vgg.json) and output paths are set in make_lobster_descriptors.ini'
                                    'Example:\n'
                                    'make_lobster_descriptors.py -part whole -spp lobster'
                                    )
    cmdline.add_argument('-part', '--part', help='The region part eg. head.', required=True)
    cmdline.add_argument('-spp', '--spp', help='The species.', required=True)
    args = cmdline.parse_args()
    

    vggsp = G.VGGSearchParams(cfg.MakeLobsterDescriptors.vgg_dir, parts=[args.part], species=[args.spp])
    #t1 = transforms.Transform(transforms.togreyscale)
    t2 = transforms.Transform(transforms.equalize_adapthist)
    T = transforms.Transforms(None, t2)
    RegionsG = G.VGGRegions(None, vggsp, transforms=T)

    #D = features.skHOGDetector(cfg.MakeLobsterDescriptors.output_dir)
    D = features.OpenCV_HOG(cfg.MakeLobsterDescriptors.output_dir)
    for img, f, dummy2 in RegionsG.generate():
        D(img, f, load_keypoint_visual=True)
        D.extract_descriptors()
        D.view(show=True)
        D.write()
