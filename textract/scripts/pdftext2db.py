
# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''Extract text from pdfs and write it to the books mmo database table

Positional Args:
    folder: directory with the pdfs (does not recurse)

Example:
pdftext2db.py C:/mypdfs
'''
import argparse
import os.path as path

from sqlalchemy import and_
import tika
print('Trying to start Tika server....')
tika.initVM()
from tika import parser

import mmodb
from mmodb.model import Book
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
    para_n = 1
    for pgnr, (_, element) in enumerate(etree.iterparse(bXML, tag='div', events=('end',), remove_blank_text=True,  remove_comments=True, encoding='utf8', html=True), 1):
        for child in element.getchildren():
            para = child.text
            if para:
                para = clean_para(para)
                if para:
                    yield pgnr, para_n, para
                    para_n += 1
        para_n = 1

def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__) #use the module __doc__
    cmdline.add_argument('folder', help='folder')
    args = cmdline.parse_args()
    sourcefld = path.normpath(args.folder)

    pdfs = [f for f in iolib.file_list_generator1(sourcefld, '*.pdf')]
    if not pdfs:
        raise FileNotFoundError('No pdfs found in %s' % sourcefld)

    PP = iolib.PrintProgress(len(pdfs))
    T = SW()
    for n, pdf in enumerate(pdfs):
        _, bookname, _ = iolib.get_file_parts(pdf)
        bookname = clean_para(bookname)
        xmlbook = parser.from_file(pdf, xmlContent=True)['content']

        for page_nr, para_nr, para_text in gen_paragraphs(xmlbook):
            book_ = mmodb.SESSION.query(Book).filter(and_(Book.book == bookname, Book.page_num==page_nr,  Book.para_num==para_nr)).first()
            if not book_:
                book_ = Book(book=bookname, page_num=page_nr, para_num=para_nr, para_text=para_text)
                mmodb.SESSION.add(book_)
            else:
                book_.date_modified = mssql.getNow()
                book_.text = para_text
        mmodb.SESSION.commit()
        T.lap()
        suff = 'Remain: %s' % T.pretty_remaining_global(len(pdfs) - n)
        PP.increment(suffix=suff)







if __name__ == '__main__':
    main()
