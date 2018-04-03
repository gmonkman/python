# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-import
'''Work with vgg and the dblib/W-300 point format files'''
import xml.etree.ElementTree as _et
from xml.dom import minidom as _minidom
from os import path as _path

from tqdm import tqdm as _tqdm

import opencvlib.imgpipes.vgg as _vgg
import funclib.iolib as _iolib
import funclib.stringslib as _stringslib
import opencvlib.roi as _roi



def create_xml(fname):
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


def vgg2xml(vgg_in, xml_out):
    '''(str, str)
    Read points in images defined in
    a vgg json file and export to a
    new xml file in the W-300 format

    vgg_in:
        existing vgg json file
    xml_out:
        new xml file
    '''
    vgg_in = _path.normpath(vgg_in)
    xml_out = _path.normpath(xml_out)
    assert not _iolib.file_exists(xml_out), 'XML export file already exists.'

    create_xml(xml_out)
    tree = _et.parse(xml_out)
    root = tree.getroot()
    images = root.find('images')

    assert isinstance(images, _et.Element)
    _vgg.load_json(vgg_in)

    x = sum(1 for n in _vgg.imagesGenerator(skip_imghdr_check=True))
    for Img in _tqdm.tqdm(_vgg.imagesGenerator(skip_imghdr_check=True), ascii=True, n=x):
        assert isinstance(Img, _vgg.Image)
        eImg = images.Element('image')
        eImg.attrib = {'file':Img.filename}
        eBox = eImg.append('box') #add bounding box later
        pts = []
        for Reg in Img.roi_generator(shape_type='point'):
            assert isinstance(Reg, _vgg.Region)
            lbl = int(Reg.region_key) + 1 if Reg.region_attr['pts'] is None else Reg.region_attr['pts']
            lbl = str(lbl)
            pts.append([Reg.x, Reg.y])
            ePart = eBox.append('part')
            ePart.attrib = {'name':lbl.zfill(2), 'x':str(pts[0]), 'y':str(pts[1])}

        x, y, w, h = _roi.bounding_rect_of_poly(pts, as_points=False)
        eBox.attrib = {'top':str(y), 'left':str(x), 'width':str(w), 'height':str(h)}

    tree.write(xml_out)
    print('XML written to %s')






