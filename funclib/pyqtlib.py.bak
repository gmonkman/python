#pylint: too-many-branches
import sys
from PyQt4.QtGui import QWidget, QApplication, QMessageBox
from PyQt4 import QtCore


def question(title, msg, default_button = QMessageBox.No, *flags):
    '''(str, str, ints)->QMessageBoxValueEnumeration
    Show a message box
    Ints will be binary ORed to get Yes,No,Ok for example
    Return the result (Eg QMessageBox.Yes)
    '''
    options = _or_flags(flags)
    a = QApplication(sys.argv)
    w = QWidget()
    w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    return QMessageBox.question(w, title, msg, options, default_button)

def _or_flags(flags):
    '''ORs a list of values'''
    b = 0
    for x in flags:
        b = b | x
    return b


def main():
    x = question('Quit this', 'Press yes to quit', QMessageBox.No, QMessageBox.Yes, QMessageBox.No)
    print 'yes' if x == QMessageBox.Yes else 'no'

#This only executes if this script was the entry point
if __name__ == '__main__':
    main()
