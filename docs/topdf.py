# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use,
# unused-argument
__doc__ = ('Routines for the manipulation of various documents')

import os.path as _path

from PyPDF2 import PdfFileMerger as _pdfmerge
import numpy as _np
import cv2 as _cv2
import img2pdf as _img2pdf

import funclib.iolib as _iolib
import opencvlib.transforms as _transforms
import opencvlib.common as _common
import opencvlib.info as _info
from opencvlib.imgpipes import generators as _gen




_cInfo = _info.ImageInfo()

_img2pdf_layout = _img2pdf.get_layout_fun((_img2pdf.mm_to_pt(210), _img2pdf.mm_to_pt(297)))

class a4():
    dpi72 = (595, 842)
    dpi300 = (2480, 3508)
    dpi600 = (4960, 7016)
    size_cm = (21.0, 29.7)
    size_inches = (8.3, 11.7)
    





def merge_pdf(rootdir, find, outdir, recurse=False):
    '''(str|iter, str|iter, str, bool) -> [str]
    Recurse through directories finding all pdfs then merge as seperate documents
    rootdir: 
    '''
    #for d,f,e in _iolib.file_list_generator_dfe(rrootdir, '*.pdf', recurse):
    #merger=_pdfmerge()
    #merger.append(pdf)
    #merger.write(prefix + "_ALL_" + suffix +".pdf")
    #merger.close()
    pass

def _rotate_img(im):
    '''(ndarray) -> ndarry
    helper routine, rotate image so it fits on portrait a4
    im:ndarry (the image)

    returns: ndarray (the rotated image)
    '''
    w,h = _cInfo.resolution(im)
    cim = _np.copy(im)
    if w > h:
        cim = _transforms.rotate(cim, -90)
    return cim


def _build_lbl(s: str):
    '''placeholder to build label for img'''
    return s




def merge_img(rootdir, find, outdir='', recurse:bool=False, label=False):
    '''(str|iter, str|iter, str, bool, bool) -> [str]
    Recurse through directories finding all pdfs then merge as seperate documents
    rootdir: 
    '''
    fp = _gen.FromPaths(rootdir, transforms=Transforms, filters=Filters)
    for img, pth, _ in fp.generate(recurse=recurse):
        img = _rotate_img(img)
        fld, fname, ext = _iolib.get_file_parts(pth)
        lbl = _build_lbl(fname)
        img = _transforms.equalize_hist(img)
        img = _common.draw_str(img, 10, 10, lbl, color = (0, 0, 0), scale=1.2, box_background=True)
        tmp_fld = _iolib.temp_folder()
        fname = _path.normarg_path(tmp_fld + '/' + _iolib.get_temp_fname(suffix='.pdf'))
        _cv2.imwrite(fname, img)



  