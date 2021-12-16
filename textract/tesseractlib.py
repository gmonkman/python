# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''Helper routines for tesseract processing of magazine pages with the
verbose output form
'''
from PIL import Image

import pytesseract.pytesseract as _pyt
from funclib.stringslib import to_ascii as _to_ascii
import funclib.pandaslib as _pdl
import funclib.stringslib as _stringslib


def _cleanstr(s):
    '''clean str'''
    return _stringslib.filter_alphanumeric1(s, allow_cr=False, allow_lf=False, remove_double_quote=True, remove_single_quote=True)


def to_paragraphs(img, override_page_nr=None, conf_thresh=70, psm=1):
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
    if isinstance(img, str):
        s = _pyt.image_to_data(img, config='--psm %s' % psm)
    else:
        s = _pyt.image_to_data(Image.fromarray(img), config='--psm %s' % psm)
    s = _to_ascii(s)
    s = s.replace('"', '')
    s = s.replace("'", "")
    df = _pdl.df_fromstring(s, sep='\t')
    df.sort_values(['page_num', 'block_num', 'par_num', 'line_num', 'word_num'], inplace=True, ascending=True)
    # our key is page_num, block_num, par_num
    # ipage_num, iblock_num, ipar_num, iline_num = pdl.cols_get_indexes_from_names(df, 'page_num', 'block_num', 'par_num', 'line_num')
    for row in df.iterrows():
        row = row[1]
        key = override_page_nr if isinstance(override_page_nr, int) else row.page_num, row.block_num, row.par_num
        try:
            if row.conf < conf_thresh:
                continue
        except:
            continue
        try:
            if isinstance(row.text, str):
                s = _cleanstr(row.text)
                if key in paragraphs:
                    paragraphs[key] = '%s %s' % (paragraphs[key], s)
                else:
                    paragraphs[key] = s
        except Exception as _:
            pass
    return paragraphs
