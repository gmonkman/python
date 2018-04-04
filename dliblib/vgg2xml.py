# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-import
'''Work with vgg and the dblib/W-300 point format files'''
import xml.etree.ElementTree as _et
from xml.dom import minidom as _minidom
from os import path as _path


import opencvlib.imgpipes.vgg as _vgg
import funclib.iolib as _iolib
from funclib.iolib import PrintProgress as _PP
import funclib.stringslib as _stringslib
import funclib.baselib as _baselib

import opencvlib.roi as _roi

SILENT = False

def _create_xml(fname):
    '''(str) -> void
    Create the xml file with hardcoded header info

    fname:
        filename
    '''
    s = ("<?xml version='1.0' encoding='ISO-8859-1'?>\n"
        "<?xml-stylesheet type='text/xsl' href='image_metadata_stylesheet.xsl'?>\n"
        "<dataset>\n"
        "<name>Testing faces</name>\n"
        "<comment>Landmarks</comment>\n"
        "<images>\n"
        "</images>\n"
        "</dataset>\n"
        )
    _iolib.file_create(fname, s)


def _validate(vggImg, ignore_no_roi):
    '''(class:vgg.Image) -> bool, list
    Checks the validity of a vgg.Image instance
    for conversion to an dlib xml record.

    Returns:
        True|False, indicating validity,
        list of problems
    '''
    assert isinstance(vggImg, _vgg.Image)

    problems = []
    no_roi = True
    lbls = []
    valid = True
    for vggReg in vggImg.roi_generator(shape_type='point'):
        no_roi = False
        assert isinstance(vggReg, _vgg.Region)
        lbl = int(vggReg.region_json_key) + 1 if vggReg.region_attr.get('pts', '') == '' else vggReg.region_attr['pts']
        lbl = str(lbl)
        if lbl in lbls:
            problems.append('lbl %s duplicated.' % lbl)
            valid = False
        else:
            lbls.append(lbl)

        if vggReg.x is None or vggReg.y is None:
            problems.append('point x or y could not be read')


    if no_roi:
        valid = False
        if not ignore_no_roi:
            problems.append('No rois defined')
    return valid, problems


def convert(vgg_in, xml_out, ignore_no_roi=True):
    '''(str, str, bool) -> list, list
    Read points in images defined in
    a vgg json file and export to a
    new xml file in the W-300 format

    vgg_in:
        existing vgg json file
    xml_out:
        new xml file
    ignore_no_roi:
        do not log images without rois

    Returns:
        list of all problems, empty
        if no problems occured.
    '''
    vgg_in = _path.normpath(vgg_in)
    xml_out = _path.normpath(xml_out)
    assert not _iolib.file_exists(xml_out), 'XML export file already exists.'

    _create_xml(xml_out)
    tree = _et.parse(xml_out)
    root = tree.getroot()
    eImages = root.find('images')

    assert isinstance(eImages, _et.Element)
    _vgg.load_json(vgg_in)

    x = sum(1 for n in _vgg.imagesGenerator(skip_imghdr_check=True))
    PP = _PP(x)
    errs = []
    for vggImg in _vgg.imagesGenerator(skip_imghdr_check=True):
        if not SILENT:
            PP.increment()
        assert isinstance(vggImg, _vgg.Image)

        valid, problems = _validate(vggImg, ignore_no_roi)
        if not valid:
            if problems:
                problems = ', '.join(problems)
                problems = vggImg.filename + ': ' + problems
                errs.append(problems)
            continue

        eImg = _et.SubElement(eImages, 'image', {'file':vggImg.filename})
        eBox = _et.SubElement(eImg, 'box')
        pts = []
        for vggReg in vggImg.roi_generator(shape_type='point'):
            assert isinstance(vggReg, _vgg.Region)
            lbl = int(vggReg.region_json_key) + 1 if vggReg.region_attr.get('pts', None) is None else vggReg.region_attr['pts']
            lbl = str(lbl)
            pts.append([vggReg.x, vggReg.y])
            _ = _et.SubElement(eBox, 'part', {'name':lbl.zfill(2), 'x':str(vggReg.x), 'y':str(vggReg.y)})

        res = vggImg.resolution
        x, y, w, h = _roi.bounding_rect_of_poly(pts, as_points=False)
        pad = 10
        x = x - pad if x > pad - 1 else 0
        y = y - pad if y > pad - 1 else 0
        w = w + pad if x + pad <= res[0] else res[0] - x
        h = h + pad if y + pad <= res[1] else res[1] - y
        eBox.attrib = {'top':str(y), 'left':str(x), 'width':str(w), 'height':str(h)}

    tree.write(xml_out)

    if not SILENT:
        if errs:
            print('\n'.join(errs))
        print('\nXML written to %s' % xml_out)

    return errs
