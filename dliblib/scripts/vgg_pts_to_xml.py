# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''Convert VGG configured points to the
XML format used by dlib and the W-300 faces
dataset. All points are converted.
'''
import argparse

import dliblib.vgg2xml as vgg2xml
from os import path as _path

import funclib.iolib as iolib


def main():
    '''main
    '''
    cmdline = argparse.ArgumentParser(description=__doc__) #use the module __doc__
    cmdline.add_argument('vgg_in', help='Path to the vgg json file')
    cmdline.add_argument('xml_out', help='Name of the outputted XML file, must not exist.')

    args = cmdline.parse_args()
    vgg_in = _path.normpath(args.vgg_in)
    xml_out = _path.normpath(args.xml_out)

    assert not iolib.file_exists(xml_out), 'XML output file %s exists.' % xml_out
    vgg2xml.SILENT = False
    errs = vgg2xml.convert(vgg_in, xml_out, ignore_no_roi=True)
    #print('Done, XML save to %s' % xml_out)

if __name__ == "__main__":
    main()
