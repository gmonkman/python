# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# no-self-use, unused-argument
'''Copies files with defined tags to
a specified subfolder where the image has valid regions
'''
import argparse
import os.path as path
from shutil import copyfile

import opencvlib.vgg as vgg
import opencvlib.digikamlib as dkl
from funclib.iolib import get_file_parts2
from funclib.iolib import create_folder
from funclib.iolib import print_progress
from funclib.baselib import DictList


def main():
    '''(str, kwags)->void
    Copies files matching the tags kwargs to
    the subfolder where the image has no set.

    The -r flag will only copy images without any ROIs defined in the VGG JSON file.

    Example:
    subjectless.py -t OR "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/bass-angler.json" "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/digikam4.db" is_train=head is_train=whole
    '''

    cmdline = argparse.ArgumentParser(description='Copies image files to a specified subfolder which have'
                                        ' the specified tags in digikam\n\n'
                                        'Only images in the root of the VGG file folder are checked.\n\n'
                                        'Example:\n'
                                        'subjectless.py -t OR "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/bass-angler.json" "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/digikam4.db" is_train=head is_train=whole'
                                      )

    cmdline.add_argument(
        '-f', '--subfolder', help='The subfolder to copy the files to. If optional uses the tags to create the folder.', default='')
    cmdline.add_argument(
        '-r', '--regionless', help='The default. Only image files without any regions are copied.', default='True')
    cmdline.add_argument(
        '-t', '--bool_type', help='Use AND or OR for key-value WHERE. Default:AND', default='AND')
    cmdline.add_argument('vggfile', help='VGG JSON file to manipulate')
    cmdline.add_argument('digikamfile', help='Digikam file (sqlitedb) to use')
    cmdline.add_argument(
        'key_values', help='Provide tag key value pairs, e.g. species=bass MV=is_train', nargs='+')
    args = cmdline.parse_args()

    vgg.SILENT = True

    vggfile = path.normpath(args.vggfile)
    if not path.isfile(vggfile):
        print('\n%s is not a file.' % vggfile)
        return

    try:
        vgg.load_json(vggfile)
    except Exception as e:
        s = ('Failed to initialise VGG JSON file %s.\n\n' /
             'The error was %s\n\n' /
             'Check it is a valid JSON file.' % (vggfile, str(e)))
        print(s)
        return

    print("Loaded JSON VGG file %s...." % vggfile)

    digikamfile = path.normpath(args.digikamfile)
    if not path.isfile(digikamfile):
        print('\n%s is not a digikam file.' % digikamfile)
        return

    try:
        digi = dkl.ImagePaths(digikamfile)
    except Exception as e:
        s = ('Failed to initialise the digikam database %s.\n\n' /
             'The error was %s\n\n' /
             'Check it is not in use and is a valid sqlite database.' % (digikamfile, str(e)))
        print(s)
        return

    if not args.key_values:
        print('No key-value pairs specified.')
        return

    # Build kw args
    kwords = DictList() #allow multiple values in our key value pairs, eg is_train=head is_train=whole will be {'is_train':['head','whole']}
    for kv in args.key_values:
        kv = str(kv)
        a, b = kv.split(sep='=')
        kwords[a] = b

    # return list of all matching images, irrespective of path
    if not args.bool_type in ['AND', 'OR']:
        print('Unknown argument %s for -t (the boolean search type). Defaulting to AND' %
              args.bool_type)

    images = digi.ImagesByTags(bool_type=args.bool_type, **kwords)
    print('%s images matched digikam tag criteria' % len(images))
    # create the new folder
    if args.subfolder == '':
        subfolder = " ".join(args.key_values)
    else:
        subfolder = args.subfolder

    new_fld = path.normpath(get_file_parts2(vggfile)[0] + '/' + subfolder)
    create_folder(new_fld)
    print("\nCreated folder %s" % new_fld)

    vgg_folder = get_file_parts2(vggfile)[0]
    cnt = 1
    copy_cnt=0
    for img in images:
        imgfld = get_file_parts2(img)[0]
        if vgg_folder == imgfld:
            do_copy = True

            if args.regionless:
                vgg_image = vgg.Image(img)
                do_copy = bool(vgg_image.shape_count == 0)

            if do_copy:
                dest = path.join(new_fld, get_file_parts2(img)[1])
                copyfile(img, dest)
                copy_cnt +=1

            s = '%s of %s' % (cnt, len(images))
            print_progress(cnt, len(images), s, bar_length=30)
            cnt += 1

    print('Done. Copied %s files to %s' % (copy_cnt, new_fld))


if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
