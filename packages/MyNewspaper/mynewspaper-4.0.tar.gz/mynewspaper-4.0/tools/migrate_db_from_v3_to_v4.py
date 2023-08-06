#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# CAUTION: this script migrates a MyNewspaper database from
#          v3.x to v4.x format

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
import sys
import sqlite3
import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from utils import get_feed_icon


######################################################################
##### Variables
STMT_CREATE_DB = """
CREATE TABLE groups (
    gid INTEGER PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    sort_idx INT,
    num_total INT,
    num_unread INT,
    num_starred INT,
    num_later INT,
    num_archived INT
);

CREATE TABLE feeds (
    fid INTEGER PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    url VARCHAR(255) NOT NULL,
    link VARCHAR(255),
    icon VARCHAR(255),
    state INT,  -- 0:archive, 1:enabled, 2:disabled, 3:broken
    sort_idx INT,
    gid INT,
    etag VARCHAR(255),
    lastupdate VARCHAR(100), -- feed sent timestamp, as string
    artsperhour INT,
    num_total INT,
    num_unread INT,
    num_starred INT,
    num_later INT,
    num_archived INT
);
CREATE INDEX idx_feeds_group ON feeds (gid);

CREATE TABLE articles (
    aid INTEGER PRIMARY KEY,
    uid VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(255),
    url VARCHAR(255),
    contents TEXT,
    timestamp TIMESTAMP,
    state INT,  -- 0:total/delete, 1:unread, 2:starred, 3:later, 4:archived
    fid INT
);
CREATE INDEX idx_articles_uid ON articles (uid);
CREATE INDEX idx_articles_state ON articles (state);
CREATE INDEX idx_articles_feed ON articles (fid);

INSERT INTO groups VALUES (0, 'Uncategorized', 0, 0, 0, 0, 0, 0);
INSERT INTO feeds VALUES (0, 'Archive', '', '', '', 0, 0, -1, '', '', 0, 0, 0, 0, 0, 0);
"""


######################################################################
##### Functions
class Feed:
    def __init__(self, fid, name, link):
        self.fid = fid
        self.name = name
        self.link = link
    def __repr__(self):
        return '<Feed {0.fid}: {0.name}>'.format(self)


def migrate_db(db_old, db_new, add_icons=True):
    db0 = sqlite3.connect(db_old)
    db0.row_factory = sqlite3.Row
    c0 = db0.cursor()
    print('Creating new DB')
    db1 = sqlite3.connect(db_new)
    db1.row_factory = sqlite3.Row
    c1 = db1.cursor()
    c1.executescript(STMT_CREATE_DB)

    print('Migrating Folders')
    c0.execute('SELECT * FROM rss_group')
    for r in c0.fetchall():
        c1.execute('INSERT INTO groups VALUES (?, ?, ?, 0, 0, 0, 0, 0)', (r['id'], r['name'], r['sort_idx']))

    print('Migrating Feeds')
    c0.execute('SELECT * FROM feed')
    for r in c0.fetchall():
        lastupdate = '' # datetime.datetime.strptime(r['lastupdate'], '%Y-%m-%d %H:%M:%S')
        state = 2 if r['disabled'] else 1
        c1.execute('INSERT INTO feeds VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, -1, 0, 0, 0, 0, 0)',
                   (r['id'], r['name'], r['url'], r['link'], '', state, r['sort_idx'],
                    r['rss_group_id'], r['etag'], lastupdate))

    print('Migrating Articles')
    c0.execute('SELECT * FROM article')
    for r in c0.fetchall():
        timestamp = r['timestamp'] + '+00:00'
        if r['state'] == 2: state = 4   # archived
        elif r['state'] == 3: state = 2 # starred
        elif r['state'] == 4: state = 3 # later
        else: state = r['state']
        c1.execute('INSERT INTO articles VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                   (r['id'], r['aid'], r['title'], r['url'], r['contents'],
                    timestamp, state, r['feed_id']))

    print('Fixing numbers')
    ST = ('num_total', 'num_unread', 'num_starred', 'num_later', 'num_archived')
    c1.execute('SELECT fid FROM feeds')
    for r in c1.fetchall():
        for st, it in enumerate(ST):
            if st == 0: continue # num_total
            stmt = 'UPDATE feeds SET %s=(SELECT COUNT(*) FROM articles WHERE fid=? AND state=%d) WHERE fid=?' % (it, st)
            c1.execute(stmt, (r[0], r[0]))
        c1.execute('UPDATE feeds SET num_total=num_unread+num_starred+num_later+num_archived WHERE fid=?', (r[0], ))
    c1.execute('SELECT gid FROM groups')
    for r in c1.fetchall():
        for it in ST:
            stmt = 'UPDATE groups SET %s=(SELECT COALESCE(SUM(%s), 0) FROM feeds WHERE gid=?) WHERE gid=?' % (it, it)
            c1.execute(stmt, (r[0], r[0]))

    if add_icons:
        print('Adding feed icons... be patience, this will take some time')
        c1.execute('SELECT fid, name, link FROM feeds')
        feeds = [Feed(r['fid'], r['name'], r['link']) for r in c1.fetchall()]
        with ThreadPoolExecutor(max_workers=10) as e:
            futures_favicon = {e.submit(get_feed_icon, f): f for f in feeds}
            for future in as_completed(futures_favicon):
                try:
                    feed = futures_favicon[future]
                    icon_url = future.result()
                except Exception as exc:
                    print('Error adding favicon for %s: %s' % (feed, exc))
                else:
                    if icon_url is not None:
                        c1.execute('UPDATE feeds SET icon=? WHERE fid=?', (icon_url, feed.fid))
    else:
        print('Won\'t add feed icons')

    db1.commit()
    c0.close()
    db0.close()
    c1.close()
    db1.close()


def main(db_old, db_new, add_icons=True):
    t0 = time.time()
    print('MyNewspaper DB migration tool v3 -> v4')
    print('---------------------------------------')
    print('Old DB: %s' % db_old)
    print('New DB: %s' % db_new)
    print
    if not os.path.exists(db_old):
        print('Old db file <%s> does not exist' % db_old)
        sys.exit(-1)
    if os.path.exists(db_new):
        os.unlink(db_new)
    migrate_db(db_old, db_new, add_icons)
    tot = time.time() - t0
    if tot > 60:
        print('Migration finished in %d\'%2.2d"' % divmod(tot, 60))
    else:
        print('Migration finished in %d sec' % tot)


######################################################################
##### Main
if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] != sys.argv[2]:
        main(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 4 and sys.argv[1] != sys.argv[2] and sys.argv[3] == '--no-favicons':
        main(sys.argv[1], sys.argv[2], False)
    else:
        print('%s <old.db> <new.db> [--no-favicons]' % sys.argv[0])
        sys.exit(-1)


######################################################################
