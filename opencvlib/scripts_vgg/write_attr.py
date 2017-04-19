# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# no-self-use, unused-argument
'''Fix up JSON file to create region attributes where
two regions have been defined for a single subject'''

import argparse
from os import path

import opencvlib.vgg as vgg
from funclib.iolib import print_progress


def write_region_attributes(species, backup=True):
    '''(str)->void
    Species is the species name to write to the VGG file.

    Will write the region tags:
    species=bass, subjectid=1, part=head|tail
    Decides to write head/tail based on the shape area.

    Only works if there is a single subject (fish) with shapes.

    This is purely a fix to save manual entry.

    *Note, load_json needs to be called fits.
    '''
    max_area = 0
    max_region_key = None
    region_cnt = 0
    region_shape_cnt = 0
    docontinue = False
    dosave = False
    cnt = 0
    fixed = 0
    targ_cnt = 0

    if not vgg.JSON_FILE:
        raise ValueError(
            'Unable to load VGG JSON file. Check the path and that the file is not in use.')

    # first pass to get some stats
    for key in vgg.JSON_FILE:
        subj = vgg.Subject(key)
        region_cnt = 0
        region_shape_cnt = 0
        for region in subj.regions_generator():
            assert isinstance(region, vgg.Region)
            if region.has_attrs:
                docontinue = True
                break

            region_cnt += 1
            region_shape_cnt = region_shape_cnt + \
                (1 if region.shape in vgg.VALID_SHAPES_2D else 0)
            if region.area > max_area:
                max_area = region.area
                max_region_key = region.region_key

        if docontinue:  # move to next image if there is not two shapes
            docontinue = False
            cnt += 1
            continue

        if region_cnt == 2 and region_cnt == region_shape_cnt:
            targ_cnt += 1
            for region in subj.regions_generator():
                if not region.has_attrs:
                    region.species = species
                    region.subjectid = 1
                    region.part = ('whole' if region.region_key ==
                                   max_region_key else 'head')
                    region.write()
                    s = '\nUpdated regions in %s, part: %s' % (
                        key, region.part)
                    #_prints(s)
                    dosave = True
                    fixed += 1
        cnt += 1
        print_progress(cnt, len(vgg.JSON_FILE), '%s of %s' %
                       (cnt, len(vgg.JSON_FILE)), bar_length=30)

    if dosave:
        vgg.save_json(backup)
        s = '\nWrote %s regions in %s images of %s' % (
            fixed, targ_cnt, len(vgg.JSON_FILE))
        print(s)
    else:
        print('\nCompleted without error. No regions matched criteria to fix.')


def main():
    '''main entry if run from commandline.

    Example:
    write_attr.py -s bass -b "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/bass-angler.json"
    '''
    cmdline = argparse.ArgumentParser(description='Write region attributes in a VGG file for a defined species (or ALL) where'
                                      'shapes already exist.\n'
                                      'Currently just writes for head and whole.\n'
                                      'Example:\n'
                                      'write_attr.py -s bass -b "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/bass-angler.json"'
                                      )

    # position argument
    cmdline.add_argument('-s', '--species', help='Species name to write to the VGG image files',
                         required=False, default='bass')
    cmdline.add_argument('-b', '--backup', help='Backup the VGG file before updating',
                         action='store_true')
    cmdline.add_argument('file', help='VGG JSON file to manipulate')
    args = cmdline.parse_args()

    spp = args.species
    vgg.SILENT = False
    vgg.load_json(path.normpath(args.file))

    if spp == '':
        spp = 'bass'

    if spp not in vgg.VALID_SPECIES:
        print('Species not found. Valid species are ' +
              ", ".join(vgg.VALID_SPECIES))
        return

    print("Updating regions, subject target is %s....\n" % spp)

    write_region_attributes(spp, args.backup)


if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
