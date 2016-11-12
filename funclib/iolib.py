#pylint: disable=C0302, too-many-branches, dangerous-default-value, line-too-long, no-member, expression-not-assigned, locally-disabled, not-context-manager

'''My file input and output library, e.g. for csv handling.'''
import csv
from glob import glob
import itertools
import os
import string

try:
    import cPickle as pickle
except:
    import pickle

import subprocess
import sys

from numpy import ndarray as numpy_ndarray
import fuckit
import funclib.stringslib as stringslib
from funclib.stringslib import add_right
from funclib.stringslib import add_left

_NOTEPADPP_PATH = 'C:\\Program Files (x86)\\Notepad++\\notepad++.exe'


#region CSV IO
def write_to_eof(filename, thetext):
    '''(string,string) ->void
    Write thetext to the end of the file given in filename.
    '''
    try:
        fid = open(filename, 'a')
        fid.write(thetext)
    finally:
        fid.close

def readcsv(filename, cols=1, startrow=0, numericdata=True):
    '''(string, int, bool, int, bool) -> list
    Reads a csv file into a list and returns the list
    Set cols to the number of cols in the csv.

    If you want to skip the first row (eg if you have a header row, set startrow to 1.
    '''
    data = [0] * (cols)
    for i in range(cols):
        data[i] = []
    if sys.version_info.major == 2:
        with open(filename, 'rb') as csvfile:  #open the file, and iterate over its data
            csvdata = csv.reader(csvfile)   #tell python that the file is a csv
            for i in range(0, startrow): #skip to the startrow
                csvdata.next()
            for row in csvdata:     #iterate over the rows in the csv
                #Assign the cols of each row to a variable
                for items in range(cols):   #read in the text values as floats in the array
                    if numericdata:
                        data[items].append(float(row[items]))
                    else:
                        data[items].append(row[items])
    elif sys.version_info.major == 3:
        with open(filename, newline='') as csvfile:  #open the file, and iterate over its data
            csvdata = csv.reader(csvfile)   #tell python that the file is a csv
            for i in range(0, startrow): #skip to the startrow
                csvdata.next()
            for row in csvdata:     #iterate over the rows in the csv
                #Assign the cols of each row to a variable
                for items in range(cols):   #read in the text values as floats in the array
                    if numericdata:
                        data[items].append(float(row[items]))
                    else:
                        data[items].append(row[items])
    else:
        sys.stderr.write('You need to use python 2* or 3* \n')
        exit(1)
    return data

def writecsv(filename, datalist, header=[], inner_as_rows=True):
    '''(string, list, list, bool) -> Void
    Reads a csv file into a list and returns the list
    ---
    inner_as_rows == True
    [[1,a],[2,b]]
    row1:1,2
    row2:a,b
    -
    inner_as_rows == False
    [[1,a],[2,b]]
    row1=1,a
    row2=2,b
    '''
    csvfile = []
    useheader = False
    #make sure we have the correct versions of python
    if sys.version_info.major == 2:
        csvfile = open(filename, 'wb')
    elif sys.version_info.major == 3:
        csvfile = open('pythonTest.csv', 'w', newline='')
    else:
        sys.stderr.write('You need to use python 2* or 3* \n')
        exit(1)

    #if user passed a numpy array, convert it
    if isinstance(datalist, numpy_ndarray):
        datalist = datalist.T
        datalist = datalist.tolist()
    #if there is no data, close the file
    if len(datalist) < 1:
        csvfile.close()
        return
    #check to see if datalist is a single list or list of lists
    is_listoflists = False
    list_len = 0
    num_lists = 0
    if isinstance(datalist[0], (list, tuple)):    #check the first element in datalist
        is_listoflists = True
        list_len = len(datalist[0])
        num_lists = len(datalist)
    else:
        is_listoflists = False
        list_len = len(datalist)
        num_lists = 1
    #if a list then make sure everything is the same length
    if is_listoflists:
        for list_index in range(1, len(datalist)):
            if len(datalist[list_index]) != list_len:
                sys.stderr.write('All lists in datalist must be the same length \n')
                csvfile.close()
                return
    #if header is present, make sure it is the same length as the number of
    #cols
    if len(header) != 0:
        if len(header) != num_lists:
            sys.stderr.write('Header length did not match the number of columns, ignoring header.\n')
        else:
            useheader = True

    #now that we've checked the inputs, loop and write outputs
    writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL) # Create writer object
    if useheader:
        writer.writerow(header)
    if inner_as_rows:
        for row in range(0, list_len):
            thisrow = []
            if num_lists > 1:
                for col in range(0, num_lists):
                    thisrow.append(datalist[col][row])
            else:
                thisrow.append(datalist[row])
            writer.writerow(thisrow)
    else:
        for row in datalist:
            writer.writerow(row)

    #close the csv file to save
    csvfile.close()
#endregion


#region file system
def exit():
    if get_platform == 'windows':
        os.system("pause")
    else:
        os.system('read -s -n 1 -p "Press any key to continue..."')
    sys.exit()

def get_platform():
    '''-> str
    returns windows, mac, linux
    '''
    s = sys.platform.lower()
    if s == "linux" or s == "linux2":
       return 'linux'
    elif s == "darwin":
       return 'mac'
    elif s == "win32":
       return 'windows'

def drive_get_uuid(drive='C:',strip=['-'], make_lcase=True, return_when_unidentified='??'):
    drive = os.popen('vol %s' % drive).readlines()[1].split()[-1]
    if len(drive) == 0: drive = return_when_unidentified
    if make_lcase: drive = drive.lower()
    for char in strip:
        drive = drive.replace(char, '')
    return drive

def get_available_drives(strip=['-'], make_lcase=True, return_when_unidentified='??'):
    '''->dictionary
    gets a list of available drives as the key, with uuids as the values
    eg. {'c:':'abcd1234','d:':'12345678'}
    '''
    drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
    uuids = [drive_get_uuid(drv, strip, make_lcase, return_when_unidentified) for drv in drives]
    return dict(zip(drives, uuids))

def get_available_drive_uuids(strip=['-'], make_lcase=True, return_when_unidentified='??'):
    '''->dictionary
    gets a list of available drives with uuids as the key
    eg. {'c:':'abcd1234','d:':'12345678'}
    '''
    drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
    uuids = [drive_get_uuid(drv, strip, make_lcase, return_when_unidentified) for drv in drives]
    return dict(zip(uuids, drives))

def get_drive_from_uuid(uuid, strip=['-'], make_lcase=True):
    '''str, str iterable, bool->str | None
    given a uuid get the drive letter
    uuid is expected to be lower case

    Returns None if not found
    '''
    uuid = uuid.encode('ascii', 'ignore')
    if make_lcase: uuid = uuid.lower()
    for char in strip:
        uuid = uuid.replace(char, '')
    drives = get_available_drive_uuids(strip, make_lcase) #first val is drive, second is the uuid
    if drives.has_key(uuid):
        return drives[uuid]
    else:
        return None

def file_list_generator(paths, wildcards):
    '''(iterable, iterable) -> tuple
    Takes a list of paths and wildcards and creates a
    generator which can be used to iterate through
    the generated file list so:
    paths = ('c:/','d:/')     wildcards=('*.ini','*.txt')
    Will generate: c:/*.ini, c:/*.txt, d:/*.ini, d:/*.txt
    '''
    for vals in (add_right(x[0]) + x[1] for x in itertools.product(paths, wildcards)):
        yield os.path.normpath(vals)

def file_list_generator1(paths, wildcards):
    '''(iterable, iterable) -> tuple
    Takes a list of paths and wildcards and creates a
    generator which iterates through all the files found
    in the paths matching the wildcards.
    the generated file list so:
    '''
    for vals in (add_right(x[0]) + x[1] for x in itertools.product(paths, wildcards)):
        for myfile in glob(vals):
            yield os.path.normpath(myfile)

def get_file_name(path='', prefix='', ext='.txt'):
    '''(str, str, str) -> str
    returns a filename, based on a datetime stamp

    If path is not specified then the CWD is used.

    generally used to quickly writeout results to a new file
    '''
    if path == '':
        path = os.getcwd()

    return os.path.normpath(os.path.join(path, prefix + stringslib.datetime_stamp() + add_left(ext, os.path.extsep)))

def folder_open(folder='.'):
    '''(string) -> void
    opens a windows folder at path folder'''
    if os.name == 'nt':
        folder = folder.replace('/', '\\')
    with fuckit:
        subprocess.check_call(['explorer', folder])

def notepadpp_open_file(filename):
    '''(str) -> void
    opens filename in notepad++

    File name should be in the C:\\dirA\\dirB\\xx.txt format
    '''
    with fuckit:
        openpth = _NOTEPADPP_PATH + ' ' + '"' + filename + '"'
        subprocess.Popen(openpth)

def write_to_file(results, prefix='', open_in_npp=True):
    '''
    (str|iterable) -> str
    Takes result_text and writes it to a file in the cwd.
    Prints out the file name at the end and opens the folder location

    Returns the fully qualified filename written

    Use to quickly right single results set to a file

    If results is a string then it writes out the string, otherwise it iterates through
    results writing all elements to the file.
    '''
    filename = os.getcwd() + '\\RESULT' + prefix + stringslib.datetime_stamp() + '.txt'
    with open(filename, 'w+') as f:
        if isinstance(results, str):
            f.write(results)
        else:
            for s in results:
                f.write(str(s) + '\r\n')

    print results
    print filename
    if open_in_npp: notepadpp_open_file(filename)
    return filename

def create_file(file_name):
    '''(str) -> void
    creates file if it doesnt exist
    '''
    if not os.path.isfile(file_name):
        write_to_eof(file_name, '')

def file_exists(file_name):
    '''(str) -> bool
    Returns true if file exists
    '''
    return os.path.isfile(file_name)

def create_folder(folder_name):
    '''(str) -> void
    creates a folder
    '''
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)

def pickleit(full_file_name, obj):
    '''(str) -> void
    Takes full_file path and pickles (dumps) obj to the file system.
    Does a normpath on full_file_name
    '''
    with open(os.path.normpath(full_file_name), 'wb') as myfile:
        pickle.dump(obj, myfile)

def unpickle(path):
    '''(str) -> unpickled stuff
    attempts to load a pickled object named path
    Returns None if file doesnt exist
    '''
    if file_exists(path):
        with open(path, 'rb') as myfile:
            return pickle.load(myfile)
    else:
        return None
#endregion




#region console stuff
def input_int(prompt='Input number', default=0):
    '''get console input from user and force to int'''
    return int(stringslib.read_number(raw_input(prompt), default))




def print_progress(iteration, total, prefix='', suffix='', decimals=2, bar_length=50):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : number of decimals in percent complete (Int)
        bar_length   - Optional  : character length of progbar (Int)
    """
    filled_length = int(round(bar_length * iteration / float(total)))
    if iteration / float(total) > 1:
        total = iteration
    percents = round(100.00 * (iteration / float(total)), decimals)
    if bar_length > 0:
        progbar = '#' * filled_length + '-' * (bar_length - filled_length)
    else:
        progbar = ''

    sys.stdout.write('%s [%s] %s%s %s\r' % (prefix, progbar, percents, '%', suffix)), sys.stdout.flush()
    if iteration == total:
        print "\n"
#endregion
