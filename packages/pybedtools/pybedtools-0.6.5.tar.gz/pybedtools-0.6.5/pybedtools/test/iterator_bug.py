import os
import sys
"""
I think that iterators are leaking....
"""

import pybedtools
x = pybedtools.example_bedtool('x.bed')

def gen():
    for c, i in enumerate(x):
        y = pybedtools.BedTool([i])
        z = y.intersect(y)
        print "\r%s" % c,
        sys.stdout.flush()
        for k in z:
            yield k
        pybedtools.helpers.close_or_delete(y, z)
        del y.fn
        del z
        del y


x = pybedtools.BedTool(gen()).saveas()
