"""XCheck
XMLChecker objects that can validate text, xml-formatted text,
or an elementtree.ElementTree node. XCheck objects can also
return checked data in a normalized form (BoolCheck, for example,
returns Boolean values, IntCheck returns an integer)

"""
__version__ = '0.7.0'

__rev__ = 19

from core import *
from textcheck import TextCheck, EmailCheck, URLCheck
from boolcheck import BoolCheck
from listcheck import NoSelectionError, BadSelectionsError
from listcheck import SelectionCheck, ListCheck
from numbercheck import IntCheck, DecimalCheck
from datetimecheck import DatetimeCheck
from wrap import Wrap
from loader import load_checker

from infinity import INF, NINF

import utils

if __name__=='__main__':
    print dir()