#pylint: disable=C0302, too-many-branches, dangerous-default-value, line-too-long, no-member, expression-not-assigned, locally-disabled

'''My file input and output library, e.g. for csv handling.'''
import csv
import os
import subprocess
import sys


from numpy import ndarray as numpy_ndarray

import fuckit


#FILE (CSV) IO
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

#TERMINAL IO
# Print iterations progress
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



def folder_open(folder='.'):
    '''(string) -> void
    opens a windows folder at path folder'''
    if os.name == 'nt':
        folder = folder.replace('/', '\\')
    with fuckit:
        subprocess.check_call(['explorer', folder])
