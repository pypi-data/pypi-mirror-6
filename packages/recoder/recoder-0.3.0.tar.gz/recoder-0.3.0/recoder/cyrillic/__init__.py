from ..pyver import *

if pyver == 2:
    from recoder import Recoder
elif pyver == 3:
    from  recoder.cyrillic.recoder import Recoder