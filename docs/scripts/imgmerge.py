
# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
__doc__ = ('Merge images into pdfs from folders.\n'      
           'syntax: img2pdf.py <root> [-r]\n'
           'root: root folder to look for images\n'
           '-r: if present, recurse through folders in root\n'
           '-o: force overwrite of the output pdf\n\n'
           'Example:\n'
           'img2pdf "C:\temp" -r')


import argparse
from os.path import normpath

import funclib.iolib as iolib
import docs.topdf as topdf


#\\nercwlctdb\Projects\PROJECTS1\NEC06941_LTS-S_UK-SCaPE_WP1.3_WP1.4_Field_Survey\WP1.3 & 1.4_Field_Survey\Year 3 2021\Square document packs Winter 2021\Not yet visited\Photos


def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__) #use the module __doc__
    cmdline.add_argument('root', help='Root folder to look for your images.')
    cmdline.add_argument('saveto', help='Root folder to save the created pdf.')
    cmdline.add_argument('-r', '--recurse', help='Recurse <root>', action='store_true')
    cmdline.add_argument('-o', '--overwrite', help='Allow overwriting of existing pdfs', action='store_true')
    args = cmdline.parse_args()
    saveto = normpath(args.saveto)
    root = normpath(args.root)

    if args.recurse:
        n = sum(1 for x in iolib.folder_generator(root))
        PP = iolib.PrintProgress(n)
        for fld in iolib.folder_generator(root):
            pdf_file_name, tmpfld, imgs = topdf.merge_img(fld, save_to_folder=saveto, label_with_file=True, label_with_fld=True, overwrite=args.overwrite)
            PP.increment()
    else:
        pdf_file_name, tmpfld, imgs = topdf.merge_img(root, save_to_folder=saveto, label_with_file=True, label_with_fld=True, overwrite=args.overwrite)
    
if __name__ == "__main__":
    main()

