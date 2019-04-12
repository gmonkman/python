# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''Helper routines for tesseract processing of magazine pages with the
verbose output form
'''
import pandas as _pd
import cv2 as _cv2
import pytesseract as _pyt
from PIL import Image

from funclib.stringslib import to_ascii as _to_ascii
import funclib.iolib as _iolib
import funclib.pandaslib as _pdl
import funclib.stringslib as _stringslib
import funclib.baselib as _baselib


_stringslib.filter_alphanumeric

def _cleanstr(s):
    '''clean str'''
    return _stringslib.filter_alphanumeric1(s, allow_cr=False, allow_lf=False)


def to_paragraphs(img, override_page_nr=None, conf_thresh=90, psm=1):
    '''(str|ndarray, None|int, int, int) -> dict
    Parameters:
    imgpath:path to the image or ndarray
    override_page_nr:force a fixed page number, ignores detected page
    conf_thresh: only include text at or above this threshold
    psm: page detection mode to pass to tesseract (see docs)

    Take an image, and run tesseract detection on it, then
    concatenate detections to paragraph level and perform
    utf-8 to ascii conversion.

    Returns a dictionary with key page_num, block_num, par_num.

    Example:
    >>>to_paragraphs('c:/temp/myimg.jpg')
    {(1,1,1):'The quick brown fox...',
    (1,1,2):'Brexit is a shit show. Isn't it.'}
    '''
    #level,page_num,block_num,par_num,line_num,word_num,left,top,width,height,conf,text
    paragraphs = {}
    if isinstance(s, str):
        s = _pyt.image_to_data(img, config='--psm %s' % psm)
    else:
        s = _pyt.image_to_data(Image.fromarray(img), config='--psm %s' % psm)

    df = _pdl.df_fromstring(_to_ascii(s), sep='\t')
    df.sort_values(['page_num', 'block_num', 'par_num', 'line_num', 'word_num'], inplace=True, ascending=True)
    #our key is page_num, block_num, par_num
    #ipage_num, iblock_num, ipar_num, iline_num = pdl.cols_get_indexes_from_names(df, 'page_num', 'block_num', 'par_num', 'line_num')
    for row in df.iterrows():
        row = row[1]
        key = override_page_nr if isinstance(override_page_nr, int) else row.page_num, row.block_num, row.par_num
        try:
            if row.conf < conf_thresh:
                continue
        except:
            continue
        if key in paragraphs:
            paragraphs[key] = '%s %s' % (paragraphs[key], _cleanstr(row.text))
        else:
            paragraphs[key] = row.text
    return paragraphs


def _make_file(img):
    '''ndarray -> str

    Takes img, and saves it to a tempory file name.
    Probably not needed as looks like pytesseract can
    accept an image.
    '''
    s = _iolib.get_file_name2(_iolib.temp_folder('tesseract'))
    _cv2.imwrite(s, img)
    return s