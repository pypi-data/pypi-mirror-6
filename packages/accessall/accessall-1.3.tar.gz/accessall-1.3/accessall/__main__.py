"""A tool for accessing stuff on google music!

Usage:
  accessall export USER
  accessall download ARTIST ALBUM SONG

"""
import sys
from docopt import docopt
from .accessall import main


if __name__ == '__main__':
    args = docopt(__doc__, version='accessall 1.0')
    sys.exit(main(args))
