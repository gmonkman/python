
# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import
'''new script wih argparse'''
import argparse
import os.path as path

from sqlalchemy import and_

import EAST.regions as regions
import mmodb
from opencvlib.view import show
from mmodb.model import Mag
import textract.samag as samag
import textract.tesseractlib as tes
import dblib.mssql as _mssql
import textract as _textract


def get_issue(s):
    '''str -> str
    gets issue from the file name'''
    return s.split('_')[1:2][0]


def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__) #use the module __doc__
    #positional: e.g. scipt.py c:/temp
    #args.folder == 'c:/temp'
    cmdline.add_argument('folder', help='folder')
    cmdline.add_argument('-v', '--vis', help='Export visualisations of the detected regions', action='store_true')
    args = cmdline.parse_args()
    sourcefld = path.normpath(args.folder)
    if args.vis:
        visfold = path.normpath('%s/vis' % args.folder)
    else:
        visfold = None

    for i, _, imgpath, group_key in regions.text_region_generator(sourcefld, visfold):
        issue, pgnr = samag.get_issue_and_page(imgpath)
        det = tes.to_paragraphs(i)
        for k, para in det.items():
            _, block, par = k #page nr, block nr, para nr
            para = para.strip()
            if para:
                if len(para.split()) >= _textract.ini.textract.is_sentence_word_limit:
                    mag_ = mmodb.SESSION.query(Mag).filter(and_(Mag.mag == samag.MAG_NAME, Mag.issue == issue, Mag.page_num == pgnr, Mag.block_num == block, Mag.group_key == group_key, Mag.paragraph == par)).first()
                    if not mag_:
                        mag_ = Mag(mag=samag.MAG_NAME, issue=issue, page_num=pgnr, paragraph=par, text=para, block_num=block, group_key=group_key)
                        mmodb.SESSION.add(mag_)
                    else:
                        mag_.date_modified = _mssql.getNow()
                        mag_.text = para

        mmodb.SESSION.commit()





if __name__ == "__main__":
    main()
