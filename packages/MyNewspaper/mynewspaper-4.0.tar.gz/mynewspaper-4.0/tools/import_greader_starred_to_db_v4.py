#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# CAUTION: this script import starred items from Google Reader takeout file
#          to MyNewspaper database v4.x format

# Copyright (C) 2013  Iñigo Serna
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.


__author__ = 'Iñigo Serna'
__revision__ = '1.0'


import os
import os.path
import logging
import sys
import time
from zipfile import ZipFile, BadZipFile

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
import db
from common import BASEPATH, LOG_FILE, LOG_LEVEL
from opml import import_starred_from_googlereader


logging.basicConfig(level=LOG_LEVEL,
                    # format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    format='%(asctime)s  %(name)s(%(module)12s:%(lineno)4d)  %(levelname).1s  %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=os.path.join(BASEPATH, LOG_FILE),
                    filemode='w')


######################################################################
##### Code
def import_starred(takeout):
    db.start()
    try:
        with ZipFile(takeout) as zf:
            starredfile = None
            for f in zf.namelist():
                if f.endswith('starred.json'):
                    starredfile = f
            if starredfile:
                import_starred_from_googlereader(zf.read(starredfile))
            return True
    except BadZipFile:
        return False
    db.update_numbers(delay_commit=False)
    db.close()


def main(takeout):
    t0 = time.time()
    print('Importing starred items from GoogleReader Takeout file to MyNewspaper DB')
    print('------------------------------------------------------------------------')
    print('Google takeout file: %s' % takeout)
    print
    if not db.check_exists():
        print('MyNewspaper Database does not exist')
        sys.exit(-1)
    if not os.path.exists(takeout):
        print('Google Takeout file <%s> does not exist' % takeout)
        sys.exit(-1)
    if not import_starred(takeout):
        print('Error while importing')
    tot = time.time() - t0
    if tot > 60:
        print('Finished in %d\'%2.2d"' % divmod(tot, 60))
    else:
        print('Finished in %d sec' % tot)


######################################################################
##### Main
if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print('%s <google-takeout.zip>' % sys.argv[0])
        sys.exit(-1)


######################################################################
