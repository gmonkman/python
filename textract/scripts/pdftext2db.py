
# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''Extract text from pdfs and write it to the books mmo database table

Args:
'''
import argparse
import os.path as path

from sqlalchemy import and_
import tika
print('Trying to start Tika server....')
tika.initVM()
from tika import parser

import mmodb
from mmodb.model import Mag
import dblib.mssql as mssql
import textract as textract
import funclib.iolib as iolib
import funclib.baselib as baselib
import funclib.stringslib as stringslib
from funclib.stopwatch import StopWatch as SW
from lxml import etree
from io import BytesIO


def clean_para(s):
    '''str -> str
    '''
    s = stringslib.filter_alphanumeric1(s, remove_single_quote=True, remove_double_quote=True, allow_cr=False, allow_lf=False).strip()
    return s


def gen_paragraphs(xml):
    '''(string) -> int, int, string
    parse xml

    Returns:
        page number, paragraph number, text content
    '''
    bXML = BytesIO(bytes(xml, encoding='utf8'))

    for _, element in etree.iterparse(bXML, tag='page'):
        belement = BytesIO(element, encoding='utf-8')
        for _, para in etree.iterparse(belement, tag='p'):





def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__) #use the module __doc__
    #positional: e.g. scipt.py c:/temp
    #args.folder == 'c:/temp'
    cmdline.add_argument('folder', help='folder')
    args = cmdline.parse_args()
    sourcefld = path.normpath(args.folder)

    pdfs = iolib.file_list_generator1(sourcefld, '*.pdf')
    if not pdfs:
        raise FileNotFoundError('No pdfs found in %s' % sourcefld)

    PP = iolib.PrintProgress(len(pdfs))

    for pdf in pdfs:
        d, bookname, e = iolib.get_file_name(pdf)
        xmlbook = parser.from_file(fname, xmlContent=True)['content']

        for para_nr, page_nr, text_ in gen_paragraphs(xmlbook):

        PP.increment()

