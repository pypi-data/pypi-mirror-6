# -*- coding: utf-8 -*-

import re
import datetime
import urllib.request
from urllib.parse import urlsplit, urljoin
from html.parser import HTMLParser

from misc.dateutil.parser import parse as dateutil_parse
from misc.dateutil.parser import tz

from common import TIMEOUT_WEB, DEFAULT_FAVICON, log


########################################################################
USER_AGENT = 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'
RSS_APPS = 'application/atom+xml,application/rdf+xml,application/rss+xml,application/x-netcdf,application/xml;q=0.9,text/xml;q=0.2,*/*;q=0.1'.split(',')
REGEX_LINK = re.compile('<link .*?>', re.MULTILINE | re.DOTALL)


########################################################################
##### web
# urllib.request.urlopen() returns byte but we want unicode, so we need to decode
# more info: http://bugs.python.org/issue4733
def urlopen_read_str(url, fallback='utf-8', force=False):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    response = urllib.request.urlopen(req, timeout=TIMEOUT_WEB)
    header = response.headers
    if force:
        charset = fallback
    else:
        resp_charset = header.get_charsets()[0] or header.get_charset()
        charset = resp_charset if resp_charset else fallback
    content = response.read()
    return str(content, encoding=charset)

def url_download_as(url, filename):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    result = urllib.request.urlopen(req, timeout=TIMEOUT_WEB).read()
    if result:
        open(filename, 'wb').write(result)

def _url_replace(url, abspath):
    s = urlsplit(url)
    base_url = s.scheme + '://' + s.netloc + (':'+str(s.port) if s.port else '')
    return urljoin(base_url, abspath)

def _check_url_exists(url):
    try:
        response = urllib.request.urlopen(url, timeout=TIMEOUT_WEB)
    except:
        return False
    return response.getcode() == 200

def _get_attr_in_tag(l, attr):
    m = re.search(attr + '\s*=\s*"(.*?)"', l, re.MULTILINE | re.DOTALL)
    if m is None:
        return None
    return m.group(1)

def get_feed_in_web(link):
    if not link:
        return
    try:
        buf = urlopen_read_str(link)
    except:
        return
    for l in REGEX_LINK.findall(buf):
        if _get_attr_in_tag(l, 'rel') == 'alternate':
            typ = _get_attr_in_tag(l, 'type')
            if typ in RSS_APPS:
                href = _get_attr_in_tag(l, 'href')
                if not href:
                    continue
                if not href.startswith('http'): # relative
                    href = _url_replace(link, href)
                return href
    return

def get_feed_icon(feed):
    if not feed.link:
        log.info('Feed icon ' + str(feed) +  ', default')
        return DEFAULT_FAVICON
    try:
        buf = urlopen_read_str(feed.link)
    except: # urllib.error.HTTPError, UnicodeDecodeError
        pass
    else:
        for l in REGEX_LINK.findall(buf):
            rel = _get_attr_in_tag(l, 'rel')
            if not rel:
                continue
            if rel.lower() in ('shortcut icon', 'icon'):
                icon_url = _get_attr_in_tag(l, 'href')
                if not icon_url:
                    continue
                if not icon_url.startswith('http'): # relative
                    icon_url = _url_replace(feed.link, icon_url)
                if _check_url_exists(icon_url):
                    log.info('Feed icon ' + str(feed) +  ', from web: ' + icon_url)
                    return icon_url
    icon_url = _url_replace(feed.link, 'favicon.ico')
    if _check_url_exists(icon_url):
        log.info('Feed icon ' + str(feed) +  ', from fav: ' + icon_url)
        return icon_url
    else:
        log.info('Feed icon ' + str(feed) +  ', default')
        return DEFAULT_FAVICON


########################################################################
##### HTML
class MyHTMLParser(HTMLParser):
    FORBIDDEN_TAGS = ('iframe', 'link', 'meta', 'script', 'style')
    SINGLE_TAGS = ('area', 'base', 'br', 'col', 'command', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param')

    def __init__(self, notags=False):
        HTMLParser.__init__(self, notags)
        self._text = ''
        self._notags = notags
        self._strip_tag = False
    def handle_starttag(self, tag, attrs):
        self._strip_tag = tag in MyHTMLParser.FORBIDDEN_TAGS
        if not (self._strip_tag or self._notags):
            ch = '/' if tag in MyHTMLParser.SINGLE_TAGS else ''
            if len(attrs) == 0:
                self._text += '<{}{}>'.format(tag, ch)
            else:
                self._text += '<{} {}{}>'.format(tag, ' '.join(['%s="%s"' % (k, v) for k, v in attrs if not k.startswith('on')]), ch)
    def handle_endtag(self, tag):
        if not (self._strip_tag or self._notags):
            if not tag in MyHTMLParser.SINGLE_TAGS:
                self._text += '</{}>'.format(tag)
        self._strip_tag = False
    def handle_data(self, data):
        if not self._strip_tag:
            self._text += data
    def handle_entityref(self, name):
        if not self._strip_tag:
            self._text += self.unescape('&{};'.format(name))
    def handle_comment(self, data):
        pass
    def get_text(self):
        return self._text

def extract_summary(text):
    return ' '.join(re.sub('<[^<]+?>', '', text)[:250].split('\n'))

def remove_dirty_tags(text):
    parser = MyHTMLParser()
    parser.feed(text)
    return parser.get_text()


########################################################################
##### date & time
def time2dt_utc(timestamp):
    utcnow = datetime.datetime.utcnow().replace(tzinfo=tz.tzutc())
    try:
        dt = dateutil_parse(timestamp, fuzzy=True)
    except ValueError: # f.e. when e.updated is not English
        return utcnow
    try:
        dt = dt.astimezone(tz=tz.tzutc()) # str -> dt -> dt_utc
    except ValueError: # because of dt without timezone info
        dt = dt.replace(tzinfo=tz.tzutc())
    return utcnow if dt > utcnow else dt

def dbtime2dt_local(timestamp, short=True):
    dt = dateutil_parse(timestamp, fuzzy=True)
    try:
        dt = dt.astimezone(tz=None) # str -> dt -> dt_local
    except ValueError: # because of dt without timezone info
        dt = dt
    if short:
        if dt.date() == datetime.date.today():
            return 'Today, ' + dt.strftime('%H:%M')
        elif dt.date() == datetime.date.today()-datetime.timedelta(days=1):
            return 'Yesterday, ' + dt.strftime('%H:%M')
        else:
            return dt.strftime('%d %b %Y')
    else:
        return dt.strftime('%A %d %B %Y, %H:%M')

def dt2local(dt):
    try:
        return dt.astimezone(tz=tz.tzlocal())
    except ValueError: # because of dt without timezone info
        dt = dt.replace(tzinfo=tz.tzutc())
        return dt.astimezone(tz=tz.tzlocal())


########################################################################
