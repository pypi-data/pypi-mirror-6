#!/usr/bin/env python3

"""tbar - Terminal Bar

Number to bar in terminal.
"""

__version__ = "0.0.1"

import sys

from tbar.tbar import TBar
from tbar.reader import Reader

def main(infile, comment, sep, field, regexp,
         max, length, vertical):
    infile = infile or sys.stdin
    r = Reader(infile=infile, comment=comment, sep=sep, field=field,
               regexp=regexp)
    b = TBar(_max=max, length=length, vertical=vertical)
    b.add_data_itr(r.data)

    s = str(b)
    if s:
        print(s)
    else:
        print("No data.")
    return
