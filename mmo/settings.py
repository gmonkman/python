# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''settings file, stopped using an ini'''
from os import path as _path
from inspect import getsourcefile as _getsourcefile
import mmo as _mmo
from funclib import iolib as _iolib


_THIS_FILE_PATH = _path.normpath(_iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0])
_MODULE_ROOT = _path.normpath(_mmo.__path__[0]) #root of opencvlib
BIN_FOLDER = _path.normpath(_path.join(_MODULE_ROOT, 'bin'))


class PATHS():
    '''folder settings'''
    NAMED_ENTITIES_ALL = _path.normpath(_path.join(BIN_FOLDER, 'named_entities_all.pkl'))
    NAMED_ENTITIES_ALL_SINGLE = _path.normpath(_path.join(BIN_FOLDER, 'named_entities_all_single.pkl')) #the whitelist of individual words
    LOG_WRITE_HINTS = _path.normpath('c:/temp/log_write_hints.py.log')
    LOG_NAMED_ENTITIES = _path.normpath('c:/temp/log_named_entities.py.log') #currently unused
    NAMED_ENTITIES_DUMP_FOLDER = BIN_FOLDER
    LOG_CLEAN_UGC = _path.normpath('c:/temp/clean_ugc.py.log')
    LOG_CLEAN_GAZ = _path.normpath('c:/temp/clean_gaz.py.log')
    LOG_MAKE_GAZ_WORDCOUNTS = _path.normpath('c:/temp/make_gaz_wordcounts.py.log')
    GAZ_WORDS_BY_WORD_COUNT = _path.normpath(_path.join(BIN_FOLDER, 'gaz_words_by_word_count.pkl'))
    LOG_WRITE_UGC_GAZ = _path.normpath('c:/temp/write_ugc_gaz.py.log')
    GAZETTEERIDS_BY_NAME = _path.normpath(_path.join(BIN_FOLDER, 'gazetteerids_by_name.pkl'))



class UgcHintSettings():
    '''control what hints to run'''
    force_species_catch_hints = False     #very slow
    force_run_month_hints = False
    force_run_season_hints = False
    force_run_platform_hints = False
    force_run_trip_hints = False
    force_run_date_hints = False
    force_run_species_hints = False

    run_species_catch_hints = False     #very slow
    run_month_hints = True
    run_season_hints = True
    run_platform_hints = True
    run_trip_hints = True
    run_date_hints = True
    run_species_hints = True

    TEST_MODE = False #no deletes or writes or processed checks
