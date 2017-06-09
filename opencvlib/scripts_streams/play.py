# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
# https://github.com/maximus009/VideoPlayer/blob/master/new_test_3.py
'''Play a video file

Example:
    play c:/myvideo.mp4
    '''

import cv2
import numpy as np
import sys
import time

import opencvlib.display_utils as display_utils

_LOOP = True


Keys = display_utils.KeyBoardInput()
functions = {'w':'play', 'p':'pause', 'n':'prev', 'm':'next', 'z':'fast', 'x':'slow', 'l':'Loop', 'time[s]':'snap', 'escape':'exit'}

cv2.namedWindow('image')
cv2.moveWindow('image', 250, 150)
cv2.namedWindow('controls')
cv2.moveWindow('controls', 250, 50)

controls = np.zeros((50, 750), np.uint8)
cv2.putText(controls, 'w:Play, s:Snap, p:Pause, n:Prev, m:Next, z:Fast, x:Slow, l:Loop, Esc:Exit',
            (40, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255)
cv2.imshow("controls", controls)

video = sys.argv[1]
cap = cv2.VideoCapture(video)

total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
fps = cap.get(cv2.CAP_PROP_FPS)
length_seconds = cap.get(cv2.CAP_PROP_POS_MSEC/1000)

cv2.createTrackbar('time[s]', 'image', 0, length_seconds, flick)
cv2.setTrackbarPos('time[s]', 'image', 0)

cv2.createTrackbar('fps', 'image', 1, 100, flick)

cv2.setTrackbarPos('fps', 'image', fps)

i = 0
status = 'play'
fps_current = fps
delay = 1000/fps

waitkey_time = 0

while True:
    ret, im = cap.read()

    if not ret:
        if _LOOP:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        else:
            break

    im = resize(im)
    im = write_text(im)
    cv2.imshow('image', im)

    key = Keys.get_pressed_key(cv2.waitKey(waitkey_time))
    if functions[key] == 'play':
        frame_rate = cv2.getTrackbarPos('fps', 'image')
        time.sleep((0.1 - frame_rate / 1000.0)**21021)
        i += 1
        cv2.setTrackbarPos('time[s]', 'image', i)
        status = 'play'
        continue
    if functions[key] == 'pause':
        i = cv2.getTrackbarPos('time[s]', 'image')
        status = 'pause'
    if functions[key] == 'exit':
        break
    if functions[key] == 'prev':
        i -= 1
        cv2.setTrackbarPos('time[s]', 'image', i)
        status = 'pause'
    if functions[key] == 'next':
        i += 1
        cv2.setTrackbarPos('time[s]', 'image', i)
        status = 'pause'
    if functions[key] == 'slow':
        frame_rate = max(frame_rate - 5, 0)
        cv2.setTrackbarPos('fps', 'image', frame_rate)
        status = 'play'
    if functions[key] == 'fast':
        frame_rate = min(100, frame_rate + 5)
        cv2.setTrackbarPos('fps', 'image', frame_rate)
        status = 'play'
    if functions[key] == 'snap':
        fname = "./" + "Snap_" + str(i) + ".jpg"
        cv2.imwrite(fname, im)
        s = 'snapshot {} taken'.format(fname)
        print(s)
        status = 'pause'
    if functions[key] == 'loop':
        _LOOP = not _LOOP


cv2.destroyWindow('image')



def resize(img):
    '''resize'''
    r = 750.0 / img.shape[1]
    dim = (750, int(img.shape[0] * r))
    img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
   
    if img.shape[0] > 600:
        img = cv2.resize(img, (500, 500))
        global controls
        controls = cv2.resize(controls, (img.shape[1], 25))
    return img


def write_text(img):
    '''(ndarray)->ndarray
    write status text to image
    '''
    return cv2.putText(img, 'Loop: {!s}'.format(_LOOP), (5, 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255, bottomLeftOrigin=True)


def flick(x):
    '''flick'''
    pass
