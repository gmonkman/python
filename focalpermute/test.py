#pylint: skip-file
'''test stuff focalpermute'''

import numpy as np
import focalpermute.mediandistance
import focalpermute as fp

#region mediandistance
def median_distance():
    a = numpy.arange(25).reshape(5,5).astype(float)
    a[0][0] = numpy.nan
    a[0][1] = 0
    focalpermute.mediandistance.bin_array_quartile(a)
    print a
    z=1
#endregion




median_distance()