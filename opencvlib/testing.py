#pylint: skip-file

import sys
import opencvlib.digikamlib as digikamlib

def main():
    dbpath = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/digikam4.db'
    bass = digikamlib.ImagePaths(dbpath)
    lst = bass.ImagesByTags(species='bass')
    print(str(len(lst)))
    pass

if __name__ == "__main__":
    main()
    sys.exit(int(main() or 0))
