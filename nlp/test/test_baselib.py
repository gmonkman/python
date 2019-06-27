# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-variable, unused-import, missing-docstring
'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path
import funclib.iolib as iolib
import nlp
import nlp.baselib as baselib
from nltk.corpus import wordnet as _wordnet
from nlp.baselib import WordnetLexnames as Lexnames

class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.this_file_path = _path.normpath(iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0])
        self.module_root = _path.normpath(nlp.__path__[0]) #root of opencvlib




    #@unittest.skip("Temporaily disabled while debugging")
    def test_similiar(self):
        '''test'''
        s = baselib.lemma_bag_all('two', 'noun.quantity')
        s = baselib.lemma_bag_all('fiday')
        pass

    def test_filter_synsets(self):
        '''test'''
        baselib.prettyprint_synset(['dog', 'cat', 'rabbit'])

        Days = [_wordnet.synset('monday.n.01'), _wordnet.synset('tuesday.n.01'), _wordnet.synset('wednesday.n.01'), _wordnet.synset('thursday.n.01')]
        Pets = [_wordnet.synset('dog.n.01'), _wordnet.synset('cat.n.01'), _wordnet.synset('parrot.n.01'), _wordnet.synset('horse.n.01')]
        Pet = _wordnet.synset('cat.n.01')
        Day = _wordnet.synset('monday.n.01')
        All = Days + Pets
        Family = _wordnet.synset('canine.n.01')
        Out = baselib.filter_synsets(Pets, ('n', 'v'), sim_threshs=0.1, dist_threshs=3, dist_synsets=Family)
        Out = baselib.filter_synsets(Days, ('n', 'v'), sim_threshs=0.1, dist_threshs=3, dist_synsets=Family)
        Out = baselib.filter_synsets(Days, ('n', 'v'), sim_threshs=0.1, dist_threshs=3, dist_synsets=Day)
        s = baselib.common_meaning_bag('wednesday')
        print(s)





if __name__ == '__main__':
    unittest.main(verbosity=2)
