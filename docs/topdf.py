# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use,
# unused-argument
__doc__ = ('Routines for the manipulation of various documents')

import os.path as _path
import shutil as _shutil
from warnings import warn as _warn

#from PyPDF2 import PdfFileMerger as _pdfmerge
import numpy as _np
import cv2 as _cv2
import img2pdf as _img2pdf
from PyPDF2 import PdfFileMerger as _PdfFileMerger

import funclib.iolib as _iolib
import opencvlib.transforms as _transforms
import opencvlib.common as _common
import opencvlib.info as _info
from opencvlib.imgpipes import generators as _gen




_cInfo = _info.ImageInfo()


class a4():
    #x,y
    dpi72 = (595, 842)
    dpi150 = (1240, 1754)
    dpi300 = (2480, 3508)
    dpi600 = (4960, 7016)
    size_cm = (21.0, 29.7)
    size_inches = (8.3, 11.7)
    layout = _img2pdf.get_layout_fun((_img2pdf.mm_to_pt(210), _img2pdf.mm_to_pt(297)))
    layout_margin = _img2pdf.get_layout_fun((_img2pdf.mm_to_pt(168), _img2pdf.mm_to_pt(238)))

    
def _rotate_img(im):
    '''(ndarray) -> ndarry
    helper routine, rotate image so it fits on portrait a4
    im:ndarry (the image)

    returns: ndarray (the rotated image)
    '''
    w, h = _cInfo.resolution(im)
    cim = _np.copy(im)
    if w > h:
        cim = _transforms.rotate(cim, -90)
    return cim


def _build_lbl(s: str):
    '''placeholder to build label for img'''
    return s



def merge_pdf(rootdir, find='', out_file='', recurse=False):
    '''(str, str|iter, str, bool) -> [str]
    Finding and merge all pdfs in rootdir

    rootdir: root folder to find pdfs
    find: list or string, to match file names
    out_file: full qualified name to call the merged pdf. Will be created in root dir with the basename of rootdir if out_file is empty
    recurse: recurse subdirs of rootdir

    Returns: out_file
    '''
    rootdir = _path.normpath(rootdir)
    basefld = _path.basename(rootdir)
    pdfs = []
    if type(find) == str: find = [find]
    
    for d,f,e, fname in _iolib.file_list_generator_dfe(rootdir, '*.pdf', recurse=recurse):
        found = True
        if find:
            found = False
            for s in find:
                found = find in f
                if found: continue
        if not found: continue
        pdfs.append(fname)

    merger = PdfFileMerger()
    _ = (merger.append(open(pdf, 'rb')) for pdf in pdfs)

    if out_file == '':
        out_file = _path.normpath('%s/%s%s' % (rootdir, basefld, '.pdf'))

    with open(out_file, 'wb') as fout:
        merger.write(fout)
    return out_file
    

def merge_pdf_by_list(pdfs, out_file):
    '''(iter, str, str) -> void
    Finding and merge all pdfs in the iterable pdfs

    pdfs: iterable of fully qualified pdf file names
    out_file: full qualified name to call the merged pdf

    Returns: None

    Example:
    pdfs = ('c:\temp\1.pdf', 'c:\temp\2.pdf', 'c:\temp\3.pdf')
    merge_pdf_by_list(pdfs, 'c:\temp\1_2_3.pdf')
    '''

    rootdir = _path.normpath(rootdir)
    basefld = _path.basename(rootdir)

    merger = PdfFileMerger()
    _ = (merger.append(open(_path.normpath(pdf), 'rb')) for pdf in pdfs)

    with open(_path.normpath(out_file), 'wb') as fout:
        merger.write(fout)


def merge_img(rootdir, find='', save_to_folder='', pdf_file_name='', overwrite=False, label_with_file=False, label_with_fld=False, keep_tmp_images=False):
    '''(str, str|iter, str, bool, bool,bool, bool, int, int) -> str|None, str|None, list|None
    Find all images in rootdir then merge into a single pdf.

    rootdir: root folder
    find: wildcard match for files
    pdf_file_name: save the pdf to this name. If ommitted will use the base folder name of rootdir
    overwrite: If the pdf output file name already exists, overwrite it
    label_with_file: label each image with the images filename
    label_with_fld: add the folder base name to the label
    keep_tmp_images: do not delete the temporary images folder

    Returns: pdf file name, temporary folder used to save adjusted images to, list of matched images

    Example:
    _, _, _ = merge_img('C:\temp\images', 'C:\temp', ('IMG','PIC'), 'merged.pdf')
    '''
    files = []
    rootdir = _path.normpath(rootdir)

    n = _iolib.file_count2(rootdir, _common.IMAGE_EXTENSIONS_WILDCARDED)
    if n == 0:
        print('No images in folder %s.' % rootdir )
        return None, None, None

    base_fld = _path.basename(rootdir)
    tmp_fld = _iolib.temp_folder() #get temp folder now so we can use it later
    _iolib.create_folder(tmp_fld)
    fp = _gen.FromPaths(rootdir)

    PP = _iolib.PrintProgress(maximum = n)
    for img, pth, _ in fp.generate(recurse=False):
        img = _rotate_img(img)

        w, h = a4.dpi72
        img = _transforms.resize(img, height=h, do_not_grow=True)
        img = _transforms.resize(img, width=w, do_not_grow=True)

        fld, fname, ext = _iolib.get_file_parts(pth)

        if find:
            if not find.lower() in fname.lower():
                PP.increment()
                continue

        #img = _transforms.histeq_color(img)

        lbl = []
        if label_with_fld: lbl.append(base_fld)
        if label_with_file: lbl.append(_build_lbl(fname))

        if lbl:
            s = ' '.join(lbl)
            _common.draw_str(img, 10, 10, s, color = (0, 0, 0), scale=1.2, box_background=(255,255,255))
        
        fname = _path.normpath(tmp_fld + '/' + _iolib.get_temp_fname(suffix='.png', name_only=True)) #png expected to give better results
        #write the image to a temporary folder
        if not (_cv2.imwrite(fname, img)):
            raise Exception('OpenCV failed to write %s to disk' % fname)
        files.append(fname)
        PP.increment()

       
    #now make the pdf
    if not pdf_file_name:
        if save_to_folder:
            pdf_file_name = '%s/%s' % (save_to_folder, base_fld + '.pdf')
        else:
            pdf_file_name = '%s/%s' % (rootdir, base_fld + '.pdf')

    pdf_file_name = _path.normpath(pdf_file_name)

    if not overwrite and _iolib.file_exists(pdf_file_name):
        raise FileExistsError('PDF file %s exists.' % pdf_file_name)

    with open(pdf_file_name, "wb") as f:
        f.write(_img2pdf.convert(files, layout_fun=a4.layout_margin))
    
    if not keep_tmp_images:
        _shutil.rmtree(tmp_fld, ignore_errors=True)

    return pdf_file_name, tmp_fld, files
