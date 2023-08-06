#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import os.path
import sys
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from common import BASEPATH, LOG_FILE, LOG_LEVEL
import db
from web import run_standalone #, run_fcgi


########################################################################
try:
    os.mkdir(os.path.join(BASEPATH, 'data'))
except OSError:
    pass
logging.basicConfig(level=LOG_LEVEL,
                    # format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    format='%(asctime)s  %(name)s(%(module)12s:%(lineno)4d)  %(levelname).1s  %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=os.path.join(BASEPATH, LOG_FILE),
                    filemode='w')


########################################################################
os.chdir(os.path.dirname(os.path.abspath(__file__)))
if db.check_exists():
    db.start()
try:
    run_standalone()
except:
    db.close()
    raise
else:
    db.close()


########################################################################
