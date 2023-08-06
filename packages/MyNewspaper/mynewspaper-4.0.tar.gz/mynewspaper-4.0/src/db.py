# -*- coding: utf-8 -*-

import os
import os.path
import time
import datetime
import shelve
import sqlite3
from shutil import rmtree

from utils import get_feed_icon, extract_summary, remove_dirty_tags, dbtime2dt_local, dt2local
from common import *


########################################################################
##### Globals
DBFILE = 'data/mynewspaper.db'
CACHEFILE = 'data/mynewspaper.cache'
DBFILE_fullpath = os.path.join(BASEPATH, DBFILE)
CACHEFILE_fullpath = os.path.join(BASEPATH, CACHEFILE)

db = None

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


########################################################################
##### DB Exceptions
class DBInvalidException(Exception): pass
class DBGroupNotExistException(Exception): pass
class DBFeedNotExistException(Exception): pass
class DBArticleNotExistException(Exception): pass
class DBMalformedArticleProcessingValue(Exception): pass


########################################################################
##### DataBase
class MNDataBase:
    def __init__(self):
        self.connect()

    def init_schema(self):
        assert self.conn is not None
        log.info('Creating DB "%s"' % DBFILE)
        try:
            self.conn.executescript(STMT_CREATE_DB)
            self.conn.commit()
        except sqlite3.OperationalError:
            raise DBInvalidException

    def connect(self):
        log.info('Connecting to DB "%s"' % DBFILE)
        # self.conn = sqlite3.connect(DBFILE_fullpath, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.conn = sqlite3.connect(DBFILE_fullpath)
        self.conn.row_factory = sqlite3.Row
        # self.conn.create_function('startswith', 2, startswith)
        self.cur = self.conn.cursor()
        self.cache = shelve.open(CACHEFILE_fullpath) # {article.uid: secs_from_epoch}
        try:
            os.makedirs(os.path.join(BASEPATH, 'data', 'favicons'))
        except OSError:
            pass

    def close(self):
        global db
        log.info('Closing DB "%s"' % DBFILE)
        self.conn.commit()
        self.cur.close()
        self.conn.close()
        self.conn = self.cur = db = None
        self.cache.close()

    def destroy(self):
        self.close()
        log.info('Destroying DB "%s"' % DBFILE)
        try:
            os.unlink(DBFILE_fullpath)
            os.unlink(CACHEFILE_fullpath)
            rmtree(os.path.join(BASEPATH, 'data', 'favicons'), ignore_errors=True)
        except OSError:
            pass

    def commit(self):
        self.conn.commit()

    def vacuum(self):
        log.info('Vacuum database')
        self.cur.execute('VACUUM')
        self.conn.commit()

    def clear_old_articles_from_cache(self, nmonths):
        log.info('Removing from cache entries older than {} months'.format(nmonths))
        m3 = datetime.datetime.now() - datetime.timedelta(nmonths*365/12)
        t3 = time.mktime(m3.timetuple())
        ids_todelete = [eid for eid, t in self.cache.items() if t < t3]
        for eid in ids_todelete:
            del self.cache[eid]
        # HACK: del doesn't reduce file size so we need to rewrite the file
        tmp_cache = shelve.open(CACHEFILE_fullpath+'.tmp')
        for eid, t in self.cache.items():
            tmp_cache[eid] = t
        tmp_cache.close()
        self.cache.close()
        os.unlink(CACHEFILE_fullpath)
        os.rename(CACHEFILE_fullpath+'.tmp', CACHEFILE_fullpath)
        self.cache = shelve.open(CACHEFILE_fullpath)


def start():
    global db
    db = MNDataBase()

def commit():
    db.commit()

def close():
    db.close()

def destroy():
    db.destroy()

def vacuum():
    db.vacuum();

def is_entry_in_cache(eid, dt):
    if eid in db.cache:
        return True
    else:
        db.cache[eid] = time.mktime(dt.timetuple())
        return False

def clear_old_articles_from_cache(nmonths=3):
    db.clear_old_articles_from_cache(nmonths)

def check_exists():
    return os.path.exists(DBFILE_fullpath)


########################################################################
##### Group
GROUP_COLS = ('gid', 'name', 'sort_idx', 'num_total', 'num_unread', 'num_starred', 'num_later', 'num_archived')

class Group:
    __slots__ = GROUP_COLS

    def __init__(self):
        self.gid = -1
        self.name = ''
        self.sort_idx = -1
        self.num_total = 0
        self.num_unread = 0
        self.num_starred = 0
        self.num_later = 0
        self.num_archived = 0

    def __repr__(self):
        return '<Group {0.gid}: {0.name}>'.format(self)

    def from_data(self, name):
        self.name = name
        return self

    def from_dbrow(self, row):
        if row is None:
            raise DBGroupNotExistException
        for i, colname in enumerate(GROUP_COLS):
            self.__setattr__(colname, row[i])
        return self

    def to_dbrow(self):
        assert self.name != ''
        db.cur.execute('INSERT INTO groups VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                       (None, self.name, self.sort_idx,
                        self.num_total, self.num_unread, self.num_starred, self.num_later, self.num_archived))
        self.gid = self.sort_idx = db.cur.lastrowid
        self.update_fields({'sort_idx': self.sort_idx})

    def get_by_id(self, gid):
        db.cur.execute('SELECT * FROM groups WHERE gid=?', (gid, ))
        return self.from_dbrow(db.cur.fetchone())

    def get_by_name(self, name):
        db.cur.execute('SELECT * FROM groups WHERE name=?', (name, ))
        return self.from_dbrow(db.cur.fetchone())

    def update_fields(self, kwargs, delay_commit=False):
        lst_keys, lst_values = [], []
        for k, v in kwargs.items():
            if k in GROUP_COLS:
                self.__setattr__(k, v)
                lst_keys.append('{}=?'.format(k))
                lst_values.append(v)
        args = tuple(lst_values + [self.gid])
        db.cur.execute('UPDATE groups SET %s WHERE gid=?' % ','.join(lst_keys), args)
        if not delay_commit:
            db.commit()

    def get_feeds(self, sort=True, only_enabled=True):
        stmt = 'SELECT * FROM feeds WHERE gid=?'
        stmt = stmt + ' AND state=%s' % FEED_ENABLED if only_enabled else stmt
        stmt = stmt + ' ORDER BY sort_idx' if sort else stmt
        db.cur.execute(stmt, (self.gid, ))
        return [Feed().from_dbrow(row) for row in db.cur.fetchall()]
        # for row in db.cur.fetchall():
        #     yield Feed().from_dbrow(row)

    def sort_feeds(self, pos):
        for idx, fid in enumerate(pos):
            Feed().get_by_id(fid).update_fields({'sort_idx': idx}, delay_commit=True)
        db.commit()

    def resort_feeds(self):
        for i, f in enumerate(self.get_feeds(sort=True, only_enabled=False)):
            f.update_fields({'sort_idx': i}, delay_commit=True)
        db.commit()

    def get_articles(self, state=TOTAL, sort=SORT_DATENEW_FEED, offset=0, limit=0):
        cl_state, cl_sort, cl_nums = _build_select_arts_clauses(state, sort, offset, limit)
        cl_group = ' AND fid in (SELECT fid FROM feeds WHERE gid=?)'
        stmt = 'SELECT COUNT(*) FROM articles' + cl_state + cl_group
        db.cur.execute(stmt, (self.gid, ))
        num_total = db.cur.fetchone()[0]
        stmt = 'SELECT * FROM articles' + cl_state  + cl_group + cl_sort + cl_nums
        db.cur.execute(stmt, (self.gid, ))
        arts = _rows2articles()
        return (len(arts), num_total, arts)

    def get_nums(self):
        return [self.num_total, self.num_unread, self.num_starred, self.num_later, self.num_archived]


def group_new(name):
    i = 0
    while True:
        newname = name if i == 0 else '%s-%d' % (name, i)
        try:
            group = Group().get_by_name(newname)
        except DBGroupNotExistException:
            group = Group().from_data(newname)
            group.to_dbrow()
            db.commit()
            log.info('Group created: ' + str(group))
            return group
        else:
            i += 1


def check_groupname_exists(groupname):
    for g in get_groups(False):
        if g.name == groupname:
            return True
    else:
        return False


def group_delete(gid, move_arts):
    g = Group().get_by_id(gid)
    if gid == 0 or g is None: # Don't delete "Uncategorized"
        return
    if move_arts:
        # sqlite doesn't support left join in update clauses, so we have to do in 2 steps
        for f in g.get_feeds(False, False):
            db.cur.execute('UPDATE articles SET title=? || ": " || title WHERE fid=?', (f.name, f.fid))
            log.info('Feed deleted: ' + str(f))
        db.cur.execute('UPDATE articles SET fid=0 WHERE fid IN (SELECT fid FROM feeds WHERE gid=?)', (gid, ))
    else:
        db.cur.execute('DELETE FROM articles WHERE fid IN (SELECT fid FROM feeds WHERE gid=?)', (gid, ))
    db.cur.execute('DELETE FROM feeds WHERE fid IN (SELECT fid FROM feeds WHERE gid=?)', (gid, ))
    db.cur.execute('DELETE FROM groups WHERE gid=?', (gid, ))
    log.info('Group deleted: ' + str(g))
    for i, g in enumerate(get_groups(sort=True)):
        g.update_fields({'sort_idx': i}, delay_commit=True)
    update_numbers(delay_commit=False)


def get_groups(sort=True):
    stmt = 'SELECT * FROM groups'
    stmt = stmt + ' ORDER BY sort_idx' if sort else stmt
    db.cur.execute(stmt)
    return [Group().from_dbrow(row) for row in db.cur.fetchall()]
    # for row in db.cur.fetchall():
    #     yield Group().from_dbrow(row)


def sort_groups(pos):
    for idx, gid in enumerate(pos):
        g = Group().get_by_id(gid)
        g.update_fields({'sort_idx': idx}, delay_commit=True)
    db.commit()


def get_feeds(sort=True, only_enabled=True):
    for g in get_groups(sort):
        for f in g.get_feeds(sort, only_enabled):
            yield f


def get_num_groups():
    db.cur.execute('SELECT count(*) FROM groups')
    return db.cur.fetchone()[0] # 'Uncategorized' included


def get_num_feeds():
    db.cur.execute('SELECT count(*) FROM feeds')
    return db.cur.fetchone()[0] - 1 # 'archive'


def get_num_feeds_extra():
    db.cur.execute('SELECT count(*) FROM feeds')
    nfeeds = db.cur.fetchone()[0] - 1 # 'archive'
    db.cur.execute('SELECT count(*) FROM feeds WHERE state=?', (FEED_DISABLED, ))
    nfeeds_disabled = db.cur.fetchone()[0]
    db.cur.execute('SELECT count(*) FROM feeds WHERE state=?', (FEED_BROKEN, ))
    nfeeds_broken = db.cur.fetchone()[0]
    nfeeds_inactive = 0 # TODO: get feeds without new posts in last X days
    return (nfeeds, nfeeds_disabled, nfeeds_broken, nfeeds_inactive)


def get_nums(only_enabled=True):
    nums = [0, 0, 0, 0, 0]
    for g in get_groups(False):
        db.cur.execute('SELECT num_total, num_unread, num_starred, num_later, num_archived FROM groups WHERE gid=?', (g.gid, ))
        row = db.cur.fetchone()
        nums = [nums[i]+row[i] for i in range(len(nums))]
    return nums


def get_lastupdate():
    db.cur.execute('SELECT lastupdate FROM feeds')
    dt_lastupdate = datetime.datetime(2000, 1, 1)
    for s in db.cur.fetchall():
        try:
            dt = datetime.datetime.strptime(s['lastupdate'], '%a, %d %b %Y %H:%M:%S GMT')
        except ValueError:
            dt = datetime.datetime(2000, 1, 1)
        if dt > dt_lastupdate:
            dt_lastupdate = dt
    return dt2local(dt_lastupdate).strftime('%A %d %B %Y, %H:%M:%S')


def get_articles(state=TOTAL, sort=SORT_DATENEW_FEED, offset=0, limit=0):
    cl_state, cl_sort, cl_nums = _build_select_arts_clauses(state, sort, offset, limit)
    db.cur.execute('SELECT COUNT(*) FROM articles' + cl_state)
    num_total = db.cur.fetchone()[0]
    stmt = 'SELECT * FROM articles' + cl_state + cl_sort + cl_nums
    db.cur.execute(stmt)
    arts = _rows2articles()
    return (len(arts), num_total, arts)


def update_numbers(delay_commit=True):
    ST = ('num_total', 'num_unread', 'num_starred', 'num_later', 'num_archived')
    db.cur.execute('SELECT fid FROM feeds')
    for r in db.cur.fetchall():
        for st, it in enumerate(ST):
            if st == 0: continue # num_total
            stmt = 'UPDATE feeds SET %s=(SELECT COUNT(*) FROM articles WHERE fid=? AND state=%d) WHERE fid=?' % (it, st)
            db.cur.execute(stmt, (r[0], r[0]))
        db.cur.execute('UPDATE feeds SET num_total=num_unread+num_starred+num_later+num_archived WHERE fid=?', (r[0], ))
    db.cur.execute('SELECT gid FROM groups')
    for r in db.cur.fetchall():
        for it in ST:
            stmt = 'UPDATE groups SET %s=(SELECT COALESCE(SUM(%s), 0) FROM feeds WHERE gid=?) WHERE gid=?' % (it, it)
            db.cur.execute(stmt, (r[0], r[0]))
    if not delay_commit:
        db.commit()


########################################################################
##### Feed
FEED_COLS = ('fid', 'name', 'url', 'link', 'icon', 'state', 'sort_idx', 'gid',
             'etag', 'lastupdate', 'artsperhour',
             'num_total', 'num_unread', 'num_starred', 'num_later', 'num_archived')

class Feed:
    __slots__ = FEED_COLS

    def __init__(self):
        self.fid = -1
        self.name = self.url = self.link = self.icon = ''
        self.state = FEED_ENABLED
        self.sort_idx = -1
        self.gid = -1
        self.etag = ''
        self.lastupdate = ''
        self.artsperhour = -1
        self.num_total = 0
        self.num_unread = 0
        self.num_starred = 0
        self.num_later = 0
        self.num_archived = 0

    def __repr__(self):
        return '<Feed {0.fid}: {0.name}>'.format(self)

    def from_data(self, name, url, link, gid):
        self.name = name
        self.url = url
        self.link = link
        self.gid = gid
        return self

    def from_dbrow(self, row):
        if row is None:
            raise DBFeedNotExistException
        for i, colname in enumerate(FEED_COLS):
            self.__setattr__(colname, row[i])
        return self

    def to_dbrow(self):
        assert self.name != ''
        db.cur.execute('INSERT INTO feeds VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (None, self.name, self.url, self.link, self.icon, self.state,
                        self.sort_idx, self.gid, self.etag, self.lastupdate, self.artsperhour,
                        self.num_total, self.num_unread, self.num_starred, self.num_later, self.num_archived))
        self.fid = self.sort_idx = db.cur.lastrowid
        self.update_fields({'sort_idx': self.sort_idx})

    def get_by_id(self, fid):
        db.cur.execute('SELECT * FROM feeds WHERE fid=?', (fid, ))
        return self.from_dbrow(db.cur.fetchone())

    def get_by_name(self, name):
        db.cur.execute('SELECT * FROM feeds WHERE name=?', (name, ))
        return self.from_dbrow(db.cur.fetchone())

    def get_by_url(self, url):
        db.cur.execute('SELECT * FROM feeds WHERE url=?', (url, ))
        return self.from_dbrow(db.cur.fetchone())

    def update_fields(self, kwargs, delay_commit=False):
        lst_keys, lst_values = [], []
        for k, v in kwargs.items():
            if k in FEED_COLS:
                self.__setattr__(k, v)
                lst_keys.append('{}=?'.format(k))
                lst_values.append(v)
        args = tuple(lst_values + [self.fid])
        db.cur.execute('UPDATE feeds SET %s WHERE fid=?' % ','.join(lst_keys), args)
        if not delay_commit:
            db.commit()

    def get_articles(self, state=TOTAL, sort=SORT_DATENEW_FEED, offset=0, limit=0):
        cl_state, cl_sort, cl_nums = _build_select_arts_clauses(state, sort, offset, limit)
        cl_feed = ' AND fid=?'
        stmt = 'SELECT COUNT(*) FROM articles' + cl_state + cl_feed
        db.cur.execute(stmt, (self.fid, ))
        num_total = db.cur.fetchone()[0]
        stmt = 'SELECT * FROM articles' + cl_state  + cl_feed + cl_sort + cl_nums
        db.cur.execute(stmt, (self.fid, ))
        arts = _rows2articles()
        return (len(arts), num_total, arts)


def feed_new(name, url, link, gid, delay_icon=False):
    i = 0
    while True:
        newname = name if i == 0 else '%s-%d' % (name, i)
        try:
            feed = Feed().get_by_name(newname)
        except DBFeedNotExistException:
            feed = Feed().from_data(newname, url, link, gid)
            if not delay_icon:
                feed.icon = get_feed_icon(feed)
            feed.to_dbrow()
            db.commit()
            log.info('Feed created: ' + str(feed))
            return feed
        else:
            i += 1


def check_feedname_exists(feedname, fid):
    for f in get_feeds(False, False):
        if f.name==feedname and f.fid!=fid:
            return True
    else:
        return False


def feed_delete(fid, move_arts):
    f = Feed().get_by_id(fid)
    if fid == 0 or f is None: # Don't delete "Archive"
        return
    g = Group().get_by_id(f.gid)
    if move_arts:
        db.cur.execute('UPDATE articles SET fid=0, title=? || ": " || title  WHERE fid=?', (f.name, fid))
    else:
        db.cur.execute('DELETE FROM articles WHERE fid=?', (fid, ))
    db.cur.execute('DELETE FROM feeds WHERE fid=?', (fid, ))
    try:
        os.unlink(os.path.join(BASEPATH, 'data', 'favicon', '%d.png' % fid))
    except OSError:
        pass
    log.info('Feed deleted: ' + str(f))
    for i, f in enumerate(g.get_feeds(sort=True, only_enabled=False)):
        f.update_fields({'sort_idx': i}, delay_commit=True)
    update_numbers(delay_commit=False)


########################################################################
##### Article
ARTICLE_COLS = ('aid', 'uid', 'title', 'url', 'contents', 'timestamp', 'state', 'fid')

class Article:
    __slots__ = tuple(list(ARTICLE_COLS) + ['feedname', 'feedlink', 'summary', 'timestamp2'])

    def __init__(self):
        self.aid = -1
        self.uid = self.title = self.url = self.contents = ''
        self.timestamp = None
        self.state = UNREAD
        self.fid = -1
        self.feedname = self.feedlink = self.summary = self.timestamp2 = ''

    def __repr__(self):
        return '<Article {0.aid}: {0.title}>'.format(self)

    def from_data(self, uid, title, url, contents, timestamp, fid, state=UNREAD):
        self.uid = uid
        self.title = title
        self.url = url
        self.contents = contents
        self.timestamp = timestamp
        self.state = state
        self.fid = fid
        return self

    def to_dbrow(self):
        assert self.title != ''
        db.cur.execute('INSERT INTO articles VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                       (None, self.uid, self.title, self.url, self.contents,
                        self.timestamp, self.state, self.fid))
        self.aid = db.cur.lastrowid

    def from_dbrow(self, row):
        if row is None:
            raise DBArticleNotExistException
        for i, colname in enumerate(ARTICLE_COLS):
            self.__setattr__(colname, row[i])
        return self

    def get_by_id(self, aid):
        db.cur.execute('SELECT * FROM articles WHERE aid=?', (aid, ))
        return self.from_dbrow(db.cur.fetchone())

    def get_by_uid(self, uid):
        db.cur.execute('SELECT * FROM articles WHERE uid=?', (uid, ))
        return self.from_dbrow(db.cur.fetchone())


def article_new(uid, title, url, contents, timestamp, fid, state=UNREAD, delay_commit=False):
    try:
        art = Article().get_by_uid(uid)
    except DBArticleNotExistException:
        art = Article().from_data(uid, title, url, remove_dirty_tags(contents), timestamp, fid, state)
        art.to_dbrow()
        if not delay_commit:
            db.commit()
        return art
    else:
        return None


def process_articles(arts):
    try:
        for item in arts.split(','):
            aid, st = item.split(':')
            aid, st = int(aid), int(st)
            assert st in range(5)
            if st == 0: # delete
                db.cur.execute("DELETE FROM articles WHERE aid=?", (aid, ))
            else: # change state
                db.cur.execute('UPDATE articles SET state=? WHERE aid=?', (st, aid))
    except:
        log.error('Malformed articles processing value from web')
        raise DBMalformedArticleProcessingValue
    else:
        update_numbers()
        # vacuum() # FIXME: do this in cron
        db.commit()


########################################################################
##### Misc
def _build_select_arts_clauses(state, sort, offset, limit):
    if state == TOTAL:
        clause_state = ' WHERE 1=1' # needed because " AND gid=?"
    else:
        clause_state = ' WHERE state=%d' % state
    if sort == SORT_DATENEW_FEED:
        clause_sort = ' ORDER BY timestamp DESC, fid'
    elif sort == SORT_DATEOLD_FEED:
        clause_sort = ' ORDER BY timestamp ASC, fid'
    elif sort == SORT_FEED_DATENEW:
        clause_sort = ' ORDER BY fid, timestamp DESC'
    elif sort == SORT_FEED_DATEOLD:
        clause_sort = ' ORDER BY fid, timestamp ASC'
    else:
        clause_sort = ''
    if limit==0 and offset==0:
        clause_nums = ''
    else:
        clause_nums = ' LIMIT %d OFFSET %d' % (limit, offset)
    return clause_state, clause_sort, clause_nums


def _rows2articles():
    arts = []
    for row in db.cur.fetchall():
        a = Article().from_dbrow(row)
        f = Feed().get_by_id(a.fid)
        a.summary = extract_summary(a.contents)
        a.feedname = f.name
        a.feedlink = f.link
        a.fid = f.fid
        a.timestamp = dbtime2dt_local(a.timestamp, short=True)
        a.timestamp2 = dbtime2dt_local(a.timestamp, short=False)
        arts.append(a)
    return arts

########################################################################
