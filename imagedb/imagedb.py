'''stuff to do with the image database'''
from numpy import array as np_array, linalg

from abc import ABC, abstractmethod


class Fish(ABC):
    '''base class to store samples'''
    def __init__(self, length_tl=0):
        '''init class'''
        self.name_latin = ''
        self.name_common = ''
        self.length_tl = length_tl
        self.length_fl = 0
        self.length_sl = 0
        self.max_ventral_dorsal_thickness = 0


    @abstractmethod
    def get_max_depth(self):
        '''(double)->double
        given the total length, get the depth
        '''

#define an array of functions which will accept other 'species' classes
class FishActions(object):
    '''polymorphic class functions for fish species, aubclassed from Fish'''
    def __init__(self, species):
        '''species is a fish class (polymorphic)
        '''
        self.species = species

    def get_max_depth(self):
        '''get max fish depth based on the length and species
        '''
        return self.species.get_max_depth()

class Bass(Fish):
    '''bass'''

    def __init__(self, length_tl):
        super(Bass, self).__init__(length_tl) #keep python 2.7 compat, Python 3 only would be super().__init__(length_tl)

    def get_max_depth(self):
        '''(float)->float
        given a length in mm, get maximum fish depth in mm
        REF: "Quality outline of European sea bass Dicentrarchus labrax reared in Italy: shelf life, edible yield, nutritional and dietetic traits"
        '''
        a = np_array([[280, 10], [427.5, 10]])
        c = np_array([34.3, 54.3])

        ret = linalg.solve(a, c)
        return self.length_tl*ret[0] + ret[1]





#region ENTRY
def main():
    '''execute if script was entry point'''
    pass

#This only executes if this script was the entry point
if __name__ == '__main__':
    #execute my code
    main()
#endregion
