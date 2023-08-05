"""String formatting"""

__copyright__ = "Copyright (C) 2013 Ivan D Vasin"
__docformat__ = "restructuredtext"

from spruce.pprint import indented as _indented


def indented(string, level=1, size=2):
# TODO (Python 3):
#def indented(string, level=1, *, size=2):
    return _indented(string, level, size=size)
