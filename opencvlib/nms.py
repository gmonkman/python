# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
#https://www.pyimagesearch.com/2015/02/16/faster-non-maximum-suppression-python/
#by Adrian Rosebrook, from Malisiewicz et al.
'''non-max suppression
'''
import numpy as np



def nms_fast(boxes, overlapThresh=0.5):
    '''(ndarray, float) -> ndarray
    boxes: x-top-left, y-top-left, x-bottom-right, y-bottom right

    overlapThresh:
        Ignore boxes with IoU greater than overlapThresh. Typical values between 0.3 to 0.5

    Example:
    >>>
    '''
    if len(boxes) == 0:
        return []

    boxes = boxes.astype("float")
    pick = []

    # grab the coordinates of the bounding boxes
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]
    #if boxes.shape[1] > 4:
     #   extra_cols = boxes[:,4:]

    # compute the area of the bounding boxes and sort the bounding
    # boxes by the bottom-right y-coordinate of the bounding box
    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(y2)

    # keep looping while some indexes still remain in the indexes
    # list
    while len(idxs) > 0:
        # grab the last index in the indexes list and add the
        # index value to the list of picked indexes
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)

        # find the largest (x, y) coordinates for the start of
        # the bounding box and the smallest (x, y) coordinates
        # for the end of the bounding box
        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])

        # compute the width and height of the bounding box
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)

        # compute the ratio of overlap
        overlap = (w * h) / area[idxs[:last]]

        # delete all indexes from the index list that have
        idxs = np.delete(idxs, np.concatenate(([last],
            np.where(overlap > overlapThresh)[0])))

    # return only the bounding boxes that were picked using the
    # integer data type
    return boxes[pick]
