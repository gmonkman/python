# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-import
'''Work with vgg and the dblib/W-300 point format files'''
import xml.etree.ElementTree as _et
from xml.dom import minidom as _minidom
from os import path as _path


import opencvlib.imgpipes.vgg as _vgg
import funclib.iolib as _iolib
from funclib.iolib import PrintProgress as _PP
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
    eImages = root.find('images')

    assert isinstance(eImages, _et.Element)
    _vgg.load_json(vgg_in)

    x = sum(1 for n in _vgg.imagesGenerator(skip_imghdr_check=True))
    PP = _PP(x)
    for vggImg in _vgg.imagesGenerator(skip_imghdr_check=True):
        PP.increment()
        assert isinstance(vggImg, _vgg.Image)
        eImg = _et.SubElement(eImages, 'image', {'file':vggImg.filename})
        eBox = _et.SubElement(eImg, 'box')
        pts = []
        for vggReg in vggImg.roi_generator(shape_type='point'):
            assert isinstance(vggReg, _vgg.Region)
            lbl = int(vggReg.region_json_key) + 1 if vggReg.region_attr.get('pts', None) is None else vggReg.region_attr['pts']
            lbl = str(lbl)
            pts.append([vggReg.x, vggReg.y])
            ePart = _et.SubElement(eBox, 'part', {'name':lbl.zfill(2), 'x':str(vggReg.x), 'y':str(vggReg.y)})

        res = vggImg.resolution
        x, y, w, h = _roi.bounding_rect_of_poly(pts, as_points=False)
        pad = 10
        x = x - pad if x > pad - 1 else 0
        y = y - pad if y > pad - 1 else 0
        w  = w + pad if x + pad <=  res[0] else res[0] - x
        h  = h + pad if y + pad <=  res[1] else res[1] - y
        eBox.attrib = {'top':str(y), 'left':str(x), 'width':str(w), 'height':str(h)}

    tree.write(xml_out)
    print('XML written to %s' % xml_out)






