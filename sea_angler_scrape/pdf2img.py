# pylint: disable=C0302, line-too-long, too-few-public-methods, too-many-branches, too-many-statements, no-member
'''Custom export for Sea Angler pdfs.

PDFs are converted to images in an issue subfolder, created programmatically.

Just specify the pdf path. It is assumed that pdfs are individual pages.

Arguments
    -s: <path containing pdf>

e.g.
pdf2img.py -s c:\temp\pdfs
'''
import argparse
import os.path as path


from pdf2image import convert_from_path


import funclib.iolib as iolib


_POP_PATH = 'C:/Program Files (x86)/poppler-0.68.0/bin' #path to poppler


def get_issue(s):
    '''str -> str
    gets issue'''
    return s.split('_')[1:2][0]

def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__) #use the module __doc__

    #named: eg script.py -part head
    cmdline.add_argument('-s', '--source', help='Source PDFs', required=True)
    args = cmdline.parse_args()
    src = args.source

    n = sum([1 for x in iolib.file_list_generator1(src, wildcards='*.pdf', recurse=False)])
    PP = iolib.PrintProgress(bar_length=20, init_msg='Processing pdfs...', maximum=n)

    for d, f, _, pdf in iolib.file_list_generator_dfe(src, wildcards='*.pdf', recurse=False):
        issue_nr = get_issue(f)
        fld = path.normpath('%s/%s' % (d, issue_nr))
        iolib.create_folder(fld)

        img = convert_from_path(pdf, poppler_path=_POP_PATH, dpi=300, fmt='jpg')
        for x, i in enumerate(img):
            if x == 0:
                imgout = '%s/%s.jpg' % (fld, iolib.get_file_parts(pdf)[1])
            else:
                imgout = '%s/%s_%s.jpg' % (fld, iolib.get_file_parts(pdf)[1], x)
            i.save(fp=imgout, dpi=(300, 300))

        PP.increment()




if __name__ == "__main__":
    main()
