
from _xboard_list import xbrd
#from _aboard_list import abrd

# list of boards with default pin mappings

def get_boards(name=None):
    if xbrd.has_key(name):
        pass
    else:
        raise ValueError("Invalid board %s"%(name))
