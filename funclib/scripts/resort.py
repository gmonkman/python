# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-variable
'''cmdline util to sort files'''
import os
import shutil
import fnmatch
from datetime import datetime
import optparse

_SORT_MODES = ['first_char', 'two_char', 'date']

def main(opts, args_in):
    '''entry point to code'''
    for directory in args_in:
        basedir = os.path.abspath(opts.destination or os.path.split(directory)[0])

        if opts.recurse:
            for dirpath, dirnames, filenames in os.walk(directory):
                for file in fnmatch.filter(filenames, opts.pattern):
                    sort_file(basedir, dirpath, file, opts.sortmode, opts.copy)
        else:
            for file in fnmatch.filter(os.listdir(directory), opts.pattern):
                sort_file(basedir, directory, file, opts.sortmode, opts.copy)

def sort_file(basedir, directory, file, sortmode, copy):
    '''sort file'''
    path = os.path.abspath(os.path.join(directory, file,))

    date = None

    if sortmode == 'first_char':
        new_directory = os.path.join(basedir, file[0].lower())
    elif sortmode == 'two_char':
        new_directory = os.path.join(basedir, file[0:2].lower())
    else:
        if not date:
            date = _get_modification_date(path)

        new_directory = os.path.join(basedir, str(date.year) + ('%02d' % date.month))

    if not options.pretend:
        if not os.access(new_directory, os.F_OK):
            os.makedirs(new_directory)

        if copy:
            shutil.copy(path, os.path.join(new_directory, file))
        else:
            shutil.move(path, os.path.join(new_directory, file))

    if options.verbose or options.pretend:
        if copy:
            print(path, "<->", new_directory)
        else:
            print(path, "->", new_directory)

#TODO Add to funclib, and this is currently unused
def _get_file_count(paths, recurse=False):
    '''(list like|str)->int'''
    cnt = 0

    if isinstance(paths, str):
        paths = [paths]

    for ind, val in enumerate(paths):
        paths[ind] = os.path.normpath(val)

    if recurse:
        for thedir in paths:
            cnt += sum((len(f) for _, _, f in os.walk(thedir)))
    else:
        for thedir in paths:
            cnt += len([item for item in os.listdir(thedir) if os.path.isfile(os.path.join(thedir, item))])
    return cnt

def _get_modification_date(path):
    """Return the modification date & time of the file at path."""
    return datetime.fromtimestamp(os.stat(path).st_mtime)

if __name__ == "__main__":
    parser = optparse.OptionParser("Usage: %prog [options] directory ...")

    parser.add_option("-p", "--pattern", dest="pattern", help="file pattern to match")
    parser.add_option("-r", "--recurse", dest="recurse", action="store_true", help="recurse into subdirectories")
    parser.add_option("-d", "--destination", dest="destination", help="directory that will contain sorted files")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", help="show verbose output")
    parser.add_option("-P", "--pretend", dest="pretend", action="store_true", help="don't actually move files")
    parser.add_option("-s", "--sortmode", dest="sortmode", help="One of: [date | first_char | two_char]")
    parser.add_option("-c", "--copy", dest="copy", action="store_true", help="Copy rather than move")
    parser.set_defaults(pattern="*.*",
                        recurse=False,
                        destination=None,
                        verbose=False,
                        pretend=False,
                        sortmode="date",
                        copy=False)

    (options, args) = parser.parse_args()

    if options.sortmode not in _SORT_MODES:
        raise ValueError("Invalid sortmode -s %s. Options are [first_char | two_char | date]" % options.sortmode)

    if len(args) < 1:
        parser.error("Missing path argument")

    if options.verbose:
        print("File pattern:", options.pattern)

        if options.recurse:
            print("Recursing into subdirectories")

        if options.copy:
            print("Copy mode: Copy")
        else:
            print("Copy mode: Move")

        print("Sort mode: %s" % options.sortmode)
        print("Destination directory: %s" % (options.destination or "Default"))

    main(options, args)
