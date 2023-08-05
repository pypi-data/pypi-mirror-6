# -*- coding: utf8 - *-
"""For accessing vcspull as a package.

vcspull
~~~~~~~

:copyright: Copyright 2013 Tony Narlock.
:license: BSD, see LICENSE for details

"""

import sys
import os


def run():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, base)
    import vcspull
    vcspull.cli.main()

if __name__ == '__main__':
    exit = run()
    if exit:
        sys.exit(exit)
