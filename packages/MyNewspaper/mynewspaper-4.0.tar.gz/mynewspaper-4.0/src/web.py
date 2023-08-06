import os
import os.path
import datetime
from tempfile import TemporaryDirectory
from concurrent.futures import ThreadPoolExecutor

import misc.bottle as bottle

import db
from feeds import update_feeds, feed_add
from utils import dbtime2dt_local, url_download_as, extract_summary
from opml import import_opml, import_from_googlereader, export_opml
from common import *


########################################################################
##### web app
app = bottle.Bottle()


########################################################################
##### error and static contents
@app.error(404)
def error404(error):
    return bottle.template('error404')

@app.route('/docs/<filename>')
def serve_docs(filename):
    return bottle.static_file(filename, root=os.path.join(BASEPATH, 'docs'))

@app.route('/favicon.ico')
def serve_favicon():
    return bottle.static_file('favicon.ico', root=os.path.join(BASEPATH, 'images'))

@app.route('/images/<filename>')
def serve_images(filename):
    return bottle.static_file(filename, root=os.path.join(BASEPATH, 'images'))

@app.route('/static/<filename>')
def serve_static(filename):
    return bottle.static_file(filename, root=os.path.join(BASEPATH, 'static'))

@app.route('/favicon/<fid:int>')
def serve_feed_favicon(fid):
    favicon = os.path.join(BASEPATH, 'data', 'favicons', '%d.png' % fid)
    if not os.path.exists(favicon):
        try:
            icon_url = db.Feed().get_by_id(fid).icon
        except db.DBFeedNotExistException:
            return bottle.static_file('default_favicon.ico', root=os.path.join(BASEPATH, 'images'))
        else:
            with ThreadPoolExecutor(max_workers=1) as e:
                e.submit(url_download_as, icon_url, favicon)
            return bottle.static_file('default_favicon.ico', root=os.path.join(BASEPATH, 'images'))
    return bottle.static_file('%d.png' % fid, root=os.path.join(BASEPATH, 'data', 'favicons'))


########################################################################
##### main
@app.route('/')
def root():
    if db.check_exists():
        return bottle.template('web_base', dict(wis='h/0/0'))
    else:
        bottle.redirect('/wizard')

@app.route('/summary/group/<gid:int>')
def summary_group(gid=-1):
    if gid != -1:
        try:
            g = db.Group().get_by_id(gid)
        except db.DBGroupNotExistException:
            bottle.abort(404, 'Nothing here')
    return bottle.template('web_base', dict(wis='t/0/{}'.format(gid)))

@app.route('/summary/feed/<fid:int>')
def summary_feed(fid=0):
    try:
        f = db.Feed().get_by_id(fid)
    except db.DBFeedNotExistException:
        bottle.abort(404, 'Nothing here')
    return bottle.template('web_base', dict(wis='t/1/{}'.format(fid)))

@app.route('/articles/<w:re:[agf]>/<i:int>/<st:int>')
def articles(w='a', i=0, st=UNREAD):
    if not 0 <= st < MAX_STATE:
        bottle.abort(404, 'Nothing here')
    if w not in 'agf':
        bottle.abort(404, 'Nothing here')
    if w == 'g':
        try:
            g = db.Group().get_by_id(i)
        except db.DBGroupNotExistException:
            bottle.abort(404, 'Nothing here')
    elif w == 'f':
        try:
            f = db.Feed().get_by_id(i)
        except db.DBFeedNotExistException:
            bottle.abort(404, 'Nothing here')
    return bottle.template('web_base', dict(wis='{}/{}/{}'.format(w, i, st)))

@app.route('/update')
def update():
    update_feeds(db.get_feeds(False))
    return 'Finished updating feeds at ' + str(datetime.datetime.now())


########################################################################
##### admin
@app.route('/wizard')
def wizard():
    if db.check_exists():
        bottle.redirect('/')
    else:
        return bottle.template('wizard', dict())

@app.post('/do_wizard')
def do_wizard():
    val = bottle.request.forms.get('init_feeds')
    if val == 'blank':
        db.start()
        db.db.init_schema()
        bottle.redirect('/')
    elif val == 'opml':
        upload = bottle.request.files.getunicode('opmlfile')
        db.start()
        db.db.init_schema()
        do_import_opml(upload, from_wizard=True)
    elif val == 'googlereader':
        upload = bottle.request.files.getunicode('googlereaderfile')
        db.start()
        db.db.init_schema()
        log.info('Importing feeds from Google Reader takeout file "{}"'.format(upload.filename))
        with TemporaryDirectory() as tmpdirname:
            upload.save(tmpdirname)
            ok = import_from_googlereader(os.path.join(tmpdirname, upload.filename))
        if ok:
            update_feeds(db.get_feeds(False))
            bottle.redirect('/')
        else:
            log.error('Error importing from Google Reader takeout file "{}"'.format(upload.filename))
            db.destroy()
            bottle.abort(400, 'ERROR importing from Google Reader\n\nAre you sure "%s" is a valid Google Reader takeout file?' % upload.filename)
    else:
        bottle.abort(400, 'Error, wrong params in request')

@app.post('/import_opml')
def web_import_opml():
    upload = bottle.request.files.getunicode('opmlfile')
    do_import_opml(upload, from_wizard=False);

def do_import_opml(upload, from_wizard=False):
    log.info('Importing feeds from OPML file "{}"'.format(upload.filename))
    ok = import_opml(upload.file.read())
    if ok:
        update_feeds(db.get_feeds(False))
        bottle.redirect('/' if from_wizard else '/summary/group/-1')
    else:
        log.error('Error importing OPML file "{}"'.format(upload.filename))
        if from_wizard:
            db.destroy()
        bottle.abort(400, 'ERROR importing OPML file\n\nAre you sure "%s" is a valid OPML file?' % upload.filename)

@app.post('/export')
def web_export():
    val = bottle.request.forms.get('export')
    if val == 'opml':
        opmlfile = os.path.join(BASEPATH, 'data', 'mynewspaper.opml')
        with open(opmlfile, 'w') as f:
            f.write(export_opml())
        return bottle.static_file(os.path.basename(opmlfile), root=os.path.dirname(opmlfile), download=opmlfile)
    elif val == 'db':
        db.vacuum()
        dbfile = db.DBFILE_fullpath
        return bottle.static_file(os.path.basename(dbfile), root=os.path.dirname(dbfile), download=dbfile)
    else:
        bottle.abort(400, 'Error, wrong params in request')
    bottle.redirect('/')

@app.post('/clean/<which>')
def do_update_feeds(which='vacuum'):
    if which == 'vacuum':
        db.vacuum()
    elif which == 'cache':
        db.clear_old_articles_from_cache(nmonths=3)
    else:
        bottle.abort(400, 'Error, wrong params in request')


########################################################################
##### ajax
@app.route('/ajax/home')
def home():
    return bottle.template('home', dict(nfeeds=db.get_num_feeds_extra(), num_groups=db.get_num_groups(),
                                        lastupdate=db.get_lastupdate(), nums=db.get_nums()))

@app.route('/ajax/help_keys')
def help_keys():
    return bottle.template('help_keys', dict())

@app.route('/ajax/sidebar_load')
def sidebar():
    return bottle.template('sidebar', dict(gs=db.get_groups(), num_unread=db.get_nums()[UNREAD]))

@app.route('/ajax/summary_group/<gid:int>')
def get_summary_group(gid=-1):
    if (gid == -1):
        return bottle.template('summary_all_groups', dict(gs=db.get_groups(), nums=db.get_nums(),
                                                          num_feeds=db.get_num_feeds()))
    else:
        try:
            g = db.Group().get_by_id(gid)
        except db.DBGroupNotExistException:
            bottle.abort(404, 'Nothing here')
        return bottle.template('summary_group_feeds', dict(title=g.name, fs=g.get_feeds(only_enabled=False),
                                                           nums=g.get_nums(), gid=gid, groupname=g.name))

@app.route('/ajax/summary_feed/<fid:int>')
def get_summary_feed(fid):
    try:
        f = db.Feed().get_by_id(fid)
    except db.DBFeedNotExistException:
        bottle.abort(404, 'Nothing here')
    groupname = 'Archive' if f.fid == 0 else db.Group().get_by_id(f.gid).name # 'Archive'
    lastupdate = dbtime2dt_local(f.lastupdate, short=False)
    return bottle.template('summary_feed', dict(f=f, groupname=groupname, feedstate=FEED_STATES[f.state],
                                                lastupdate=lastupdate))

@app.post('/ajax/sort_items')
def sort_items():
    if not 'order' in bottle.request.params.keys() or not 'gid' in bottle.request.params.keys():
        bottle.abort(400, 'Error sorting')
    try:
        gid = int(bottle.request.params.get('gid'))
        order = bottle.request.params.get('order')
        order = map(int, order.split(','))
        if gid == -1:
            db.sort_groups(order)
        else:
            db.Group().get_by_id(gid).sort_feeds(order)
    except:
        bottle.abort(400, 'Error sorting')

@app.post('/ajax/group_new')
def group_new():
    if not 'groupname' in bottle.request.params.keys():
        bottle.abort(400, 'Error adding new group')
    try:
        groupname = bottle.request.params.getunicode('groupname').strip()
        db.group_new(groupname)
    except:
        bottle.abort(400, 'Error adding new group')

@app.post('/ajax/group_edit')
def group_edit():
    if not 'gid' in bottle.request.params.keys() or not 'groupname' in bottle.request.params.keys():
        bottle.abort(400, 'Error renaming group')
    try:
        gid = int(bottle.request.params.get('gid'))
        groupname = bottle.request.params.getunicode('groupname').strip()
        if db.check_groupname_exists(groupname):
            return dict(errmsg='name already exists')
        else:
            db.Group().get_by_id(gid).update_fields({'name': groupname})
    except:
        bottle.abort(400, 'Error renaming group')

@app.post('/ajax/group_delete')
def group_delete():
    if not 'gid' in bottle.request.params.keys() or not 'move_arts' in bottle.request.params.keys():
        bottle.abort(400, 'Error deleting group')
    try:
        gid = int(bottle.request.params.get('gid'))
        move_arts = bool(int(bottle.request.params.get('move_arts')))
        db.group_delete(gid, move_arts)
    except:
        bottle.abort(400, 'Error deleting group')

@app.post('/ajax/feed_new')
def feed_new():
    if not 'feedurl' in bottle.request.params.keys() or not 'gid' in bottle.request.params.keys():
        bottle.abort(400, 'Error adding feed')
    try:
        url = bottle.request.params.get('feedurl').strip()
        gid = int(bottle.request.params.get('gid'))
        if gid == -1:
            gid = 0 # 'Uncategorized'
        f = feed_add(url, gid)
        return dict(errmsg='\nNo feed found under this URL') if f is None else dict(fid=f.fid)
    except:
        bottle.abort(400, 'Error adding feed')

@app.route('/ajax/get_feed_edit_info/<fid:int>')
def get_feed_edit_info(fid):
    try:
        f = db.Feed().get_by_id(fid)
    except db.DBFeedNotExistException:
        bottle.abort(404, 'Nothing here')
    state = 0 if f.state==FEED_DISABLED else 1
    gs = [dict(gid=g.gid, name=g.name) for g in db.get_groups()]
    return dict(feedname=f.name, url=f.url, link=f.link, gid=f.gid, state=state, groups=gs)

@app.post('/ajax/feed_edit')
def feed_edit():
    if not 'fid' in bottle.request.params.keys() or not 'feedname' in bottle.request.params.keys() or \
       not 'url' in bottle.request.params.keys() or not 'link' in bottle.request.params.keys() or \
       not 'gid' in bottle.request.params.keys() or not 'state' in bottle.request.params.keys():
        bottle.abort(400, 'Error editing feed')
    try:
        fid = int(bottle.request.params.get('fid'))
        feedname = bottle.request.params.getunicode('feedname').strip()
        url = bottle.request.params.get('url').strip()
        link = bottle.request.params.get('link').strip()
        gid = int(bottle.request.params.get('gid'))
        state = bool(int(bottle.request.params.get('state')))
        if db.check_feedname_exists(feedname, fid):
            return dict(errmsg='\nName already exists')
        else:
            f = db.Feed().get_by_id(fid)
            oldgid = f.gid
            f.update_fields(dict(name=feedname, url=url, link=link, gid=gid, sort_idx=10000,
                                 state=FEED_ENABLED if state else FEED_DISABLED))
            db.Group().get_by_id(gid).resort_feeds()
            if gid != oldgid:
                db.Group().get_by_id(oldgid).resort_feeds()
            if state:
                update_feeds([f])
    except:
        bottle.abort(400, 'Error editing feed')

@app.post('/ajax/feed_delete')
def feed_delete():
    if not 'fid' in bottle.request.params.keys() or not 'move_arts' in bottle.request.params.keys():
        bottle.abort(400, 'Error deleting feed')
    try:
        fid = int(bottle.request.params.get('fid'))
        move_arts = bool(int(bottle.request.params.get('move_arts')))
        db.feed_delete(fid, move_arts)
    except:
        raise
        bottle.abort(400, 'Error deleting feed')

@app.route('/ajax/articles/<w:re:[agf]>/<i:int>/<st:int>/<sorttype:int>/<offset:int>/<limit:int>')
def get_articles(w='a', i=0, st=UNREAD, sorttype=SORT_DATENEW_FEED, offset=0, limit=50):
    if not 0 <= st < MAX_STATE:
        bottle.abort(404, 'Nothing here')
    if w == 'a':
        num_query, num_total, arts = db.get_articles(st, sorttype, offset, limit)
        title = '<a onclick="summary_group(-1);">All items</a>'
    elif w == 'g':
        try:
            g = db.Group().get_by_id(i)
        except db.DBGroupNotExistException:
            bottle.abort(404, 'Nothing here')
        num_query, num_total, arts = g.get_articles(st, sorttype, offset, limit)
        title = 'Folder:&nbsp;&nbsp;<a onclick="summary_group({0.gid});">{0.name}</a>'.format(g)
    elif w == 'f':
        try:
            f = db.Feed().get_by_id(i)
        except db.DBFeedNotExistException:
            bottle.abort(404, 'Nothing here')
        num_query, num_total, arts = f.get_articles(st, sorttype, offset, limit)
        if i == 0: # Archive
            title = 'Feed:&nbsp;&nbsp;<a onclick="summary_feed({0.fid});">{0.name}</a>'.format(f)
        else:
            title = 'Feed:&nbsp;&nbsp;<a onclick="summary_feed({0.fid});">{0.name}</a>&nbsp;&nbsp;&nbsp;&nbsp;<small>in folder:&nbsp;&nbsp;<a onclick="summary_group({1.gid});">{1.name}</a></small>'.format(f, db.Group().get_by_id(f.gid))
    else:
        bottle.abort(404, 'Nothing here')
    kwargs = dict(arts=arts, icons=ART_STATE_ICONS, state=st)
    html = bottle.template('articles', kwargs)
    return dict(title=title, num_query=num_query, num_total=num_total, arts=html)

@app.post('/ajax/process_articles')
def process_articles():
    if not 'arts' in bottle.request.params.keys():
        bottle.abort(500, 'Error processing articles')
    arts = bottle.request.params.get('arts')
    if arts:
        try:
            db.process_articles(arts)
        except db.DBMalformedArticleProcessingValue:
            bottle.abort(500, 'Error processing articles')

@app.post('/ajax/update_feeds/<gid:int>')
def do_update_feeds(gid=-1):
    if gid == -1:
        update_feeds(db.get_feeds(sort=False, only_enabled=True))
    else:
        try:
            g = db.Group().get_by_id(gid)
        except db.DBGroupNotExistException:
            bottle.abort(404, 'Nothing here')
        update_feeds(g.get_feeds(sort=False, only_enabled=True))

@app.post('/ajax/update_feed/<fid:int>')
def do_update_feed(fid=0):
    try:
        f = db.Feed().get_by_id(fid)
    except db.DBFeedNotExistException:
        bottle.abort(404, 'Nothing here')
    update_feeds([f])


########################################################################
##### mobile
@app.route('/m')
def mobile():
    return bottle.template('mob_base', dict())

@app.route('/ajax/mob_load_summary/<st:int>')
def mobile_summary(st=UNREAD):
    return bottle.template('mob_summary', dict(st=st, gs=db.get_groups(), num=db.get_nums()[st]))

# @app.route('/ajax/mob_load_articles/<w:re:[agf]>/<i:int>/<st:int>/<sorttype:int>/<offset:int>/<limit:int>')
@app.route('/ajax/mob_load_articles/<w:re:[agf]>/<i:int>/<st:int>/<loadall:int>')
def mobile_articles(w='a', i=0, st=UNREAD, loadall=0, sorttype=SORT_DATENEW_FEED, offset=0, limit=50):
    if loadall == 1:
        limit = 0
    if not 0 <= st < MAX_STATE:
        bottle.abort(404, 'Nothing here')
    if w == 'a':
        num_query, num_total, arts = db.get_articles(st, sorttype, offset, limit)
        title = 'All items'
    elif w == 'g':
        try:
            g = db.Group().get_by_id(i)
        except db.DBGroupNotExistException:
            bottle.abort(404, 'Nothing here')
        num_query, num_total, arts = g.get_articles(st, sorttype, offset, limit)
        title = 'Folder: {}'.format(g.name)
    elif w == 'f':
        try:
            f = db.Feed().get_by_id(i)
        except db.DBFeedNotExistException:
            bottle.abort(404, 'Nothing here')
        num_query, num_total, arts = f.get_articles(st, sorttype, offset, limit)
        title = 'Feed: {}'.format(f.name)
    else:
        bottle.abort(404, 'Nothing here')
    if num_query == 0:
        bottle.redirect('/m')
    else:
        return bottle.template('mob_articles', dict(title=title, num_query=num_query, num_total=num_total,
                                                    arts=arts, icons=ART_STATE_ICONS, state=st))

@app.route('/ajax/mob_load_article/<aid:int>')
def mobile_article(aid=0):
    try:
        a = db.Article().get_by_id(aid)
    except db.DBArticleNotExistException:
        bottle.abort(404, 'Nothing here')
    f = db.Feed().get_by_id(a.fid)
    a.summary = extract_summary(a.contents)
    a.feedname = f.name
    a.timestamp2 = dbtime2dt_local(a.timestamp, short=False)
    return bottle.template('mob_article', dict(art=a))


########################################################################
##### main
def run_standalone():
    log.info('Standalone Server started')
    bottle.run(app, port=8887) #, debug=True, reloader=True)

def run_fcgi():
    log.info('FCGI Server started')
    bottle.run(app, server='flup', options={'bindAddress': '/run/lighttpd/mynewspaper.sock'})


########################################################################
