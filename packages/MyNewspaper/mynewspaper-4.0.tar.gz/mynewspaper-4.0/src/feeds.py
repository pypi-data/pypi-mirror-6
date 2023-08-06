# -*- coding: utf-8 -*-

import time
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

import misc.feedparser as feedparser
from misc.dateutil.parser import parse as dateutil_parse

import db
import utils
from common import *


########################################################################
socket.setdefaulttimeout(TIMEOUT_WEB)


########################################################################
##### Add subscription
def feed_add(link, gid=0):
    url = utils.get_feed_in_web(link)
    if url is None:
        url = link
    try:
        cts = feedparser.parse(url)
    except:
        return None
    if not cts or not cts.has_key('feed') or (cts.has_key('feed') and cts.feed==dict()) or \
       not cts.has_key('entries') or (cts.has_key('entries') and cts.entries==[]) or \
       (cts.has_key('status') and cts.status==404):
        return None
    title = cts.feed.title if cts.feed.has_key('title') else 'no title'
    link = cts.feed.link if cts.feed.has_key('link') else 'no link'
    f = db.feed_new(title, url, link, gid, delay_icon=False)
    update_feeds([f])
    return f


########################################################################
##### Update feeds
def update_feeds(feeds):
    log.info('START Updating feeds')
    with ThreadPoolExecutor(max_workers=NUMTHREADS_UPDATE_FEEDS) as e:
        futures_rss = {e.submit(parse_feed, f): f for f in feeds if f.state in (FEED_ENABLED, FEED_BROKEN)}
        for future in as_completed(futures_rss):
            try:
                feed = futures_rss[future]
                ok, cts = future.result()
            except Exception as exc:
                log.error('Error updating feed {}: {}'.format(feed, exc))
            else:
                if ok:
                    # log.info('Updating ' + str(feed))
                    feed.state = FEED_ENABLED
                    do_update_feed(feed, cts)
                else:
                    feed.state = FEED_BROKEN
                    feed.lastupdate = time.asctime(time.gmtime()) + ' GMT'
                    feed.update_fields({'state': feed.state, 'lastupdate': feed.lastupdate})
                    log.warning('Update {}: FEED BROKEN {}\n{}'.format(feed, feed.url, str(cts)))
    db.update_numbers(delay_commit=False)
    log.info('END Updating feeds')


def parse_feed(feed):
    try:
        # we pass modified and etag to avoid unnecessary downloads
        # as http://feedparser.org/docs/http-etag.html
        cts = feedparser.parse(feed.url, etag=feed.etag, modified=feed.lastupdate)
    except Exception as err:
        return False, err
    else:
        if not cts:
            return False, 'No contents'
        else:
            if (cts.has_key('status') and cts.status==404):
                return False, 'No feed here'
            else:
                return True, cts


def do_update_feed(feed, r):
    # if feed not changed => return 0
    if (r.has_key('status') and r.status==304) or not r.entries:
        log.debug('Update {}: feed not changed'.format(feed))
        return 0

    # if feed lastime_update <= stored value: nothing changed => return 0
    try: # r.has_key('updated') doesn't detect 'modified' or 'published'
        _ = r.updated
    except AttributeError:
        r.updated = time.asctime(time.gmtime()) + ' GMT'
        r.updated_parsed = dateutil_parse(r.updated, fuzzy=True).timetuple()
        log.debug('Update {}: NO attr feed.updated - {}'.format(feed, feed.url))
    if feed.lastupdate:
        stored_lastupdate_parsed = dateutil_parse(feed.lastupdate, fuzzy=True).timetuple()
        if stored_lastupdate_parsed >= r.updated_parsed:
            log.debug('Update {}: feed already updated in db'.format(feed))
            return 0

    # new entries, so process new articles
    new = 0
    for e in r.entries:
        try:
            if not e.has_key('id'):
                e.id = e.link
            if not e.has_key('summary'):
                e.summary = ''
            try: # e.has_key('updated') doesn't detect 'modified' or 'published'
                _ = e.updated
            except AttributeError:
                e.updated = time.asctime(time.gmtime()) + ' GMT'
                # e.updated_parsed = dateutil_parse(e.updated, fuzzy=True).timetuple()
            dt = utils.time2dt_utc(e.updated) # normalize timestamp to utc
            if db.is_entry_in_cache(e.id, dt):
                log.debug('Update {}: "{}" article in cache'.format(feed, e.title))
                continue
            title = e.author+': '+e.title if e.has_key('author') else e.title
            a = db.article_new(e.id, title, e.link, e.summary, dt, feed.fid, state=UNREAD, delay_commit=True)
            if not a:
                log.debug('Update {}: "{}" article already in db'.format(feed, e.title))
        except Exception as err:
            log.error('Update {}: malformed entry - {}\n{}'.format(feed, feed.url, str(err)))
            continue
        else:
            new += 1

    # update feed attributes
    if new > 0:
        etag = 'none' if not r.has_key('etag') else r.etag
        # TODO: artsperhour, feed_arts_numbers
        feed.update_fields({'etag': etag, 'lastupdate': r.updated})
    return new


########################################################################
##### Feeds favicons
def fetch_feeds_icon(feeds):
    with ThreadPoolExecutor(max_workers=NUMTHREADS_FETCH_ICONS) as e:
        futures_iconurl = {e.submit(utils.get_feed_icon, f): f for f in feeds}
        for future in as_completed(futures_iconurl):
            try:
                feed = futures_iconurl[future]
                icon_url = future.result()
            except Exception as exc:
                log.error('Error fetching favicon for {}: {}'.format(feed, exc))
            else:
                if icon_url:
                    feed.update_fields({'icon': icon_url}, delay_commit=True)
    db.commit()


########################################################################
