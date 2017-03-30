# pylint: disable=C0302, line-too-long, too-few-public-methods, too-many-branches, too-many-statements, unused-import, no-member
'''MODULE COMMENTS HERE
'''

#region imports
#region base imports
import datetime
import itertools
import math
import os
import time
#end region

#region 3rd party imports
import fuckit
import numpy as np
import pandas as pd
import scipy
import scipy.stats
import xlwings
#endregion

#region my imports
import funclib.arraylib as arraylib
import funclib.iolib as iolib
#import funclib.statslib as statslib #includes rpy which takes ages to load
from funclib.stringslib import add_right
from enum import Enum
from funclib.baselib import switch
#endregion
#endregion




#region main
def main(getcmdlineargs=False, initialise_ini=False):
    '''
    <DEV_NOTE>
        (bool)->void
        Main is only called if the script is directly executed and can
        be used to do stuff in here like testing.

        Setting getcmdlineargs to true will set up cmdline arguments,
        which can be loaded into global variables as required (need to define)
    </DEV_NOTE>
    '''
    if getcmdlineargs:
        import argparse
        cmdline = argparse.ArgumentParser(description='Description if script is excuted with -h option')
        cmdline.add_argument('-f', '--foo', help='Description for foo argument', required=True)
        cmdline.add_argument('-b', '--bar', help='Description for bar argument', required=False, default='WAS_EMPTY')
        cmdargs = cmdline.parse_args()

        if cmdargs.foo == 'THE FOO ARG':
            #global _FOO = cmdargs.foo
            #do stuff
            pass

        if cmdargs.bar == 'WAS_EMPTY':
            #do stuff if no bar argument was passed
            pass
        else:
            #global _BAR = cmdargs.bar
            pass

    if initialise_ini:
        from funclib import inifilelib
        ini_name = os.path.abspath(__file__) + '.ini'
        ini = inifilelib.ConfigFile(ini_name)
        #read and write values as which, put into global variable if needed


if __name__ == '__main__':
    main()
#endregion
