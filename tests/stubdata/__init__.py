# -*- coding: utf-8 -*-
from collections import OrderedDict
import os

# records exported from the ads/ReadRecordsCached.py
ADSRECORDS = OrderedDict()
_path = os.path.abspath(os.path.join(__file__, '../ADSRecords/'))
for x in os.listdir(_path):
    x = os.path.join(_path, x)
    if not os.path.isfile(x):
        continue
    f = eval(open(x, 'r').read())
    ADSRECORDS[os.path.basename(x)] = f
    

from . import mergerdata  