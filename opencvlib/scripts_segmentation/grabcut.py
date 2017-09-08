#pylint: skip-file

'''
===============================================================================
Interactive Image Segmentation using GrabCut algorithm.

This sample shows interactive image segmentation using grabcut algorithm.

USAGE:
    python grabcut.py <filename>

README FIRST:
    Two windows will show up, one for input and one for output.

    At first, in input window, draw a rectangle around the object using
mouse right button. Then press 'n' to segment the object (once or a few times)
For any finer touch-ups, you can press any of the keys below and draw lines on
the areas you want. Then again press 'n' for updating the output.

Key '0' - To select areas of sure background
Key '1' - To select areas of sure foreground
Key '2' - To select areas of probable background
Key '3' - To select areas of probable foreground

Key 'n' - To update the segmentation
Key 'r' - To reset the setup
Key 's' - To save the results
===============================================================================
'''


import os.path as _path
import argparse

import numpy as np
import cv2 as _cv2
import sys

BLUE = [255, 0, 0]        # rectangle color
RED = [0, 0, 255]         # PR BG
GREEN = [0, 255, 0]       # PR FG
BLACK = [0, 0, 0]         # sure BG
WHITE = [255, 255, 255]   # sure FG

DRAW_BG = {'color': BLACK, 'val': 0}
DRAW_FG = {'color': WHITE, 'val': 1}
DRAW_PR_FG = {'color': GREEN, 'val': 3}
DRAW_PR_BG = {'color': RED, 'val': 2}


# setting up flags
RECT = (0, 0, 1, 1)
DRAWING = False         # flag for drawing curves
RECTANGLE = False       # flag for drawing rect
RECT_OVER = False       # flag to check if rect drawn
RECT_OR_MASK = 100      # flag for selecting rect or mask mode
VALUE = DRAW_FG         # drawing initialized to FG
THICKNESS = 3           # brush thickness

EXT = '.seg'


def onmouse(event, x, y, flags, param):
    global img, img2, DRAWING, VALUE, mask, RECTANGLE, RECT, RECT_OR_MASK, ix, iy, RECT_OVER

    # Draw Rectangle
    if event == _cv2.EVENT_RBUTTONDOWN:
        RECTANGLE = True
        ix, iy = x, y

    elif event == _cv2.EVENT_MOUSEMOVE:
        if RECTANGLE == True:
            img = img2.copy()
            _cv2.rectangle(img, (ix, iy), (x, y), BLUE, 2)
            RECT = (min(ix, x), min(iy, y), abs(ix - x), abs(iy - y))
            RECT_OR_MASK = 0

    elif event == _cv2.EVENT_RBUTTONUP:
        RECTANGLE = False
        RECT_OVER = True
        _cv2.rectangle(img, (ix, iy), (x, y), BLUE, 2)
        RECT = (min(ix, x), min(iy, y), abs(ix - x), abs(iy - y))
        RECT_OR_MASK = 0
        print(" Now press the key 'n' a few times until no further change \n")

    # draw touchup curves

    if event == _cv2.EVENT_LBUTTONDOWN:
        if RECT_OVER == False:
            print("first draw rectangle \n")
        else:
            DRAWING = True
            _cv2.circle(img, (x, y), THICKNESS, VALUE['color'], -1)
            _cv2.circle(mask, (x, y), THICKNESS, VALUE['val'], -1)

    elif event == _cv2.EVENT_MOUSEMOVE:
        if DRAWING == True:
            _cv2.circle(img, (x, y), THICKNESS, VALUE['color'], -1)
            _cv2.circle(mask, (x, y), THICKNESS, VALUE['val'], -1)

    elif event == _cv2.EVENT_LBUTTONUP:
        if DRAWING == True:
            DRAWING = False
            _cv2.circle(img, (x, y), THICKNESS, VALUE['color'], -1)
            _cv2.circle(mask, (x, y), THICKNESS, VALUE['val'], -1)

            

if __name__ == '__main__':

    # print documentation
    print(__doc__)


    img = _cv2.imread(filename)
    img2 = img.copy()                               # a copy of original image
    mask = np.zeros(img.shape[:2], dtype=np.uint8)  # mask initialized to PR_BG
    output = np.zeros(img.shape, np.uint8)           # output image to be shown

    # input and output windowsa
    _cv2.namedWindow('output')
    _cv2.namedWindow('input')
    _cv2.setMouseCallback('input', onmouse)
    _cv2.moveWindow('input', img.shape[1] + 10, 90)

    print(" Instructions: \n")
    print(" Draw a rectangle around the object using right mouse button \n")

    while(1):

        _cv2.imshow('output', output)
        _cv2.imshow('input', img)
        k = _cv2.waitKey(1)

        # key bindings
        if k == 27:         # esc to exit
            break
        elif k == ord('0'):  # BG drawing
            print(" mark background regions with left mouse button \n")
            VALUE = DRAW_BG
        elif k == ord('1'):  # FG drawing
            print(" mark foreground regions with left mouse button \n")
            VALUE = DRAW_FG
        elif k == ord('2'):  # PR_BG drawing
            VALUE = DRAW_PR_BG
        elif k == ord('3'):  # PR_FG drawing
            VALUE = DRAW_PR_FG
        elif k == ord('s'):  # save image
            bar = np.zeros((img.shape[0], 5, 3), np.uint8)
            res = np.hstack((img2, bar, img, bar, output))
            _cv2.imwrite('grabcut_output.png', res)
            print(" Result saved as image \n")
        elif k == ord('r'):  # reset everything
            print("resetting \n")
            RECT = (0, 0, 1, 1)
            DRAWING = False
            RECTANGLE = False
            RECT_OR_MASK = 100
            RECT_OVER = False
            VALUE = DRAW_FG
            img = img2.copy()
            # mask initialized to PR_BG
            mask = np.zeros(img.shape[:2], dtype=np.uint8)
            # output image to be shown
            output = np.zeros(img.shape, np.uint8)
        elif k == ord('n'):  # segment the image
            print(""" For finer touchups, mark foreground and background after pressing keys 0-3
            and again press 'n' \n""")
            if (RECT_OR_MASK == 0):         # grabcut with rect
                bgdmodel = np.zeros((1, 65), np.float64)
                fgdmodel = np.zeros((1, 65), np.float64)
                _cv2.grabCut(img2, mask, RECT, bgdmodel,
                fgdmodel, 1, _cv2.GC_INIT_WITH_RECT)
                RECT_OR_MASK = 1
            elif RECT_OR_MASK == 1:         # grabcut with mask
                bgdmodel = np.zeros((1, 65), np.float64)
                fgdmodel = np.zeros((1, 65), np.float64)
                _cv2.grabCut(img2, mask, RECT, bgdmodel,
                            fgdmodel, 1, _cv2.GC_INIT_WITH_MASK)

        mask2 = np.where((mask == 1) + (mask == 3), 255, 0).astype('uint8')
        output = _cv2.bitwise_and(img2, img2, mask=mask2)

    _cv2.destroyAllWindows()



if __name__ == '__main__':
    cmdline = argparse.ArgumentParser(description='Run watershed segmentation and try back projection'
                                    'Example:\n'
                                    'grabcut.py "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/lobster" -l "C:/development/python/opencvlib/bin/watershedhisto"'
                                    )

    cmdline.add_argument('imgfolder', help='Folder with the images', default='')
    args = cmdline.parse_args()


    fn = args.imgfolder

    _DUMP_DIR = normpath(LOAD_FROM)


    print(__doc__)

    Ts = None

    #Ts = _transform.Transforms()
    #Ts.add(_transform.Transform(_cv2.fastNlMeansDenoisingColored,None,10,10,7,21))
    #Ts.add(_transform.Transform(_transform.equalize_adapthist)) #1 arg, the img, autoconverts to HSV
    App(fn, Ts).run()